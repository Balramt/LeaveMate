from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

print("✅ leave.py loaded")
print("✅ Has router:", 'router' in globals())
# Leave page (only accessible if logged in)
@router.get("/leaveDashboard", response_class=HTMLResponse)
async def show_leave_page(request: Request):
    if not request.session.get("user_logged_in"):
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("leave_dashboard.html", {
        "request": request,
        "username": request.session.get("username")
    })
