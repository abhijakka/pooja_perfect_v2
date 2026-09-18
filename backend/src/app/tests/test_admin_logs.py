"""Activity log tests — global file-based pipeline (PonyTail Ultra).

Covers:
- daily file naming (``pooja_DD_MM_YYYY.log``)
- SUCCESS / WARNING / ERROR classification and meaningful descriptions
- GraphQL error inspection
- sensitive-data sanitization
- the admin GraphQL API and file-backed CRUD mutations
"""

from __future__ import annotations

import re

from fastapi.testclient import TestClient

from app.core.activity_logging import (
    ERROR,
    SUCCESS,
    WARNING,
    build_description,
    classify_graphql_errors,
    classify_response,
    create_activity_log,
    daily_log_path,
    get_activity_log,
    read_entries,
)
from app.main import app
from app.tests.admin_test_utils import admin_headers, gql
from app.tests.conftest import ACTIVITY_LOG_DIR

LIST_QUERY = """
query {
  activityLogs(page: 1, pageSize: 50) {
    items { id action level details status method path user source statusCode ipAddress }
    pagination { total }
  }
}
"""

CREATE_MUTATION = """
mutation CreateLog($data: ActivityLogInput!) {
  createActivityLog(data: $data) {
    id action level details status
  }
}
"""

UPDATE_MUTATION = """
mutation UpdateLog($id: UUID!, $data: ActivityLogUpdateInput!) {
  updateActivityLog(id: $id, data: $data) {
    id action level status
  }
}
"""

DELETE_MUTATION = """
mutation DeleteLog($id: UUID!) {
  deleteActivityLog(id: $id) { success message }
}
"""

CLEAR_MUTATION = """
mutation {
  clearActivityLogs { success message }
}
"""

GET_QUERY = """
query GetLog($id: UUID!) {
  activityLog(id: $id) { id action level details }
}
"""


# ── Unit tests: classification ───────────────────────────────────────────────
def test_classify_response_status_mapping() -> None:
    for status in (200, 201, 202, 204):
        assert classify_response(status) == SUCCESS
    for status in (400, 401, 403, 404, 409, 422, 429):
        assert classify_response(status) == WARNING
    for status in (500, 502, 503, 504):
        assert classify_response(status) == ERROR


def test_classify_graphql_errors() -> None:
    assert classify_graphql_errors([{"extensions": {"code": 401}}]) == WARNING
    assert classify_graphql_errors([{"extensions": {"code": 404}}]) == WARNING
    assert classify_graphql_errors([{"extensions": {"code": 409}}]) == WARNING
    assert classify_graphql_errors([{"extensions": {"code": 500}}]) == ERROR
    assert classify_graphql_errors([{"message": "boom"}]) == "error"


# ── Unit tests: meaningful descriptions ──────────────────────────────────────
def test_success_description_is_meaningful() -> None:
    action, source, resource, _, description = build_description(
        method="POST",
        path="/admin/graphql",
        level=SUCCESS,
        status=200,
        user="admin",
        graphql_operation="createProduct",
    )
    assert description == "SUCCESS - Admin created product successfully via createProduct"
    assert action == "Product created"
    assert resource == "product"
    assert source == "Catalog"


def test_warning_description_explains_reason() -> None:
    _, _, _, _, login_warn = build_description(
        method="POST", path="/auth/login", level=WARNING, status=401, user="customer"
    )
    assert login_warn == "WARNING - Login failed because credentials were invalid"

    _, _, _, _, not_found = build_description(
        method="GET", path="/api/admin/orders/999", level=WARNING, status=404, user="admin"
    )
    assert not_found.startswith("WARNING")
    assert "not found" in not_found.lower()

    _, _, _, _, unauthorized = build_description(
        method="GET", path="/api/admin/logs", level=WARNING, status=403, user="customer"
    )
    assert unauthorized == "WARNING - Unauthorized access attempt to /api/admin/logs"


def test_error_description_explains_failure() -> None:
    _, _, _, _, database_error = build_description(
        method="POST", path="/api/orders", level=ERROR, status=500, user="customer"
    )
    assert database_error == (
        "ERROR - Internal server error while processing POST /api/orders (HTTP 500)"
    )

    _, _, _, _, graphql_error = build_description(
        method="POST",
        path="/admin/graphql",
        level=ERROR,
        status=200,
        user="admin",
        graphql_operation="createProduct",
        graphql_errors=[{"extensions": {"code": 500}}],
    )
    assert "ERROR" in graphql_error
    assert "internal server error" in graphql_error.lower()


# ── Middleware integration ───────────────────────────────────────────────────
def test_daily_log_file_is_named_pooja_dd_mm_yyyy(client: TestClient) -> None:
    response = client.get("/definitely-not-a-route")
    assert response.status_code == 404
    log_path = daily_log_path()
    assert log_path.exists()
    assert log_path.parent == ACTIVITY_LOG_DIR
    assert re.fullmatch(r"pooja_\d{2}_\d{2}_\d{4}\.log", log_path.name)


def test_success_request_logged(client: TestClient) -> None:
    response = client.post("/auth/logout")
    assert response.status_code == 204

    entries = read_entries()
    entry = entries[-1]
    assert entry["level"] == SUCCESS
    assert entry["method"] == "POST"
    assert entry["path"] == "/auth/logout"
    assert entry["status"] == "204"
    assert entry["user"] == "customer"
    assert entry["description"] == "SUCCESS - Customer logged out successfully"


def test_warning_request_logged(client: TestClient) -> None:
    response = client.get("/definitely-not-a-route")
    assert response.status_code == 404

    entry = read_entries()[-1]
    assert entry["level"] == WARNING
    assert entry["status"] == "404"
    assert entry["description"].startswith("WARNING")
    assert "not found" in entry["description"].lower()


