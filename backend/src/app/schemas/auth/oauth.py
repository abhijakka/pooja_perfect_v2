from pydantic import Field

from ..common import SchemaBase


class OAuthLoginInput(SchemaBase):
    provider: str = Field(min_length=1, max_length=32)
    id_token: str = Field(min_length=1)


class OAuthProviderConfigResponse(SchemaBase):
    """Public browser-side OAuth bootstrap.

    Carries the *public* client id only — the same value the backend passes to
    ``verify_oauth2_token`` as the expected audience, so the browser and the
    verifier can never drift apart. The client secret is deliberately absent and
    is not referenced by any code path.
    """

    client_id: str = ""
