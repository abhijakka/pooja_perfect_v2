"""Admin subscription GraphQL tests."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.enums import BillingCycle, SubscriptionStatus, UserRole
from app.models.subscription import Subscription
from app.models.subscription_plan import SubscriptionPlan
from app.models.user import User
from app.tests.admin_test_utils import admin_headers, gql
from app.tests.conftest import TestingSessionLocal

LIST_QUERY = """
query {
  subscriptions(page: 1, pageSize: 20) {
    items { id status }
    pagination { total }
  }
}
"""


def test_list_subscriptions(client: TestClient) -> None:
    session: Session = TestingSessionLocal()
    try:
        customer = User(
            first_name="Sub",
            last_name="User",
            email="sub@example.com",
            password_hash="x",
            role_name=UserRole.CUSTOMER,
        )
        session.add(customer)
        session.flush()
        plan = SubscriptionPlan(
            name="Weekly Pooja",
            price=Decimal("99.00"),
            billing_cycle=BillingCycle.WEEKLY,
        )
        session.add(plan)
        session.flush()
        subscription = Subscription(
            user_id=customer.id,
            plan_id=plan.id,
            status=SubscriptionStatus.ACTIVE,
            price=Decimal("99.00"),
            start_date=datetime.now(UTC),
        )
        session.add(subscription)
        session.commit()
    finally:
        session.close()

    result = gql(client, LIST_QUERY, headers=admin_headers())
    assert "errors" not in result, result
    assert result["data"]["subscriptions"]["pagination"]["total"] == 1