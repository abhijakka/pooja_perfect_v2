"""Admin report GraphQL tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.tests.admin_test_utils import admin_headers, gql

QUERY = """
query($reportType: String!) {
  report(reportType: $reportType) {
    name
    generatedAt
    data
  }
}
"""


def test_generate_sales_report(client: TestClient) -> None:
    today = datetime.now(UTC).date()
    result = gql(
        client,
        QUERY,
        variables={
            "reportType": "sales",
            "fromDate": str(today - timedelta(days=30)),
            "toDate": str(today),
        },
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    data = result["data"]["report"]
    assert data["name"] == "sales"
    assert isinstance(data["data"], list)


def test_generate_orders_report(client: TestClient) -> None:
    result = gql(
        client,
        QUERY,
        variables={"reportType": "orders"},
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    assert result["data"]["report"]["name"] == "orders"