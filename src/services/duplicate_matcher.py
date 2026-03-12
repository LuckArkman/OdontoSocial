from sqlalchemy.orm import Session
from src.models.lead import Lead
from typing import Optional

class DuplicateMatcher:
    """
    Serviço para detecção de leads duplicados dentro do mesmo Tenant.
    """
    
    @staticmethod
    def find_existing_lead(db: Session, tenant_id: int, phone: str, email: Optional[str] = None) -> Optional[Lead]:
        """
        Verifica se já existe um lead com o mesmo telefone ou e-mail no Tenant.
        A prioridade de busca é o telefone (identificador principal no WhatsApp).
        """
        # 1. Buscar por telefone no tenant
        query = db.query(Lead).filter(
            Lead.tenant_id == tenant_id,
            Lead.phone == phone
        )
        existing = query.first()
        
        if existing:
            return existing
            
        # 2. Buscar por e-mail no tenant (se fornecido)
        if email:
            query = db.query(Lead).filter(
                Lead.tenant_id == tenant_id,
                Lead.email == email
            )
            existing = query.first()
            if existing:
                return existing
                
        return None

    @staticmethod
    def is_duplicate(db: Session, tenant_id: int, phone: str, email: Optional[str] = None) -> bool:
        """Retorna True se o lead já existir."""
        return DuplicateMatcher.find_existing_lead(db, tenant_id, phone, email) is not None
