"""Public subscription GraphQL tests — plans, subscribe, update, cancel."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.enums import BillingCycle
from app.models.subscription_plan import SubscriptionPlan
from app.tests.admin_test_utils import customer_headers
from app.tests.conftest import TestingSessionLocal
from app.tests.public_test_utils import public_gql

PLANS_QUERY = """
query {
  subscriptionPlans { id name price billingCycle }
}
"""

SUBSCRIBE = """
mutation($planId: UUID!, $weekdays: [String!]) {
  subscribe(planId: $planId, weekdays: $weekdays) {
    id status price weekdays
  }
}
"""

MY_SUBS = """
query {
  mySubscriptions(page: 1, pageSize: 20) {
    items { id status }
    pagination { total }
  }
}
"""

CANCEL = """
mutation($id: UUID!) {
  cancelSubscription(id: $id) { id status }
}
"""


def _plan_id() -> str:
    session: Session = TestingSessionLocal()
    try:
        plan = SubscriptionPlan(
            name="Weekly Pooja",
            description="Weekly pooja essentials",
            price=500,
            currency="INR",
            billing_cycle=BillingCycle.WEEKLY,
            interval_count=1,
            is_active=True,
        )
        session.add(plan)
        session.commit()
        session.refresh(plan)
        return str(plan.id)
    finally:
        session.close()


def test_list_plans(client: TestClient) -> None:
    _plan_id()
    result = public_gql(client, PLANS_QUERY)
    assert "errors" not in result, result
    assert len(result["data"]["subscriptionPlans"]) == 1


def test_subscribe(client: TestClient) -> None:
    plan_id = _plan_id()
    headers = customer_headers()
    result = public_gql(
        client,
        SUBSCRIBE,
        variables={"planId": plan_id, "weekdays": ["MON", "WED"]},
        headers=headers,
    )
    assert "errors" not in result, result
    data = result["data"]["subscribe"]
    assert data["status"] == "active"
    assert data["weekdays"] == ["MON", "WED"]


def test_subscribe_requires_auth(client: TestClient) -> None:
    plan_id = _plan_id()
    result = public_gql(client, SUBSCRIBE, variables={"planId": plan_id})
    assert "errors" in result


def test_my_subscriptions(client: TestClient) -> None:
    plan_id = _plan_id()
    headers = customer_headers()
    public_gql(client, SUBSCRIBE, variables={"planId": plan_id}, headers=headers)
    result = public_gql(client, MY_SUBS, headers=headers)
    assert "errors" not in result, result
    assert result["data"]["mySubscriptions"]["pagination"]["total"] == 1


def test_cancel_subscription(client: TestClient) -> None:
    plan_id = _plan_id()
    headers = customer_headers()
    sub = public_gql(client, SUBSCRIBE, variables={"planId": plan_id}, headers=headers)
    sub_id = sub["data"]["subscribe"]["id"]
    result = public_gql(client, CANCEL, variables={"id": sub_id}, headers=headers)
    assert "errors" not in result, result
    assert result["data"]["cancelSubscription"]["status"] == "cancelled"