from fastapi import APIRouter, Form, Request, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import User
from app.db import get_db

router = APIRouter()
templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------------- USER SECTION ----------------------------

# GET: Show user login page
@router.get("/", response_class=HTMLResponse)
async def show_user_login_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})
    #return HTMLResponse(content="✅ Server is working", status_code=200)

# POST: Handle user login
@router.post("/Userlogin", response_class=HTMLResponse)
async def user_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()

    if user and pwd_context.verify(password, user.hashed_password):
        request.session["user_logged_in"] = True
        request.session["username"] = user.username
        return RedirectResponse(url="/uleaveDashboard", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("home.html", {"request": request, "error": "Invalid credentials"})


# ---------------------------- ADMIN SECTION ----------------------------

# Hardcoded admin credentials
ADMIN_USER = "admin"
ADMIN_PASSWORD_HASH = "$2b$12$7QDIOKX83ydJhgooZeK6kOk8LZhmI5HGjNcCERgjlTbe3c1jvf1Kq"

# GET: Show admin login page
@router.get("/admin", response_class=HTMLResponse)
async def show_admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

# POST: Handle admin login
@router.post("/admin/login", response_class=HTMLResponse)
async def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    if username == ADMIN_USER and pwd_context.verify(password, ADMIN_PASSWORD_HASH):
        request.session["admin_logged_in"] = True
        request.session["username"] = username
        return RedirectResponse(url="/aleaveDashboard", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("admin_login.html", {"request": request, "error": "Invalid admin credentials"})


