"""Admin catalog mutations — products and categories."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any

import strawberry
from strawberry.types import Info

from app.admin.api.graphql.types.category import CategoryType
from app.admin.api.graphql.types.common import MutationResult
from app.admin.api.graphql.types.product import ProductImageType, ProductType
from app.admin.context import AdminContext
from app.admin.services.category_service import CategoryService
from app.admin.services.product_service import ProductService
from app.models.enums import ProductStatus
from app.schemas.catalog.category import CategoryCreate, CategoryUpdate
from app.schemas.catalog.product import ProductCreate, ProductUpdate


@strawberry.input
class ProductInput:
    category_id: uuid.UUID
    name: str
    slug: str
    sku: str
    short_description: str | None = None
    description: str | None = None
    price: Decimal
    original_price: Decimal | None = None
    discount_price: Decimal | None = None
    stock: int = 0
    status: str = "active"
    is_featured: bool = False
    metadata_json: strawberry.scalars.JSON | None = None


@strawberry.input
class ProductUpdateInput:
    category_id: uuid.UUID | None = None
    name: str | None = None
    slug: str | None = None
    sku: str | None = None
    short_description: str | None = None
    description: str | None = None
    price: Decimal | None = None
    original_price: Decimal | None = None
    discount_price: Decimal | None = None
    stock: int | None = None
    status: str | None = None
    is_active: bool | None = None
    is_featured: bool | None = None
    metadata_json: strawberry.scalars.JSON | None = None


@strawberry.input
class CategoryInput:
    name: str
    slug: str
    description: str | None = None
    image_url: str | None = None
    emoji: str | None = None
    seo_title: str | None = None
    seo_description: str | None = None
    parent_id: uuid.UUID | None = None
    display_order: int = 0
    is_active: bool = True
    is_featured: bool = False


@strawberry.input
class CategoryUpdateInput:
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    image_url: str | None = None
    emoji: str | None = None
    seo_title: str | None = None
    seo_description: str | None = None
    parent_id: uuid.UUID | None = None
    display_order: int | None = None
    is_active: bool | None = None
    is_featured: bool | None = None


def _to_product_type(p: Any) -> ProductType:
    return ProductType(
        id=p.id,
        category_id=p.category_id,
        name=p.name,
        slug=p.slug,
        sku=p.sku,
        short_description=p.short_description,
        description=p.description,
        price=p.price,
        original_price=p.original_price,
        discount_price=p.discount_price,
        stock=p.stock,
        status=p.status,
        is_active=p.is_active,
        is_featured=p.is_featured,
        average_rating=p.average_rating,
        review_count=p.review_count,
        created_at=p.created_at,
        updated_at=p.updated_at,
        images=[
            ProductImageType(
                id=image.id,
                url=image.url,
                alt_text=image.alt_text,
                display_order=image.display_order,
                is_primary=image.is_primary,
            )
            for image in sorted(p.images or [], key=lambda item: item.display_order)
        ],
    )


def _to_category_type(c: Any) -> CategoryType:
    return CategoryType(
        id=c.id,
        parent_id=c.parent_id,
        name=c.name,
        slug=c.slug,
        description=c.description,
        image_url=c.image_url,
        emoji=c.emoji,
        seo_title=c.seo_title,
        seo_description=c.seo_description,
        display_order=c.display_order,
        is_active=c.is_active,
        is_featured=c.is_featured,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


# ── products ────────────────────────────────────────────────


def mutate_create_product(self, info: Info, data: ProductInput) -> ProductType:
    ctx: AdminContext = info.context
    svc = ProductService(ctx.db)
    payload = ProductCreate(
        category_id=data.category_id,
        name=data.name,
        slug=data.slug,
        sku=data.sku,
        short_description=data.short_description,
        description=data.description,
        price=data.price,
        original_price=data.original_price,
        discount_price=data.discount_price,
        stock=data.stock,
        status=ProductStatus(data.status),
        is_featured=data.is_featured,
        metadata_json=data.metadata_json or {},  # type: ignore[arg-type]
    )
    return _to_product_type(svc.create(payload))


def mutate_update_product(
    self, info: Info, id: uuid.UUID, data: ProductUpdateInput
) -> ProductType:
    ctx: AdminContext = info.context
    svc = ProductService(ctx.db)
    values: dict[str, Any] = {
        "category_id": data.category_id,
        "name": data.name,
        "slug": data.slug,
        "sku": data.sku,
        "short_description": data.short_description,
        "description": data.description,
        "price": data.price,
        "original_price": data.original_price,
        "discount_price": data.discount_price,
        "stock": data.stock,
        "status": ProductStatus(data.status) if data.status else None,
        "is_active": data.is_active,
        "is_featured": data.is_featured,
        "metadata_json": data.metadata_json,  # type: ignore[arg-type]
    }
    payload = ProductUpdate(**{k: v for k, v in values.items() if v is not None})
    return _to_product_type(svc.update(id, payload))


def mutate_delete_product(self, info: Info, id: uuid.UUID) -> MutationResult:
    ctx: AdminContext = info.context
    svc = ProductService(ctx.db)
    svc.delete(id)
    return MutationResult(success=True, message="Product deleted")


def mutate_change_product_status(
    self, info: Info, id: uuid.UUID, status: str
) -> ProductType:
    ctx: AdminContext = info.context
    svc = ProductService(ctx.db)
    return _to_product_type(svc.change_status(id, ProductStatus(status)))


def mutate_update_product_stock(
    self, info: Info, id: uuid.UUID, stock: int
) -> ProductType:
    ctx: AdminContext = info.context
    svc = ProductService(ctx.db)
    return _to_product_type(svc.update_stock(id, stock))


def mutate_set_product_featured(
    self, info: Info, id: uuid.UUID, is_featured: bool
) -> ProductType:
    ctx: AdminContext = info.context
    svc = ProductService(ctx.db)
    return _to_product_type(svc.set_featured(id, is_featured))


def mutate_add_product_image(
    self,
    info: Info,
    product_id: uuid.UUID,
    url: str,
    alt_text: str | None = None,
    display_order: int = 0,
    is_primary: bool = False,
) -> ProductType:
    ctx: AdminContext = info.context
    svc = ProductService(ctx.db)
    return _to_product_type(
        svc.add_image(
            product_id,
            url,
            alt_text=alt_text,
            display_order=display_order,
            is_primary=is_primary,
        )
    )


def mutate_remove_product_image(
    self, info: Info, image_id: uuid.UUID
) -> MutationResult:
    ctx: AdminContext = info.context
    ProductService(ctx.db).remove_image(image_id)
    return MutationResult(success=True, message="Product image removed")


def mutate_upload_product_image(
    self,
    info: Info,
    product_id: uuid.UUID,
    data_url: str,
    alt_text: str | None = None,
    display_order: int = 0,
    is_primary: bool = False,
) -> ProductType:
    """Upload a base64 image to Cloudinary and attach it to the product."""
    ctx: AdminContext = info.context
    svc = ProductService(ctx.db)
    return _to_product_type(
        svc.upload_image(
            product_id,
            data_url,
            alt_text=alt_text,
            display_order=display_order,
            is_primary=is_primary,
        )
    )


# ── categories ──────────────────────────────────────────────


def mutate_create_category(self, info: Info, data: CategoryInput) -> CategoryType:
    ctx: AdminContext = info.context
    svc = CategoryService(ctx.db)
    payload = CategoryCreate(
        name=data.name,
        slug=data.slug,
        description=data.description,
        image_url=data.image_url,
        emoji=data.emoji,
        seo_title=data.seo_title,
        seo_description=data.seo_description,
        parent_id=data.parent_id,
        display_order=data.display_order,
        is_active=data.is_active,
        is_featured=data.is_featured,
    )
    return _to_category_type(svc.create(payload))


def mutate_update_category(
    self, info: Info, id: uuid.UUID, data: CategoryUpdateInput
) -> CategoryType:
    ctx: AdminContext = info.context
    svc = CategoryService(ctx.db)
    values: dict[str, Any] = {
        "name": data.name,
        "slug": data.slug,
        "description": data.description,
        "image_url": data.image_url,
        "emoji": data.emoji,
        "seo_title": data.seo_title,
        "seo_description": data.seo_description,
        "parent_id": data.parent_id,
        "display_order": data.display_order,
        "is_active": data.is_active,
        "is_featured": data.is_featured,
    }
    payload = CategoryUpdate(**{k: v for k, v in values.items() if v is not None})
    return _to_category_type(svc.update(id, payload))


def mutate_delete_category(self, info: Info, id: uuid.UUID) -> MutationResult:
    ctx: AdminContext = info.context
    svc = CategoryService(ctx.db)
    svc.delete(id)
    return MutationResult(success=True, message="Category deleted")


def mutate_set_category_active(
    self, info: Info, id: uuid.UUID, is_active: bool
) -> CategoryType:
    ctx: AdminContext = info.context
    svc = CategoryService(ctx.db)
    return _to_category_type(svc.set_active(id, is_active))


def mutate_set_category_featured(
    self, info: Info, id: uuid.UUID, is_featured: bool
) -> CategoryType:
    ctx: AdminContext = info.context
    svc = CategoryService(ctx.db)
    return _to_category_type(svc.set_featured(id, is_featured))
