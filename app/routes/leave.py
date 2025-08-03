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

print("✅ leave.py loaded")
print("✅ Has router:", 'router' in globals())
# Leave page (only accessible if logged in)
@router.get("/uleaveDashboard", response_class=HTMLResponse)
async def show_leave_page(request: Request):
    if not request.session.get("user_logged_in"):
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("user_leave_dashboard.html", {
        "request": request,
        "username": request.session.get("username")
    })

# GET: Show user registration form
@router.get("/register", response_class=HTMLResponse)
def show_user_register_form(request: Request):
    return templates.TemplateResponse("user_register.html", {"request": request})

# POST: Handle user registration
@router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    id: int = Form(...),
    name: str = Form(...),
    designation: str = Form(...),
    team: str = Form(...),
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    # Check if username or email already exists
    existing = await db.execute(select(User).where((User.username == username) | (User.email == email)))
    if existing.scalars().first():
        return templates.TemplateResponse("user_register.html", {
            "request": request,
            "error": "Username or email already exists"
        })

    hashed_password = pwd_context.hash(password)
    new_user = User(
        id=id,
        name=name,
        designation=designation,
        team=team,
        email=email,
        username=username,
        hashed_password=hashed_password
    )
    db.add(new_user)
    await db.commit()

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

# auth.py (add at the bottom of the file)

@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    request.session.clear()  # clear all session data
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

