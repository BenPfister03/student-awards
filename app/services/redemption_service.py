from sqlmodel import Session, select
from datetime import datetime
from app.models.prize import Prize, Redemption
from app.models.hourlog import HourLog


class RedemptionService:
    def __init__(self, db: Session):
        self.db = db

    def redeem_prize(self, user, prize_id: int) -> Redemption:
        prize = self.db.get(Prize, prize_id)
        if not prize or not prize.is_active:
            raise Exception("Prize not available")

        # Compute redeemable balance: sum of approved hours - user.points_spent
        approved_rows = self.db.exec(select(HourLog).where(HourLog.user_id == user.id, HourLog.status == "approved")).all()
        total_approved = sum(r.hours for r in approved_rows)
        redeemable = total_approved - (user.points_spent or 0.0)

        if prize.stock <= 0:
            raise Exception("Out of stock")

        if redeemable < prize.hours_cost:
            needed = prize.hours_cost - redeemable
            raise Exception(f"Insufficient balance: need {needed:g} more hours")

        # immediate stock decrement and immediate spend
        prize.stock -= 1
        user = self.db.merge(user)  # attach the logged-in user to this session
        user.points_spent = (user.points_spent or 0.0) + prize.hours_cost

        redemption = Redemption(
            user_id=user.id,
            prize_id=prize.id,
            hours_cost=prize.hours_cost,
            status="requested",
        )

        # one commit, so all three changes save together or not at all
        self.db.add(prize)
        self.db.add(user)
        self.db.add(redemption)
        self.db.commit()
        self.db.refresh(redemption)
        return redemption

    def fulfill(self, redemption_id: int, admin_id: int) -> Redemption:
        r = self.db.get(Redemption, redemption_id)
        if not r:
            raise Exception("Redemption not found")
        r.status = "fulfilled"
        r.fulfilled_by = admin_id
        r.fulfilled_at = datetime.utcnow()
        self.db.add(r)
        self.db.commit()
        self.db.refresh(r)
        return r
