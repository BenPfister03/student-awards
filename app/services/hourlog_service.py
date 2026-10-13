from typing import List, Optional
from sqlmodel import Session, select
from app.repositories.hourlog import HourLogRepository
from app.models.hourlog import HourLog
from app.models.milestone import Milestone, UserMilestone
from datetime import datetime

class HourLogService:
    def __init__(self, db: Session):
        self.repo = HourLogRepository(db)
        self.db = db

    def submit_hourlog(self, hourlog_data: dict) -> HourLog:
        # hourlog_data is expected to map to HourLog fields
        hourlog = HourLog(**hourlog_data)
        return self.repo.create(hourlog)

    def list_pending(self) -> List[HourLog]:
        return self.repo.get_pending()

    def approve(self, hourlog_id: int, reviewer_id: int) -> HourLog:
        hl = self.repo.get_by_id(hourlog_id)
        if not hl:
            raise Exception("HourLog not found")
        hl.status = "approved"
        hl.reviewed_by = reviewer_id
        hl.reviewed_at = datetime.utcnow()
        # persist approval
        hl = self.repo.update(hl)

        # After approval, compute lifetime approved hours for the user and award milestones
        approved_rows = self.db.exec(select(HourLog).where(HourLog.user_id == hl.user_id, HourLog.status == "approved")).all()
        total_hours = sum(r.hours for r in approved_rows)

        # Find milestones that the user now qualifies for and insert UserMilestone entries if missing
        milestones = self.db.exec(select(Milestone).where(Milestone.hours_threshold <= total_hours)).all()
        for m in milestones:
            existing = self.db.exec(select(UserMilestone).where(UserMilestone.user_id == hl.user_id, UserMilestone.milestone_id == m.id)).one_or_none()
            if not existing:
                um = UserMilestone(user_id=hl.user_id, milestone_id=m.id)
                self.db.add(um)
        self.db.commit()

        return hl

    def reject(self, hourlog_id: int, reviewer_id: int, reason: str) -> HourLog:
        hl = self.repo.get_by_id(hourlog_id)
        if not hl:
            raise Exception("HourLog not found")
        hl.status = "rejected"
        hl.reviewed_by = reviewer_id
        hl.reviewed_at = datetime.utcnow()
        hl.reject_reason = reason
        return self.repo.update(hl)
