"""hello: a visit counter, the version, and who you are after signing in."""
import html
import os

from authlib.integrations.starlette_client import OAuth
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from .db import connect

APP_URL = os.environ["APP_URL"].rstrip("/")
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(SessionMiddleware, secret_key=os.environ["SECRET_KEY"], https_only=True, same_site="lax")
oauth = OAuth()
oauth.register(
    "platform",
    server_metadata_url=f"{os.environ['OIDC_ISSUER']}/.well-known/openid-configuration",
    client_id=os.environ["OIDC_CLIENT_ID"],
    client_secret=os.environ["OIDC_CLIENT_SECRET"],
    client_kwargs={"scope": "openid profile email groups", "code_challenge_method": "S256"},
)


def page(body: str) -> HTMLResponse:
    env = os.environ.get("APP_ENV", "?")
    banner = "" if env == "prod" else f"<p style='background:#fd0;padding:4px'>{html.escape(env)} copy</p>"
    return HTMLResponse(f"<!doctype html><title>hello</title>{banner}{body}"
                        f"<p><small>version {html.escape(os.environ.get('APP_VERSION', '?'))}</small></p>")


@app.get("/health", response_class=PlainTextResponse)
def health() -> str:
    with connect() as c:
        c.execute("SELECT 1")
    return "ok"


@app.get("/")
def index() -> HTMLResponse:
    with connect() as c:
        n = c.execute("INSERT INTO visits (id, n) VALUES (1, 1) ON CONFLICT (id) DO UPDATE SET n = visits.n + 1 "
                      "RETURNING n").fetchone()[0]
        ticks = c.execute("SELECT count(*) FROM ticks").fetchone()[0]
    greeting = html.escape(os.environ.get("HELLO_GREETING", "Hello"))
    return page(f"<h1>{greeting}</h1><p>Visit number <b id=visits>{n}</b>. "
                f"Ticks: <b id=ticks>{ticks}</b>.</p><p><a href='/me'>Who am I?</a></p>")


@app.get("/me")
async def me(request: Request):
    user = request.session.get("user")
    if not user:
        return await oauth.platform.authorize_redirect(request, f"{APP_URL}/oidc/callback/")
    groups = ", ".join(html.escape(g) for g in user.get("groups", [])) or "none"
    return page(f"<h1>{html.escape(user.get('preferred_username', '?'))}</h1>"
                f"<p>Groups: <span id=groups>{groups}</span></p>")


@app.get("/oidc/callback/")
async def callback(request: Request):
    token = await oauth.platform.authorize_access_token(request)
    info = token.get("userinfo") or {}
    request.session["user"] = {"preferred_username": info.get("preferred_username"),
                               "groups": list(info.get("groups", []))}
    return RedirectResponse("/me", status_code=303)
