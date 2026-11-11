"""Database table models.

Import every table model here so ``SQLModel.metadata.create_all`` sees them.
"""

from app.models.user import User
from app.models.hourlog import Activity, HourLog
from app.models.milestone import Milestone, UserMilestone
from app.models.prize import Prize, Redemption

__all__ = ["User", "Activity", "HourLog", "Milestone", "UserMilestone", "Prize", "Redemption"]
