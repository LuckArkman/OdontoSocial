import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, String

from src.models.base import BaseModel


class ImportStatus(str, enum.Enum):
    PENDING = "pendente"
    PROCESSING = "processando"
    COMPLETED = "concluido"
    FAILED = "falhou"


class BulkImportJob(BaseModel):
    """
    Entidade para rastreamento de tarefas de importação massiva de leads.
    """

    __tablename__ = "bulk_import_jobs"

    tenant_id = Column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status = Column(Enum(ImportStatus), default=ImportStatus.PENDING, nullable=False)

    total_leads = Column(Integer, default=0)
    processed_leads = Column(Integer, default=0)

    filename = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)
    error_message = Column(String(500), nullable=True)
