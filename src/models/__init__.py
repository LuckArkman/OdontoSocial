from src.models.base import Base, BaseModel
from src.models.tenant import Clinic, Tenant

# Facilita a importação em massa para o Alembic
__all__ = ["Base", "BaseModel", "Tenant", "Clinic"]
