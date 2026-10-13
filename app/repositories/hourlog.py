from sqlmodel import Session, select
from app.models.hourlog import HourLog, Activity
from typing import List, Optional
from datetime import datetime

class HourLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, hourlog: HourLog) -> HourLog:
        self.db.add(hourlog)
        self.db.commit()
        self.db.refresh(hourlog)
        return hourlog

    def get_pending(self) -> List[HourLog]:
        q = select(HourLog).where(HourLog.status == "pending").order_by(HourLog.submitted_at)
        return self.db.exec(q).all()

    def get_by_id(self, id: int) -> Optional[HourLog]:
        return self.db.get(HourLog, id)

    def update(self, hourlog: HourLog) -> HourLog:
        self.db.add(hourlog)
        self.db.commit()
        self.db.refresh(hourlog)
        return hourlog
