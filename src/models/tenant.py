from sqlalchemy import Boolean, Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class Tenant(BaseModel):
    """
    Entidade de Tenant para isolamento lógico.
    Cada Tenant representa uma conta de faturamento ou organização pai.
    """

    __tablename__ = "tenants"

    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)

    clinics = relationship(
        "Clinic", back_populates="tenant", cascade="all, delete-orphan"
    )


class Clinic(BaseModel):
    """
    Entidade Clinic (Unidade Odontológica).
    Pertence a um Tenant. É onde os leads são processados.
    """

    __tablename__ = "clinics"

    name = Column(String(255), nullable=False)
    cnpj = Column(String(18), unique=True, index=True, nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)

    tenant_id = Column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tenant = relationship("Tenant", back_populates="clinics")

    # Campo para suporte a Row-Level Security (RLS) se necessário no futuro
    # Por ora, garantimos o isolamento via tenant_id em todas as tabelas de negócio.
