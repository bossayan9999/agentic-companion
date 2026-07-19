"""
Stub for multi-tenant auth. Swap this for Clerk/Auth0/Supabase Auth
or roll your own JWT issuance — the important part already done for you
is that tenant_id is threaded through memory/store.py and the tool layer,
so whichever auth provider you pick just needs to resolve a request to a
stable tenant_id.
"""
from fastapi import Header, HTTPException


def get_tenant_id(x_api_key: str = Header(...)) -> str:
    # TODO: replace with real lookup against your auth provider / DB
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
    return f"tenant_{x_api_key[:8]}"
