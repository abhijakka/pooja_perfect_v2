"""Admin customer GraphQL tests — list, detail, notes, status, create, update, delete."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.models.enums import UserRole
from app.tests.admin_test_utils import admin_headers, create_user, gql

LIST_QUERY = """
query {
  customers(page: 1, pageSize: 20) {
    items { id email firstName lastName status orderCount lifetimeValue adminNotes }
    pagination { total }
  }
}
"""

UPDATE_NOTES_MUTATION = """
mutation($id: UUID!, $notes: String) {
  updateCustomerNotes(id: $id, notes: $notes) {
    id adminNotes
  }
}
"""


def test_list_customers(client: TestClient) -> None:
    create_user(role=UserRole.CUSTOMER, email="cust@example.com")
    result = gql(client, LIST_QUERY, headers=admin_headers())
    assert "errors" not in result, result
    assert result["data"]["customers"]["pagination"]["total"] == 1
    item = result["data"]["customers"]["items"][0]
    assert item["orderCount"] == 0
    assert item["lifetimeValue"] == "0.00"
    assert item["adminNotes"] is None


def test_list_customers_returns_notes(client: TestClient) -> None:
    customer = create_user(role=UserRole.CUSTOMER, email="noted@example.com")
    gql(
        client,
        UPDATE_NOTES_MUTATION,
        variables={"id": str(customer.id), "notes": "Priority account"},
        headers=admin_headers(),
    )
    result = gql(client, LIST_QUERY, headers=admin_headers())
    assert "errors" not in result, result
    item = result["data"]["customers"]["items"][0]
    assert item["adminNotes"] == "Priority account"


def test_update_customer_notes(client: TestClient) -> None:
    customer = create_user(role=UserRole.CUSTOMER, email="cust2@example.com")
    result = gql(
        client,
        UPDATE_NOTES_MUTATION,
        variables={"id": str(customer.id), "notes": "VIP customer"},
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    assert result["data"]["updateCustomerNotes"]["adminNotes"] == "VIP customer"


# ── create ──────────────────────────────────────────────────────

CREATE_MUTATION = """
mutation($firstName: String!, $lastName: String!, $email: String!, $phone: String, $status: String) {
  createCustomer(firstName: $firstName, lastName: $lastName, email: $email, phone: $phone, status: $status) {
    id firstName lastName email phone status
  }
}
"""


def test_create_customer(client: TestClient) -> None:
    result = gql(
        client,
        CREATE_MUTATION,
        variables={
            "firstName": "Priya",
            "lastName": "Patel",
            "email": "priya@example.com",
            "phone": "+91 90000 00001",
            "status": "active",
        },
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    data = result["data"]["createCustomer"]
    assert data["firstName"] == "Priya"
    assert data["email"] == "priya@example.com"
    assert data["status"] == "active"


def test_create_customer_duplicate_email(client: TestClient) -> None:
    create_user(role=UserRole.CUSTOMER, email="dup@example.com")
    result = gql(
        client,
        CREATE_MUTATION,
        variables={
            "firstName": "Dup",
            "lastName": "User",
            "email": "dup@example.com",
            "status": "active",
        },
        headers=admin_headers(),
    )
    assert "errors" in result


# ── update ──────────────────────────────────────────────────────

UPDATE_MUTATION = """
mutation($id: UUID!, $firstName: String!, $lastName: String!, $email: String!, $phone: String) {
  updateCustomer(id: $id, firstName: $firstName, lastName: $lastName, email: $email, phone: $phone) {
    id firstName lastName email phone
  }
}
"""


def test_update_customer(client: TestClient) -> None:
    customer = create_user(role=UserRole.CUSTOMER, email="update@example.com")
    result = gql(
        client,
        UPDATE_MUTATION,
        variables={
            "id": str(customer.id),
            "firstName": "Updated",
            "lastName": "Name",
            "email": "updated@example.com",
            "phone": "+91 90000 00002",
        },
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    data = result["data"]["updateCustomer"]
    assert data["firstName"] == "Updated"
    assert data["email"] == "updated@example.com"


# ── delete ──────────────────────────────────────────────────────

DELETE_MUTATION = """
mutation($id: UUID!) {
  deleteCustomer(id: $id) { success message }
}
"""


def test_delete_customer(client: TestClient) -> None:
    customer = create_user(role=UserRole.CUSTOMER, email="delete@example.com")
    result = gql(
        client,
        DELETE_MUTATION,
        variables={"id": str(customer.id)},
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    assert result["data"]["deleteCustomer"]["success"] is True


def test_delete_nonexistent_customer(client: TestClient) -> None:
    import uuid
    result = gql(
        client,
        DELETE_MUTATION,
        variables={"id": str(uuid.uuid4())},
        headers=admin_headers(),
    )
    assert "errors" in result


# ── frontend contract ──────────────────────────────────────────────────

FRONTEND_LIST_QUERY = """
query Customers($page: Int, $pageSize: Int, $search: String, $status: String) {
  customers(page: $page, pageSize: $pageSize, search: $search, status: $status) {
    items { id firstName lastName email phone roleName status isEmailVerified createdAt updatedAt orderCount lifetimeValue adminNotes }
    pagination { page pageSize total totalPages hasNext hasPrevious }
  }
}
"""

FRONTEND_CREATE_MUTATION = """
mutation CreateCustomer($firstName: String!, $lastName: String!, $email: String!, $phone: String, $status: String) {
  createCustomer(firstName: $firstName, lastName: $lastName, email: $email, phone: $phone, status: $status) {
    id firstName lastName email phone roleName status isEmailVerified createdAt updatedAt orderCount lifetimeValue adminNotes
  }
}
"""

FRONTEND_UPDATE_MUTATION = """
mutation UpdateCustomer($id: UUID!, $firstName: String!, $lastName: String!, $email: String!, $phone: String) {
  updateCustomer(id: $id, firstName: $firstName, lastName: $lastName, email: $email, phone: $phone) {
    id firstName lastName email phone roleName status isEmailVerified createdAt updatedAt orderCount lifetimeValue adminNotes
  }
}
"""

FRONTEND_UPDATE_NOTES_MUTATION = """
mutation UpdateCustomerNotes($id: UUID!, $notes: String) {
  updateCustomerNotes(id: $id, notes: $notes) {
    id firstName lastName email phone roleName status isEmailVerified createdAt updatedAt orderCount lifetimeValue adminNotes
  }
}
"""

FRONTEND_SET_STATUS_MUTATION = """
mutation SetCustomerStatus($id: UUID!, $status: String!) {
  setCustomerStatus(id: $id, status: $status) {
    id firstName lastName email phone roleName status isEmailVerified createdAt updatedAt orderCount lifetimeValue adminNotes
  }
}
"""


def test_frontend_list_customer_contract(client: TestClient) -> None:
    create_user(role=UserRole.CUSTOMER, email="fe@example.com")
    result = gql(
        client,
        FRONTEND_LIST_QUERY,
        variables={"page": 1, "pageSize": 25},
        headers=admin_headers(),
    )
    assert "errors" not in result, result
    assert result["data"]["customers"]["pagination"]["total"] >= 1
    item = next(
        row for row in result["data"]["customers"]["items"] if row["email"] == "fe@example.com"
    )
    assert item["firstName"] == "Test"
    assert item["lastName"] == "User"
    assert item["status"] == "active"
    assert item["isEmailVerified"] is True
    assert item["orderCount"] == 0
    assert result["data"]["customers"]["pagination"]["hasNext"] is False
    assert result["data"]["customers"]["pagination"]["hasPrevious"] is False


def test_frontend_customer_mutation_contract(client: TestClient) -> None:
    created = gql(
        client,
        FRONTEND_CREATE_MUTATION,
        variables={
            "firstName": "Contract",
            "lastName": "User",
            "email": "contract@example.com",
            "phone": "+91 90000 00009",
            "status": "active",
        },
        headers=admin_headers(),
    )
    assert "errors" not in created, created
    new_id = created["data"]["createCustomer"]["id"]
    assert created["data"]["createCustomer"]["lifetimeValue"] == "0.00"

    updated = gql(
        client,
        FRONTEND_UPDATE_MUTATION,
        variables={
            "id": new_id,
            "firstName": "Contract2",
            "lastName": "User2",
            "email": "contract2@example.com",
            "phone": "+91 90000 00010",
        },
        headers=admin_headers(),
    )
    assert "errors" not in updated, updated
    assert updated["data"]["updateCustomer"]["firstName"] == "Contract2"

    noted = gql(
        client,
        FRONTEND_UPDATE_NOTES_MUTATION,
        variables={"id": new_id, "notes": "Frontend contract test"},
        headers=admin_headers(),
    )
    assert "errors" not in noted, noted
    assert noted["data"]["updateCustomerNotes"]["adminNotes"] == "Frontend contract test"

    blocked = gql(
        client,
        FRONTEND_SET_STATUS_MUTATION,
        variables={"id": new_id, "status": "suspended"},
        headers=admin_headers(),
    )
    assert "errors" not in blocked, blocked
    assert blocked["data"]["setCustomerStatus"]["status"] == "suspended"

    deleted = gql(
        client,
        DELETE_MUTATION,
        variables={"id": new_id},
        headers=admin_headers(),
    )
    assert "errors" not in deleted, deleted
    assert deleted["data"]["deleteCustomer"]["success"] is True