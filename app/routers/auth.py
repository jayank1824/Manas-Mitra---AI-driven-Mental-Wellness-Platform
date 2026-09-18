from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth_service import (
    verify_password, create_user, set_auth_cookie, 
    get_current_user_from_cookie
)
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request, error: str = None, success: str = None, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("auth/login.html", {
        "request": request, 
        "hide_sidebar": True,
        "error": error,
        "success": success
    })

@router.post("/login")
async def login_post(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return RedirectResponse(url="/auth/login?error=Invalid%20credentials", status_code=303)
        
    response = RedirectResponse(url="/dashboard", status_code=303)
    return set_auth_cookie(response, user)

@router.get("/register", response_class=HTMLResponse)
async def register_get(request: Request, error: str = None, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("auth/register.html", {
        "request": request, 
        "hide_sidebar": True,
        "error": error
    })

@router.post("/register")
async def register_post(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    phone: str = Form(None),
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return RedirectResponse(url="/auth/register?error=Email%20already%20registered", status_code=303)
        
    create_user(db, email, name, password, phone)
    return RedirectResponse(url="/auth/login?success=Registration%20successful.%20Please%20login.", status_code=303)

@router.get("/verify/{token}", response_class=HTMLResponse)
async def verify_get(request: Request, token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    if user:
        user.is_verified = True
        user.verification_token = None
        db.commit()
    return templates.TemplateResponse("auth/verify.html", {"request": request, "hide_sidebar": True})

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("access_token")
    return response
