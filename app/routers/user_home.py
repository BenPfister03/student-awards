from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import status
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep, IsUserLoggedIn, get_current_user, is_admin
from . import router, templates
from sqlmodel import select
from app.models.hourlog import HourLog
from app.models.milestone import Milestone, UserMilestone


@router.get("/app", response_class=HTMLResponse)
async def user_home_view(
    request: Request,
    user: AuthDep,
    db: SessionDep
):
    # Redirect admins to the admin dashboard
    if getattr(user, "role", "") == "admin":
        return RedirectResponse(url="/admin", status_code=303)
    # approved hours
    approved_rows = db.exec(select(HourLog).where(HourLog.user_id == user.id, HourLog.status == "approved")).all()
    approved_hours = sum(r.hours for r in approved_rows)
    redeemable = approved_hours - (user.points_spent or 0.0)

    # rank: compute total approved per user and sort
    rows = db.exec(select(HourLog.user_id, HourLog.hours).where(HourLog.status == "approved")).all()
    sums = {}
    for uid, hrs in rows:
        sums[uid] = sums.get(uid, 0.0) + hrs
    ordered = sorted(sums.items(), key=lambda t: t[1], reverse=True)
    rank = None
    for idx, (uid, total) in enumerate(ordered, start=1):
        if uid == user.id:
            rank = idx
            break

    # latest unlocked milestone
    um = db.exec(select(UserMilestone).where(UserMilestone.user_id == user.id).order_by(UserMilestone.unlocked_at.desc())).first()
    latest_milestone = None
    if um:
        m = db.get(Milestone, um.milestone_id)
        latest_milestone = m.name if m else None

    return templates.TemplateResponse(
        request=request,
        name="app.html",
        context={
            "user": user,
            "approved_hours": approved_hours,
            "redeemable": redeemable,
            "rank": rank,
            "latest_milestone": latest_milestone,
        },
    )