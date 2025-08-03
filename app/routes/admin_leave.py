from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

print("✅ adminleave.py loaded")

# Admin dashboard route
@router.get("/aleaveDashboard", response_class=HTMLResponse)
async def show_admin_leave_page(request: Request):
    if not request.session.get("admin_logged_in"):
        return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "username": request.session.get("username")
    })

@router.get("/admin/employee-leaves", response_class=HTMLResponse)
async def admin_employee_leave_page(request: Request):
    if not request.session.get("admin_logged_in"):
        return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("admin_leave_management.html", {
        "request": request,
        "username": request.session.get("username")
    })




# auth.py (add at the bottom of the file)

@router.get("/adminlogout", response_class=HTMLResponse)
async def logout(request: Request):
    request.session.clear()  # clear all session data
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
