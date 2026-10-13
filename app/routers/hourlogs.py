from fastapi import Request, APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep, AdminDep
from . import router, templates
from app.services.hourlog_service import HourLogService
from sqlmodel import select
from app.models.hourlog import Activity, HourLog
from app.models.user import User


@router.get("/hours/log", response_class=HTMLResponse)
async def log_hours_view(request: Request, user: AuthDep, db: SessionDep):
    # redirect admins away from the student log page
    if getattr(user, "role", "") == "admin":
        return RedirectResponse(url="/admin/approvals", status_code=303)
    # Load active activities for dropdown
    activities = db.exec(select(Activity).where(Activity.is_active == True)).all()

    # Load the student's history (most recent first) and include activity titles
    history_rows = db.exec(select(HourLog).where(HourLog.user_id == user.id).order_by(HourLog.submitted_at.desc())).all()
    history = []
    for h in history_rows:
        act = db.get(Activity, h.activity_id)
        history.append({
            "id": h.id,
            "activity_title": act.title if act else f"(id {h.activity_id})",
            "hours": h.hours,
            "status": h.status,
            "reject_reason": h.reject_reason,
            "submitted_at": h.submitted_at,
        })

    return templates.TemplateResponse(request=request, name="log_hours.html", context={"user": user, "activities": activities, "history": history})


@router.post("/hours/submit")
async def submit_hourlog(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    activity_id: int = Form(...),
    hours: float = Form(...),
    proof_note: str = Form("")
):
    # prevent admins from submitting hour logs
    if getattr(user, "role", "") == "admin":
        return RedirectResponse(url="/admin/approvals", status_code=303)
    service = HourLogService(db)
    hourlog_data = {
        "user_id": user.id,
        "activity_id": activity_id,
        "hours": hours,
        "proof_note": proof_note,
    }
    service.submit_hourlog(hourlog_data)
    return RedirectResponse(url="/app", status_code=303)

 
@router.get("/admin/approvals", response_class=HTMLResponse)
async def admin_approvals_view(request: Request, user: AdminDep, db: SessionDep):
    service = HourLogService(db)
    pending = service.list_pending()

    # Enrich pending rows with username and activity title for display
    pending_display = []
    for h in pending:
        u = db.get(User, h.user_id)
        act = db.get(Activity, h.activity_id)
        pending_display.append({
            "id": h.id,
            "username": u.username if u else f"user {h.user_id}",
            "activity_title": act.title if act else f"activity {h.activity_id}",
            "hours": h.hours,
            "proof_note": h.proof_note,
            "submitted_at": h.submitted_at,
            "reject_reason": h.reject_reason,
        })

    return templates.TemplateResponse(request=request, name="admin_approvals.html", context={"user": user, "pending": pending_display})


@router.post("/admin/approvals/{hour_id}/approve")
async def admin_approve(hour_id: int, user: AdminDep, db: SessionDep):
    service = HourLogService(db)
    service.approve(hour_id, user.id)
    return RedirectResponse(url="/admin/approvals", status_code=303)


@router.post("/admin/approvals/{hour_id}/reject")
async def admin_reject(hour_id: int, user: AdminDep, db: SessionDep, reason: str = Form(...)):
    service = HourLogService(db)
    service.reject(hour_id, user.id, reason)
    return RedirectResponse(url="/admin/approvals", status_code=303)
