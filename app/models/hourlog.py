from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class ActivityBase(SQLModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: bool = True

class Activity(ActivityBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class HourLogBase(SQLModel):
    user_id: int = Field(foreign_key="user.id")
    activity_id: int = Field(foreign_key="activity.id")
    reviewed_by: Optional[int] = Field(default=None, foreign_key="user.id")
    hours: float
    proof_note: Optional[str] = None
    status: str = "pending"
    reject_reason: Optional[str] = None
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None

class HourLog(HourLogBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
