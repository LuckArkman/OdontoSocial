import enum

from sqlalchemy import JSON, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class LeadStatus(str, enum.Enum):
    NEW = "novo"  # Lead acabou de entrar
    CONTACTED = "contatado"  # IA ou Humano já iniciou conversa
    QUALIFIED = "qualificado"  # Demonstrou interesse real
    SCHEDULED = "agendado"  # Marcou avaliação
    CONVERTED = "convertido"  # Comprou o cartão OdontoSocial
    LOST = "perdido"  # Recusou ou parou de responder


class Lead(BaseModel):
    """
    Entidade central de leads (prospectos) para o Agente IA.
    Contém os dados de contato e o estado no funil de vendas.
    """

    __tablename__ = "leads"

    name = Column(String(255), nullable=False)
    phone = Column(String(20), index=True, nullable=False)  # Formato E.164 recomendado
    email = Column(String(255), index=True, nullable=True)

    status = Column(Enum(LeadStatus), default=LeadStatus.NEW, nullable=False)
    origin = Column(String(100), default="manual")  # facebook, google, instagram, api

    # Campo para metadados flexíveis (ex: dados extras capturados pela IA)
    meta_data = Column(JSON, nullable=True)

    last_contact = Column(DateTime, nullable=True)

    # Isolamento de dados
    tenant_id = Column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tenant = relationship("Tenant")

    # Vínculo opcional com a clínica específica (se o tenant tiver múltiplas)
    clinic_id = Column(
        ForeignKey("clinics.id", ondelete="SET NULL"), nullable=True, index=True
    )
    clinic = relationship("Clinic")
