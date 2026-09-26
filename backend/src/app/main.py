from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from strawberry.fastapi import GraphQLRouter

from app.admin.api.graphql.schema import admin_schema
from app.admin.context import get_admin_context
from app.api.auth import router as auth_router
from app.api.tracking import router as tracking_router
from app.api.webhooks.payment import router as payment_webhook_router
from app.config import settings
from app.core.exceptions import AppError
from app.db import check_db_health
from app.middleware.activity_log import ActivityLogMiddleware
from app.middleware.ip_tracking import IPActivityMiddleware
from app.public.api.graphql.schema import public_schema
from app.public.context import get_public_context

app = FastAPI(title="PoojaPoint", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    # Configured via CORS_ALLOW_ORIGINS so a new dev host or LAN address can be
    # added without editing code. Credentials are on because auth is cookie
    # based, so a wildcard origin is not permitted (see Settings.cors_allow_origins).
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(IPActivityMiddleware)
app.add_middleware(ActivityLogMiddleware)
app.include_router(auth_router)
app.include_router(tracking_router)
app.include_router(payment_webhook_router)

# Public (customer) GraphQL API at /graphql — optional auth.
public_graphql = GraphQLRouter(
    public_schema,
    context_getter=get_public_context,
    graphql_ide="graphiql",
)
app.include_router(public_graphql, prefix="/graphql")

# Admin GraphQL API at /admin/graphql — require_admin gated.
admin_graphql = GraphQLRouter(
    admin_schema,
    context_getter=get_admin_context,
    graphql_ide="graphiql",
)
app.include_router(admin_graphql, prefix="/admin/graphql")


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok", "database": check_db_health()}
