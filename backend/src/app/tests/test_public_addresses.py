"""Public address GraphQL tests — CRUD, default, ownership."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.tests.admin_test_utils import customer_headers
from app.tests.public_test_utils import public_gql

ADDRESSES_QUERY = """
query {
  addresses { id recipientName city isDefault }
}
"""

CREATE = """
mutation($recipientName: String!, $phone: String!, $addressLine1: String!,
         $city: String!, $state: String!, $postalCode: String!,
         $country: String!, $isDefault: Boolean) {
  createAddress(recipientName: $recipientName, phone: $phone,
                addressLine1: $addressLine1, city: $city, state: $state,
                postalCode: $postalCode, country: $country,
                isDefault: $isDefault) {
    id recipientName city isDefault
  }
}
"""

UPDATE = """
mutation($id: UUID!, $city: String) {
  updateAddress(id: $id, city: $city) { id city }
}
"""

DELETE = """
mutation($id: UUID!) {
  deleteAddress(id: $id) { success }
}
"""

SET_DEFAULT = """
mutation($id: UUID!) {
  setDefaultAddress(id: $id) { id isDefault }
}
"""


def _create_vars(is_default: bool = False) -> dict:
    return {
        "recipientName": "Pooja Sharma",
        "phone": "9876543210",
        "addressLine1": "12 Temple Road",
        "city": "Varanasi",
        "state": "UP",
        "postalCode": "221001",
        "country": "India",
        "isDefault": is_default,
    }


def test_create_address(client: TestClient) -> None:
    headers = customer_headers()
    result = public_gql(client, CREATE, variables=_create_vars(), headers=headers)
    assert "errors" not in result, result
    assert result["data"]["createAddress"]["city"] == "Varanasi"


def test_list_addresses(client: TestClient) -> None:
    headers = customer_headers()
    public_gql(client, CREATE, variables=_create_vars(), headers=headers)
    result = public_gql(client, ADDRESSES_QUERY, headers=headers)
    assert "errors" not in result, result
    assert len(result["data"]["addresses"]) == 1


def test_update_address(client: TestClient) -> None:
    headers = customer_headers()
    created = public_gql(client, CREATE, variables=_create_vars(), headers=headers)
    addr_id = created["data"]["createAddress"]["id"]
    result = public_gql(
        client, UPDATE, variables={"id": addr_id, "city": "Delhi"}, headers=headers
    )
    assert "errors" not in result, result
    assert result["data"]["updateAddress"]["city"] == "Delhi"


def test_delete_address(client: TestClient) -> None:
    headers = customer_headers()
    created = public_gql(client, CREATE, variables=_create_vars(), headers=headers)
    addr_id = created["data"]["createAddress"]["id"]
    result = public_gql(client, DELETE, variables={"id": addr_id}, headers=headers)
    assert "errors" not in result, result
    assert result["data"]["deleteAddress"]["success"] is True


def test_set_default_address(client: TestClient) -> None:
    headers = customer_headers()
    created = public_gql(client, CREATE, variables=_create_vars(), headers=headers)
    addr_id = created["data"]["createAddress"]["id"]
    result = public_gql(client, SET_DEFAULT, variables={"id": addr_id}, headers=headers)
    assert "errors" not in result, result
    assert result["data"]["setDefaultAddress"]["isDefault"] is True


def test_cannot_update_other_users_address(client: TestClient) -> None:
    headers_a = customer_headers()
    created = public_gql(client, CREATE, variables=_create_vars(), headers=headers_a)
    addr_id = created["data"]["createAddress"]["id"]
    headers_b = customer_headers()
    result = public_gql(
        client, UPDATE, variables={"id": addr_id, "city": "Delhi"}, headers=headers_b
    )
    assert "errors" in result