from fastapi import Request
from fastapi.responses import HTMLResponse
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from . import router, templates
from sqlmodel import select
from app.models.user import User
from app.models.hourlog import HourLog
from app.models.milestone import Milestone, UserMilestone


@router.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard_view(request: Request, user: AuthDep, db: SessionDep):
    # Compute approved hours per user
    # Only include regular students (exclude admins)
    users = db.exec(select(User).where(User.role == "regular_user")).all()
    rows = []
    for u in users:
        approved = db.exec(select(HourLog).where(HourLog.user_id == u.id, HourLog.status == "approved")).all()
        total = sum(r.hours for r in approved)
        rows.append({"id": u.id, "username": u.username, "total_hours": total})

    # Sort by total desc, then username (alphabetical) as tie-breaker
    rows.sort(key=lambda r: (-r["total_hours"], r["username"]))

    # determine current user's rank (if student)
    your_rank = None
    your_total = 0.0
    for idx, r in enumerate(rows, start=1):
        if r["id"] == user.id:
            your_rank = idx
            your_total = r["total_hours"]
            break

    return templates.TemplateResponse(request=request, name="leaderboard.html", context={"user": user, "rows": rows, "your_rank": your_rank, "your_total": your_total})


@router.get("/milestones", response_class=HTMLResponse)
async def milestones_view(request: Request, user: AuthDep, db: SessionDep):
    # list milestones and user's unlocked ones
    milestones = db.exec(select(Milestone).order_by(Milestone.hours_threshold)).all()
    unlocked = db.exec(select(UserMilestone).where(UserMilestone.user_id == user.id)).all()
    unlocked_ids = {u.milestone_id for u in unlocked}

    # compute total approved hours
    approved_rows = db.exec(select(HourLog).where(HourLog.user_id == user.id, HourLog.status == "approved")).all()
    total_hours = sum(r.hours for r in approved_rows)

    # find next locked milestone (smallest threshold > total_hours)
    next_milestone = None
    for m in milestones:
        if m.id not in unlocked_ids and m.hours_threshold > total_hours:
            next_milestone = m
            break

    items = []
    for m in milestones:
        items.append({"id": m.id, "name": m.name, "hours_threshold": m.hours_threshold, "badge_label": m.badge_label, "unlocked": m.id in unlocked_ids})

    return templates.TemplateResponse(request=request, name="milestones.html", context={"user": user, "milestones": items, "total_hours": total_hours, "next_milestone": next_milestone})
