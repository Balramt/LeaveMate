from fastapi import APIRouter, Request, status, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import get_db
from app.models import User, Leave
from datetime import date
from sqlalchemy import and_
from fastapi import Query
import io
import csv
from fpdf import FPDF
from fastapi.responses import StreamingResponse
from typing import Optional, Union
from math import ceil


router = APIRouter()
templates = Jinja2Templates(directory="templates")

print("✅ adminleave.py loaded")

# ------------------------ Dashboard Route ------------------------
# Admin dashboard route
@router.get("/aleaveDashboard", response_class=HTMLResponse)
async def show_admin_leave_page(request: Request):
    if not request.session.get("admin_logged_in"):
        return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "username": request.session.get("username")

    })

# ------------------------ View admin Leave dashboard ------------------------

@router.get("/admin/leave-dashboard", response_class=HTMLResponse)
async def show_admin_leave_dashboard(request: Request):
    if not request.session.get("admin_logged_in"):
        return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("admin_leave_dashboard.html", {
        "request": request,
        "username": request.session.get("username")
    })


# ------------------------ Employee adding Leave Page ------------------------

@router.get("/admin/employee-leaves", response_class=HTMLResponse)
async def admin_employee_leave_page(request: Request, db: AsyncSession = Depends(get_db)):
    if not request.session.get("admin_logged_in"):
        return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

    result = await db.execute(select(User))
    users = result.scalars().all()

    return templates.TemplateResponse("admin_leave_management.html", {
        "request": request,
        "username": request.session.get("username"),
        "users": users
    })

# ------------------------Delete/ modify admin report ------------------------

@router.get("/admin/modify-leave", response_class=HTMLResponse)
async def show_modify_leave(
    request: Request,
    employee_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1),
    db: AsyncSession = Depends(get_db)
):
    if not request.session.get("admin_logged_in"):
        return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

    result_users = await db.execute(select(User))
    user_list = result_users.scalars().all()

    leaves = []
    total_pages = 0

    if employee_id:
        total_query = await db.execute(
            select(Leave).where(Leave.employee_id == employee_id)
        )
        total_leaves = total_query.scalars().all()
        total_count = len(total_leaves)
        total_pages = ceil(total_count / per_page)

        offset = (page - 1) * per_page
        paginated_query = await db.execute(
            select(Leave)
            .where(Leave.employee_id == employee_id)
            .offset(offset)
            .limit(per_page)
        )
        leaves = paginated_query.scalars().all()

    return templates.TemplateResponse("admin_modify_leave.html", {
        "request": request,
        "users": user_list,
        "leaves": leaves,
        "selected_id": employee_id,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages
    })


# ------------------ Delete Leave ------------------
@router.post("/admin/delete-leave/{leave_id}")
async def delete_leave(leave_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Leave).where(Leave.id == leave_id))
    leave = result.scalar_one_or_none()
    if leave:
        await db.delete(leave)
        await db.commit()
    return RedirectResponse(url="/admin/modify-leave", status_code=303)


# ------------------ Edit Leave Form ------------------
@router.get("/admin/edit-leave/{leave_id}", response_class=HTMLResponse)
async def edit_leave_form(leave_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    if not request.session.get("admin_logged_in"):
        return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

    result = await db.execute(select(Leave).where(Leave.id == leave_id))
    leave = result.scalar_one_or_none()

    if not leave:
        return HTMLResponse("Leave not found", status_code=404)

    return templates.TemplateResponse("admin_edit_leave.html", {
        "request": request,
        "leave": leave
    })


# ------------------ Update Leave Submission ------------------
@router.post("/admin/update-leave/{leave_id}")
async def update_leave(
    leave_id: int,
    start_date: date = Form(...),
    end_date: date = Form(...),
    comment: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Leave).where(Leave.id == leave_id))
    leave = result.scalar_one_or_none()

    if not leave:
        return HTMLResponse("Leave not found", status_code=404)

    leave.start_date = start_date
    leave.end_date = end_date
    leave.comment = comment

    await db.commit()

    return RedirectResponse(url="/admin/modify-leave", status_code=303)