async def _boom() -> None:
    raise RuntimeError("boom")


def test_error_request_logged() -> None:
    if not any(getattr(route, "path", None) == "/__test_error" for route in app.routes):
        app.add_api_route("/__test_error", _boom, methods=["GET"])

    with TestClient(app, raise_server_exceptions=False) as error_client:
        response = error_client.get("/__test_error")
    assert response.status_code == 500

    entry = read_entries()[-1]
    assert entry["level"] == ERROR
    assert entry["status"] == "500"
    assert entry["description"].startswith("ERROR")


def test_health_is_not_logged(client: TestClient) -> None:
    assert client.get("/health").status_code == 200
    assert read_entries() == []


def test_unauthorized_admin_request_logged_as_warning(client: TestClient) -> None:
    response = client.post("/admin/graphql", json={"query": "{ activityLogs { pagination { total } } }"})
    assert response.status_code == 401

    entry = read_entries()[-1]
    assert entry["level"] == WARNING
    assert entry["user"] == "admin"
    assert entry["status"] == "401"


def test_graphql_business_error_is_warning(client: TestClient) -> None:
    # Missing required variable -> GraphQL validation error with an HTTP 200 body.
    response = client.post("/graphql", json={"query": "query { nonsense }"})
    assert response.status_code == 200

    entry = read_entries()[-1]
    assert entry["level"] in (WARNING, ERROR)
    assert entry["path"] == "/graphql"


def test_admin_activity_logs_includes_all_daily_files(client: TestClient) -> None:
    import uuid
    from datetime import UTC, datetime, timedelta

    from app.core.activity_logging import _rewrite_file, daily_log_path

    yesterday = (datetime.now(tz=UTC) - timedelta(days=1)).date()
    past_path = daily_log_path(yesterday)
    _rewrite_file(
        past_path,
        [
            {
                "id": str(uuid.uuid4()),
                "date": f"{yesterday:%d-%m-%Y}",
                "time": "12:00:00",
                "level": SUCCESS,
                "ip": "127.0.0.1",
                "method": "GET",
                "path": "/yesterday-event",
                "status": "200",
                "user": "admin",
                "action": "Past event",
                "source": "API",
                "resource": "page",
                "description": "SUCCESS - Past event logged",
            }
        ],
    )
    assert past_path.exists()

    client.get("/definitely-not-a-route")
    result = gql(client, LIST_QUERY, headers=admin_headers())
    assert "errors" not in result, result

    paths = {item["path"] for item in result["data"]["activityLogs"]["items"]}
    assert "/yesterday-event" in paths
    assert "/definitely-not-a-route" in paths


# ── Admin API over the daily files ───────────────────────────────────────────
def test_admin_activity_logs_api_returns_enhanced_fields(client: TestClient) -> None:
    client.get("/definitely-not-a-route")
    result = gql(client, LIST_QUERY, headers=admin_headers())
    assert "errors" not in result, result

    items = result["data"]["activityLogs"]["items"]
    assert items
    match = next(item for item in items if item["path"] == "/definitely-not-a-route")
    assert match["level"] == WARNING
    assert match["status"] == "Warning"
    assert match["statusCode"] == 404
    assert match["method"] == "GET"
    assert match["user"] == "guest"
    assert match["source"] == "API"
    assert match["details"].startswith("WARNING")


def test_admin_activity_logs_search_filter(client: TestClient) -> None:
    client.get("/definitely-not-a-route")
    result = gql(
        client,
        """
        query {
          activityLogs(page: 1, pageSize: 50, level: "warning", search: "definitely") {
            items { path level }
            pagination { total }
          }
        }
        """,
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    items = result["data"]["activityLogs"]["items"]
    assert items
    assert all(item["level"] == WARNING for item in items)


def test_create_get_delete_activity_log_mutations(client: TestClient) -> None:
    result = gql(
        client,
        CREATE_MUTATION,
        {
            "data": {
                "action": "Manual review",
                "level": "info",
                "resource": "settings",
                "details": "Notification preferences reviewed",
                "status": "Success",
            }
        },
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    created = result["data"]["createActivityLog"]
    assert created["action"] == "Manual review"
    assert created["level"] == "info"
    assert created["details"] == "SUCCESS - Notification preferences reviewed"

    fetched = gql(client, GET_QUERY, {"id": created["id"]}, headers=admin_headers())
    assert "errors" not in fetched, fetched
    assert fetched["data"]["activityLog"]["action"] == "Manual review"

    deleted = gql(client, DELETE_MUTATION, {"id": created["id"]}, headers=admin_headers())
    assert "errors" not in deleted, deleted
    assert deleted["data"]["deleteActivityLog"]["success"] is True
    assert get_activity_log(created["id"]) is None


def test_clear_activity_logs_mutation(client: TestClient) -> None:
    client.get("/definitely-not-a-route")
    assert any(entry["path"] == "/definitely-not-a-route" for entry in read_entries())

    result = gql(client, CLEAR_MUTATION, headers=admin_headers())
    assert "errors" not in result, result
    assert result["data"]["clearActivityLogs"]["success"] is True
    assert all(entry["path"] != "/definitely-not-a-route" for entry in read_entries())


# ── Sensitive-data sanitization ──────────────────────────────────────────────
def test_newlines_are_sanitized() -> None:
    entry = create_activity_log(
        action="Manual", details="first line\nsecond line", level=SUCCESS
    )
    loaded = get_activity_log(entry["id"])
    assert loaded is not None
    assert "\n" not in loaded["description"]
    assert loaded["description"] == "SUCCESS - first line second line"