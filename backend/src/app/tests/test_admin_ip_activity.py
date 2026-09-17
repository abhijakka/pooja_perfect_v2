"""Admin IP activity GraphQL tests — activity and policies."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.enums import IPPolicyStatus, UserRole
from app.models.ip_activity import IPActivity, IPPolicy
from app.models.user import User
from app.tests.admin_test_utils import admin_headers, gql
from app.tests.conftest import TestingSessionLocal

ACTIVITY_QUERY = """
query {
  ipActivity(page: 1, pageSize: 20) {
    items {
      id ipAddress action
      browser browserVersion os device deviceType path screen isMobile
    }
    pagination { total }
  }
}
"""

POLICIES_QUERY = """
query {
  ipPolicies {
    id ipAddress status
  }
}
"""

CREATE_POLICY_MUTATION = """
mutation($ipAddress: String!, $status: String!) {
  createIpPolicy(ipAddress: $ipAddress, status: $status) {
    id ipAddress status
  }
}
"""


def test_list_ip_activity(client: TestClient) -> None:
    session: Session = TestingSessionLocal()
    try:
        customer = User(
            first_name="IP",
            last_name="User",
            email="ip@example.com",
            password_hash="x",
            role_name=UserRole.CUSTOMER,
        )
        session.add(customer)
        session.flush()
        activity = IPActivity(
            user_id=customer.id,
            ip_address="203.0.113.5",
            action="login",
            metadata_json={
                "browser": "Chrome",
                "browser_version": "120.0",
                "os": "Windows 10",
                "device": "Windows PC",
                "device_type": "desktop",
                "path": "/login",
                "screen": "1920x1080",
                "is_mobile": False,
            },
        )
        session.add(activity)
        session.commit()
    finally:
        session.close()

    result = gql(client, ACTIVITY_QUERY, headers=admin_headers())
    assert "errors" not in result, result
    assert result["data"]["ipActivity"]["pagination"]["total"] == 1
    item = result["data"]["ipActivity"]["items"][0]
    assert item["ipAddress"] == "203.0.113.5"
    assert item["browser"] == "Chrome"
    assert item["browserVersion"] == "120.0"
    assert item["os"] == "Windows 10"
    assert item["device"] == "Windows PC"
    assert item["deviceType"] == "desktop"
    assert item["path"] == "/login"
    assert item["screen"] == "1920x1080"
    assert item["isMobile"] is False


def test_create_ip_policy(client: TestClient) -> None:
    result = gql(
        client,
        CREATE_POLICY_MUTATION,
        variables={"ipAddress": "203.0.113.9", "status": "blocked"},
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    assert result["data"]["createIpPolicy"]["status"] == "blocked"


def test_list_ip_policies(client: TestClient) -> None:
    session: Session = TestingSessionLocal()
    try:
        policy = IPPolicy(
            ip_address="203.0.113.10",
            status=IPPolicyStatus.BLOCKED,
        )
        session.add(policy)
        session.commit()
    finally:
        session.close()

    result = gql(client, POLICIES_QUERY, headers=admin_headers())
    assert "errors" not in result, result
    assert len(result["data"]["ipPolicies"]) == 1