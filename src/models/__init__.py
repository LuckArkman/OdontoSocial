from src.models.base import Base, BaseModel
from src.models.tenant import Clinic, Tenant
from src.models.user import User

# Facilita a importação em massa para o Alembic
__all__ = ["Base", "BaseModel", "Tenant", "Clinic", "User"]