# ------------------------Generate admin report ------------------------
# @router.get("/admin/leave-report", response_class=HTMLResponse)
# async def generate_leave_report(
#     request: Request,
#     start_date: date = Query(...),
#     end_date: date = Query(...),
#     employee_id: int = Query(None),
#     db: AsyncSession = Depends(get_db)
# ):
#     if not request.session.get("admin_logged_in"):
#         return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

#     query = select(Leave).where(
#         and_(
#             Leave.start_date >= start_date,
#             Leave.end_date <= end_date
#         )
#     )
#     if employee_id:
#         query = query.where(Leave.employee_id == employee_id)

#     result = await db.execute(query)
#     leaves = result.scalars().all()

#     summary = {
#     "total": sum((l.end_date - l.start_date).days + 1 for l in leaves),
#     "sick": sum((l.end_date - l.start_date).days + 1 for l in leaves if l.comment.strip().lower() == "sick leave"),
#     "personal": sum((l.end_date - l.start_date).days + 1 for l in leaves if l.comment.strip().lower() == "personal leave"),
#     "family": sum((l.end_date - l.start_date).days + 1 for l in leaves if l.comment.strip().lower() == "family emergency"),
# }


#     users_result = await db.execute(select(User))
#     users = users_result.scalars().all()

#     return templates.TemplateResponse("admin_leave_report.html", {
#         "request": request,
#         "leaves": leaves,
#         "start_date": start_date,
#         "end_date": end_date,
#         "selected_id": employee_id,
#         "users": users,
#         "summary": summary
#     })

@router.get("/admin/leave-report", response_class=HTMLResponse)
async def generate_leave_report(
    request: Request,
    start_date: date = Query(...),
    end_date: date = Query(...),
    employee_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1),
    db: AsyncSession = Depends(get_db)
):
    if not request.session.get("admin_logged_in"):
        return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

    # Fetch all users
    users_result = await db.execute(select(User))
    users = users_result.scalars().all()

    # Base query
    query = select(Leave).where(
        and_(
            Leave.start_date >= start_date,
            Leave.end_date <= end_date
        )
    )
    if employee_id:
        query = query.where(Leave.employee_id == employee_id)

    # Fetch all leaves for summary and download
    full_result = await db.execute(query)
    all_leaves = full_result.scalars().all()

    # Summary
    summary = {
        "total": sum((l.end_date - l.start_date).days + 1 for l in all_leaves),
        "sick": sum((l.end_date - l.start_date).days + 1 for l in all_leaves if l.comment.strip().lower() == "sick leave"),
        "personal": sum((l.end_date - l.start_date).days + 1 for l in all_leaves if l.comment.strip().lower() == "personal leave"),
        "family": sum((l.end_date - l.start_date).days + 1 for l in all_leaves if l.comment.strip().lower() == "family emergency"),
    }

    # Pagination
    total_count = len(all_leaves)
    total_pages = ceil(total_count / per_page)
    offset = (page - 1) * per_page
    paginated_leaves = all_leaves[offset:offset + per_page]

    return templates.TemplateResponse("admin_leave_report.html", {
        "request": request,
        "leaves": paginated_leaves,
        "start_date": start_date,
        "end_date": end_date,
        "selected_id": employee_id,
        "users": users,
        "summary": summary,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages
    })


# ------------------------ Download Leave Report ------------------------

