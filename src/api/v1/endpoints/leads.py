from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api import deps
from src.db.session import get_db
from src.models.lead import Lead
from src.models.user import User
from src.schemas.lead import LeadCreate, LeadRead, LeadUpdate

router = APIRouter()


@router.get("/", response_model=List[LeadRead])
def list_leads(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_clinic_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Lista os leads associados ao Tenant do usuário atual.
    O isolamento é garantido pelo TenantMiddleware e deps.get_current_clinic_user.
    """
    # Nota: Em uma implementação completa de RLS, o filtro tenant_id seria implícito.
    # Aqui, reforçamos via código para segurança redundante.
    leads = (
        db.query(Lead)
        .filter(Lead.tenant_id == current_user.tenant_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return leads


@router.post("/", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
def create_lead(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_clinic_user),
    lead_in: LeadCreate,
) -> Any:
    """
    Cria um novo lead vinculado ao Tenant logado.
    """
    db_lead = Lead(**lead_in.model_dump(), tenant_id=current_user.tenant_id)
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead


@router.get("/{lead_id}", response_model=LeadRead)
def read_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_clinic_user),
) -> Any:
    """
    Obtém detalhes de um lead específico, validando o acesso ao tenant.
    """
    lead = (
        db.query(Lead)
        .filter(Lead.id == lead_id, Lead.tenant_id == current_user.tenant_id)
        .first()
    )

    if not lead:
        raise HTTPException(
            status_code=404, detail="Lead não encontrado ou acesso negado"
        )
    return lead


@router.patch("/{lead_id}", response_model=LeadRead)
def update_lead(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_clinic_user),
    lead_id: int,
    lead_in: LeadUpdate,
) -> Any:
    """
    Atualiza dados de um lead (status, nome, etc).
    """
    db_lead = (
        db.query(Lead)
        .filter(Lead.id == lead_id, Lead.tenant_id == current_user.tenant_id)
        .first()
    )

    if not db_lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    update_data = lead_in.model_dump(exclude_unset=True)
    for field in update_data:
        setattr(db_lead, field, update_data[field])

    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead
