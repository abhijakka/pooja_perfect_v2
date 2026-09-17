from fastapi import APIRouter, Header, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError
from app.db import get_db
from app.public.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/webhook")
async def payment_webhook(
    request: Request,
    x_phonepe_signature: str | None = Header(default=None, alias="X-Phonepe-Signature"),
) -> JSONResponse:
    """Handle payment provider webhooks.

    Only a verified HMAC-SHA256 signature (using ``payment_webhook_secret``)
    can update payment/order status. Unverified payloads are rejected.
    """
    payload = await request.json()
    db = next(get_db())
    try:
        svc = PaymentService(db)
        svc.handle_webhook(payload, x_phonepe_signature)
        return JSONResponse({"status": "received"})
    except AppError as exc:
        db.rollback()
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    finally:
        db.close()