@router.get("/admin/leave-report/download")
async def download_leave_report(
    format: str = Query(..., regex="^(csv|pdf)$"),
    start_date: date = Query(...),
    end_date: date = Query(...),
    #employee_id: int = Query(None),
    employee_id: Union[str, None] = Query(default=None),
    db: AsyncSession = Depends(get_db)
):
    query = select(Leave).where(
        and_(
            Leave.start_date >= start_date,
            Leave.end_date <= end_date
        )
    )
    #if employee_id:
    #if employee_id and employee_id.strip().isdigit():
    if employee_id and employee_id.strip().lower() != "all employees" and employee_id.strip().isdigit():
        #query = query.where(Leave.employee_id == employee_id)
        query = query.where(Leave.employee_id == int(employee_id))

    result = await db.execute(query)
    leaves = result.scalars().all()

    # 🧠 Summary Calculations
    def leave_days(leave):
        return (leave.end_date - leave.start_date).days + 1

    total_days = sum(leave_days(l) for l in leaves)
    sick_days = sum(leave_days(l) for l in leaves if l.comment.strip().lower() == "sick leave")
    personal_days = sum(leave_days(l) for l in leaves if l.comment.strip().lower() == "personal leave")
    family_days = sum(leave_days(l) for l in leaves if l.comment.strip().lower() == "family emergency")

    # ✅ CSV Export
    if format == "csv":
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["Employee", "Leave Type", "Start Date", "End Date", "Days"])
        for leave in leaves:
            days = leave_days(leave)
            writer.writerow([
                leave.name,
                leave.comment,
                leave.start_date.strftime("%Y-%m-%d"),
                leave.end_date.strftime("%Y-%m-%d"),
                days
            ])
        writer.writerow([])  # blank line
        writer.writerow(["Summary"])
        writer.writerow(["Total Leave Days", total_days])
        writer.writerow(["Sick Leave Days", sick_days])
        writer.writerow(["Personal Leave Days", personal_days])
        writer.writerow(["Family Emergency Days", family_days])
        buffer.seek(0)
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=leave_report.csv"}
        )

    # ✅ PDF Export
    elif format == "pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.set_text_color(0, 0, 0)

        pdf.cell(200, 10, txt="Leave Report", ln=1, align="C")
        pdf.ln(5)

        for leave in leaves:
            days = leave_days(leave)
            line = f"{leave.name} | {leave.comment} | {leave.start_date} - {leave.end_date} | {days} days"
            pdf.cell(200, 8, txt=line, ln=1)

        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Summary:", ln=1)

        pdf.set_font("Arial", size=11)
        pdf.cell(200, 8, txt=f"Total Leave Days: {total_days}", ln=1)
        pdf.cell(200, 8, txt=f"Sick Leave: {sick_days}", ln=1)
        pdf.cell(200, 8, txt=f"Personal Leave: {personal_days}", ln=1)
        pdf.cell(200, 8, txt=f"Family Emergency: {family_days}", ln=1)

        pdf_bytes = pdf.output(dest='S').encode('latin1')
        pdf_buffer = io.BytesIO(pdf_bytes)

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=leave_report.pdf"}
        )


# # ------------------------ Assign Leave Handler ------------------------

@router.post("/admin/assign-leave", response_class=HTMLResponse)
async def assign_leave(
    request: Request,
    employee_id: int = Form(...),
    name: str = Form(...),
    start_date: date = Form(...),
    end_date: date = Form(...),
    comment: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    if not request.session.get("admin_logged_in"):
        return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

    leave = Leave(
        employee_id=employee_id,
        name=name,
        start_date=start_date,
        end_date=end_date,
        comment=comment
    )
    db.add(leave)
    await db.commit()

    # Re-fetch users to re-populate the dropdown
    result = await db.execute(select(User))
    users = result.scalars().all()

    return templates.TemplateResponse("admin_leave_management.html", {
        "request": request,
        "username": request.session.get("username"),
        "users": users,
        "success": True,  # 👈 Send success flag to template
        "employee_name": name,
        "comment": comment
    })

# ------------------------ Admin Logout ------------------------

@router.get("/adminlogout", response_class=HTMLResponse)
async def logout(request: Request):
    request.session.clear()  # clear all session data
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
