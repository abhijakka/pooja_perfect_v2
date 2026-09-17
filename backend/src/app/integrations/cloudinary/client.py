"""Cloudinary media upload client.

Uploads base64 image data to Cloudinary and returns the secure CDN URL.
Credentials come from the app settings (``CLOUDINARY_*`` env vars).
"""

from __future__ import annotations

import base64
import io
import uuid

import cloudinary
import cloudinary.uploader
from app.config import settings


class CloudinaryClient:
    """Thin wrapper around the Cloudinary SDK for image uploads."""

    def __init__(self) -> None:
        self._configured = bool(
            settings.cloudinary_cloud_name
            and settings.cloudinary_api_key
            and settings.cloudinary_api_secret
        )
        if self._configured:
            cloudinary.config(
                cloud_name=settings.cloudinary_cloud_name,
                api_key=settings.cloudinary_api_key,
                api_secret=settings.cloudinary_api_secret,
                secure=True,
            )

    def upload_base64(
        self,
        data_url: str,
        folder: str = "products",
        public_id: str | None = None,
    ) -> str:
        """Upload a base64 data URL and return the secure Cloudinary URL.

        Accepts either a full ``data:image/png;base64,...`` data URL or a raw
        base64 payload. Raises ``RuntimeError`` when Cloudinary is not
        configured.
        """
        if not self._configured:
            raise RuntimeError(
                "Cloudinary is not configured. Set CLOUDINARY_CLOUD_NAME, "
                "CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET in the backend .env."
            )
        raw, fmt = self._decode_with_format(data_url)
        upload_kwargs: dict[str, object] = {
            "public_id": public_id or uuid.uuid4().hex,
            "folder": folder,
            "resource_type": "image",
        }
        if fmt:
            upload_kwargs["format"] = fmt
        result = cloudinary.uploader.upload(io.BytesIO(raw), **upload_kwargs)
        return result["secure_url"]

    def delete(self, public_id: str) -> None:
        """Delete an asset by its public id (no-op when not configured)."""
        if self._configured:
            cloudinary.uploader.destroy(public_id)

    @staticmethod
    def _decode_with_format(data_url: str) -> tuple[bytes, str | None]:
        """Decode a data URL into raw bytes and an optional format.

        Returns ``(raw_bytes, format_or_none)`` where *format* is the image
        extension derived from the MIME type (e.g. ``"png"``, ``"jpeg"``).
        """
        fmt: str | None = None
        if data_url.startswith("data:"):
            # data:image/png;base64,AAAA …
            header, _, b64 = data_url.partition(",")
            # header is like ``data:image/png;base64``
            mime = header.split(":", 1)[1].split(";", 1)[0]  # image/png
            fmt = mime.split("/")[-1]  # png
            if fmt == "jpeg":
                fmt = "jpg"
        else:
            b64 = data_url
        return base64.b64decode(b64), fmt


cloudinary_client = CloudinaryClient()