from fastapi import APIRouter, Form, Request, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from passlib.context import CryptContext

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import User, Leave
from app.db import get_db


router = APIRouter()
templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

print("✅ leave.py loaded")
print("✅ Has router:", 'router' in globals())

# ----------------- Leave Dashboard (only accessible if logged in)-----------------

@router.get("/uleaveDashboard", response_class=HTMLResponse)
async def show_leave_page(request: Request, db: AsyncSession = Depends(get_db)):
    if not request.session.get("user_logged_in"):
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    username = request.session.get("username")

    # Fetch user object to get full name (needed for filtering leaves)
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    # Fetch all leaves assigned to this user
    result = await db.execute(select(Leave).where(Leave.employee_id == user.id))
    leaves = result.scalars().all()

    # Calculate total leave days per type
    leave_totals = {
        "Sick Leave": 0,
        "Personal Leave": 0,
        "Family Emergency": 0
    }

    for leave in leaves:
        if leave.comment in leave_totals:
            days = (leave.end_date - leave.start_date).days + 1
            leave_totals[leave.comment] += days

    return templates.TemplateResponse("user_leave_dashboard.html", {
        "request": request,
        "username": username,
        "leave_totals": leave_totals
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

