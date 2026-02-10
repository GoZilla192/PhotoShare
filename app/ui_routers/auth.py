from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from app.auth.service import AuthService
from app.dependency.dependencies import auth_service
from app.ui_routers.deps import get_templates, get_token_from_cookie, COOKIE_NAME

router = APIRouter(prefix="/auth", tags=["UI-Auth"])

@router.get("/login")
async def ui_login_form(request: Request):
    templates = get_templates(request)
    return templates.TemplateResponse("pages/auth/login.html", {"request": request})

@router.post("/login")
async def ui_login_submit(
    email: str = Form(...),
    password: str = Form(...),
    svc: AuthService = Depends(auth_service),
):
    token = await svc.login(email=email, password=password)
    resp = RedirectResponse(url="/ui/", status_code=303)
    resp.set_cookie(COOKIE_NAME, token, httponly=True, samesite="lax", path="/")
    return resp

@router.get("/register")
async def ui_register_form(request: Request):
    templates = get_templates(request)
    return templates.TemplateResponse("pages/auth/register.html", {"request": request})

@router.post("/register")
async def ui_register_submit(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    svc: AuthService = Depends(auth_service),
):
    token = await svc.register(username=username, email=email, password=password)
    resp = RedirectResponse(url="/ui/", status_code=303)
    resp.set_cookie(COOKIE_NAME, token, httponly=True, samesite="lax", path="/")
    return resp

@router.post("/logout")
async def ui_logout(
    token: str | None = Depends(get_token_from_cookie),
    svc: AuthService = Depends(auth_service),
):
    if token:
        await svc.logout(token)
    resp = RedirectResponse(url="/ui/", status_code=303)
    resp.delete_cookie(COOKIE_NAME, path="/")
    return resp