import os
import shutil
import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from src.api import deps
from src.db.session import get_db
from src.models.import_job import BulkImportJob, ImportStatus
from src.models.lead import Lead
from src.models.user import User
from src.schemas.lead import LeadCreate, LeadRead, LeadUpdate
from src.tasks.leads import process_bulk_import

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
    """
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
    Obtém detalhes de um lead específico.
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
    Atualiza dados de um lead.
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


@router.post("/import", status_code=status.HTTP_202_ACCEPTED)
async def import_leads_bulk(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_clinic_user),
    file: UploadFile = File(...),
) -> Any:
    """
    Inicia uma tarefa de importação massiva de leads a partir de um arquivo CSV ou Excel.
    """
    if not file.filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(
            status_code=400, detail="Formato inválido. Use CSV ou Excel."
        )

    # Criar Job
    job = BulkImportJob(
        tenant_id=current_user.tenant_id,
        status=ImportStatus.PENDING,
        filename=file.filename,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Salvar arquivo
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{uuid.uuid4()}_{file.filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    job.file_path = file_path
    db.add(job)
    db.commit()

    # Chamar Celery
    process_bulk_import.delay(job.id, file_path, current_user.tenant_id)

    return {
        "job_id": job.id,
        "message": "Importação iniciada.",
        "filename": file.filename,
    }


@router.get("/import-status/{job_id}")
def get_import_status(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_clinic_user),
) -> Any:
    """
    Consulta o estado de uma tarefa de importação.
    """
    job = (
        db.query(BulkImportJob)
        .filter(
            BulkImportJob.id == job_id,
            BulkImportJob.tenant_id == current_user.tenant_id,
        )
        .first()
    )

    if not job:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")

    return {
        "id": job.id,
        "status": job.status,
        "total": job.total_leads,
        "processed": job.processed_leads,
        "error": job.error_message,
    }
