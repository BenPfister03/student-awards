from fastapi import Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from . import router, templates
from app.dependencies.auth import AuthDep, AdminDep
from app.dependencies.session import SessionDep
from app.services.redemption_service import RedemptionService
from sqlmodel import select
from app.models.prize import Prize, Redemption
from app.models.user import User
from app.models.hourlog import HourLog
import urllib.parse


@router.get("/prizes", response_class=HTMLResponse)
async def prizes_view(request: Request, user: AuthDep, db: SessionDep):
    prizes = db.exec(select(Prize).where(Prize.is_active == True)).all()
    approved = db.exec(select(HourLog).where(HourLog.user_id == user.id, HourLog.status == "approved")).all()
    total_approved = sum(r.hours for r in approved)
    redeemable = total_approved - (user.points_spent or 0.0)
    # read optional error message from query params (URL-decoded)
    error_raw = request.query_params.get("error")
    error = urllib.parse.unquote_plus(error_raw) if error_raw else None
    return templates.TemplateResponse(request=request, name="prizes.html", context={"user": user, "prizes": prizes, "redeemable": redeemable, "error": error})


@router.post("/prizes/{prize_id}/redeem")
async def redeem_action(prize_id: int, user: AuthDep, db: SessionDep):
    svc = RedemptionService(db)
    try:
        svc.redeem_prize(user, prize_id)
    except Exception as exc:
        # encode message and redirect back to prizes page so it can display nicely
        msg = urllib.parse.quote_plus(str(exc))
        return RedirectResponse(url=f"/prizes?error={msg}", status_code=303)
    return RedirectResponse(url="/prizes", status_code=303)


@router.get("/redemptions", response_class=HTMLResponse)
async def admin_redemptions(request: Request, user: AdminDep, db: SessionDep):
    rows = db.exec(select(Redemption).order_by(Redemption.requested_at.desc())).all()
    enriched = []
    for r in rows:
        u = db.get(User, r.user_id)
        p = db.get(Prize, r.prize_id)
        enriched.append(
            {
                "id": r.id,
                "username": u.username if u else f"user:{r.user_id}",
                "prize_name": p.name if p else f"prize:{r.prize_id}",
                "hours_cost": r.hours_cost,
                "requested_at": r.requested_at,
                "status": r.status,
            }
        )
    return templates.TemplateResponse(request=request, name="admin_redemptions.html", context={"user": user, "rows": enriched})


@router.post("/redemptions/{rid}/fulfill")
async def admin_fulfill(rid: int, user: AdminDep, db: SessionDep):
    svc = RedemptionService(db)
    svc.fulfill(rid, user.id)
    return RedirectResponse(url="/redemptions", status_code=303)
