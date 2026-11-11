import traceback
import requests
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from urllib.parse import urlparse
from fastapi.templating import Jinja2Templates
from app.auth import get_user_from_session
from app.config import APP_ENV

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
ALLOWED_HOSTS = {"example.com", "www.example.com", "uis.no", "www.uis.no"}


def is_allowed_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    if parsed.scheme not in ("http", "https"):
        return False
    host = (parsed.hostname or "").lower()
    return host in ALLOWED_HOSTS

@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/status", response_class=HTMLResponse)
def status(request: Request):
    user = get_user_from_session(request)
    return templates.TemplateResponse(
        "status.html",
        {"request": request, "user": user, "env": APP_ENV, "python": "3.11", "service": "backend"},
    )


@router.get("/resources/import", response_class=HTMLResponse)
def import_resource_get(request: Request, url: str = ""):
    user = get_user_from_session(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    body = ""
    error = ""
    if url:
        if not is_allowed_url(url):
            error = "This URL is not allowed."
        else:
            try:
                r = requests.get(url, timeout=5, allow_redirects=False)
                body = r.text[:2000]
            except Exception:
                print(traceback.format_exc())
                error = "Could not fetch the resource."
    return templates.TemplateResponse(
        "resource_import.html",
        {"request": request, "user": user, "body": body, "url": url, "error": error},
    )


@router.post("/resources/import", response_class=HTMLResponse)
def import_resource_post(request: Request, url: str = Form(...)):
    return import_resource_get(request, url)


@router.get("/error", response_class=HTMLResponse)
def trigger_error(request: Request):
    try:
        x = 1 / 0
        return {"x": x}
    except Exception:
        print(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "details": "Something went wrong. Please try again later."},
            status_code=500,
        )
