"""Typed wrappers around the Topologis public API.

Keeps ``http_client`` generic. Each function here owns one endpoint, normalises
its response, and returns a plain tuple the GUI can consume without knowing
about HTTP status codes or JSON shapes.
"""

from typing import Optional, Tuple

from .config import API_URL
from .http_client import post_json


def sync_anonymous_session(
    token: Optional[str], session: Optional[str]
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """POST whatever ``(token, session)`` we have (either, both, or neither) to
    ``/api/public/anonymous-session`` and return the fresh ``(token, session,
    error)`` the server hands back.

    The server is the sole authority on this pair: it validates when both are
    present, rotates them when stale or revoked, and mints from scratch on an
    empty body. Callers persist the returned pair for next time.
    """
    payload = {}
    if token:
        payload["token"] = token
    if session:
        payload["session"] = session

    status, body = post_json(f"{API_URL}/api/public/anonymous-session", payload)
    if (status == 200 and isinstance(body, dict) and body.get("token") and body.get("session")):
        return str(body["token"]), str(body["session"]), None

    # Surface a server-provided message when present, otherwise fall back to a
    # generic line that still tells the user which step failed.
    err = body.get("error") if isinstance(body, dict) else None
    return None, None, err or f"Could not start anonymous session (HTTP {status})"
