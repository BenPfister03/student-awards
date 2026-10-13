from sqlmodel import Field, SQLModel
from typing import Optional
from pydantic import EmailStr


class UserBase(SQLModel,):
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    password: str
    role: str = ""
    total_hours: float = Field(default=0.0)
    points_spent: float = Field(default=0.0)

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)