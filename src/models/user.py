from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class User(BaseModel):
    """
    Entidade de Usuário do sistema OdontoSocial.
    Pode ser um SuperAdmin (sem tenant_id) ou um usuário de clínica.
    """

    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)

    # Usuários vinculados a um tenant (clínica)
    tenant_id = Column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    tenant = relationship("Tenant")
