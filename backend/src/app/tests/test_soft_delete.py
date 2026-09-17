import uuid
from decimal import Decimal

from app.admin.repositories.category_repository import AdminCategoryRepository
from app.admin.repositories.product_repository import AdminProductRepository
from app.models.address import Address
from app.models.category import Category
from app.models.enums import ProductStatus
from app.models.product import Product
from app.public.repositories.address_repository import PublicAddressRepository


def _make_category(name: str = "Candles", slug: str = "candles") -> Category:
    return Category(
        name=name,
        slug=slug,
        description="test",
        display_order=1,
        is_active=True,
        is_featured=False,
    )


def _make_product(category: Category, slug: str = "rose-candle", sku: str = "SKU-1") -> Product:
    return Product(
        category_id=category.id,
        name="Rose Candle",
        slug=slug,
        sku=sku,
        price=Decimal("499.00"),
        stock=10,
        status=ProductStatus.ACTIVE,
        is_active=True,
        is_featured=False,
        metadata_json={},
    )


def test_category_soft_delete_hides_record_from_repository(db_session):
    category = _make_category()
    db_session.add(category)
    db_session.commit()

    repo = AdminCategoryRepository(db_session)
    category.soft_delete()
    db_session.commit()

    assert repo.get_by_id(category.id) is None
    assert repo.get_by_slug(category.slug) is None
    assert repo.list() == []


def test_product_soft_delete_hides_record_from_repository(db_session):
    category = _make_category()
    db_session.add(category)
    db_session.commit()

    product = _make_product(category)
    db_session.add(product)
    db_session.commit()

    repo = AdminProductRepository(db_session)
    product.soft_delete()
    db_session.commit()

    assert repo.get_by_id(product.id) is None
    assert repo.get_by_slug(product.slug) is None
    assert repo.get_by_sku(product.sku) is None
    products, total = repo.list()
    assert products == []
    assert total == 0


def test_address_soft_delete_hides_record_from_repository(db_session):
    user_id = uuid.UUID("11111111-1111-1111-1111-111111111111")
    address = Address(
        user_id=user_id,
        label="Home",
        recipient_name="Test User",
        phone="9876543210",
        address_line1="123 Main",
        city="Delhi",
        state="Delhi",
        postal_code="110001",
        country="IN",
        is_default=True,
    )
    db_session.add(address)
    db_session.commit()

    repo = PublicAddressRepository(db_session)
    address.soft_delete()
    db_session.commit()

    assert repo.get_by_id(address.id) is None
    assert repo.list_by_user(user_id) == []
