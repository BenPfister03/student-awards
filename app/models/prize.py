from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Prize(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    hours_cost: float
    stock: int = 0
    is_active: bool = True


class Redemption(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    prize_id: int = Field(foreign_key="prize.id")
    hours_cost: float
    status: str = "requested"
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    fulfilled_by: Optional[int] = Field(default=None, foreign_key="user.id")
    fulfilled_at: Optional[datetime] = None
