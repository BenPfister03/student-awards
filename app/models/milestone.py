from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone


class Milestone(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    hours_threshold: float
    badge_label: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserMilestone(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    milestone_id: int = Field(foreign_key="milestone.id")
    unlocked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
