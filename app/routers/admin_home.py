from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import status
from app.dependencies.session import SessionDep
from app.dependencies.auth import AdminDep, IsUserLoggedIn, get_current_user, is_admin
from . import router, templates
from sqlmodel import select
from app.models.hourlog import HourLog
from app.models.prize import Redemption


@router.get("/admin", response_class=HTMLResponse)
async def admin_home_view(
    request: Request,
    user: AdminDep,
    db:SessionDep
):
    pending = db.exec(select(HourLog).where(HourLog.status == "pending")).all()
    pending_count = len(pending)
    redemptions = db.exec(select(Redemption).where(Redemption.status == "requested")).all()
    redemptions_count = len(redemptions)
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "user": user,
            "pending_count": pending_count,
            "redemptions_count": redemptions_count,
        },
    )
