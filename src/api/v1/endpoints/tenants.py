from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api import deps
from src.core.middlewares.tenant_context import get_tenant_id
from src.db.session import get_db
from src.models.tenant import Tenant

router = APIRouter()


@router.get("/")
def list_tenants(
    db: Session = Depends(get_db), _=Depends(deps.get_current_active_superuser)
):
    """
    Lista todos os tenants. Restrito a SuperAdmins globais.
    """
    tenants = db.query(Tenant).all()
    return tenants


@router.post("/")
def create_tenant(name: str, slug: str, db: Session = Depends(get_db)):
    """
    Cria um novo tenant.
    """
    db_tenant = Tenant(name=name, slug=slug)
    db.add(db_tenant)
    try:
        db.commit()
        db.refresh(db_tenant)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_tenant


@router.get("/current/debug")
def get_current_tenant_debug():
    """
    Retorna o ID do Tenant detectado no contexto atual (vindo do header X-Tenant-ID).
    """
    return {"tenant_id_context": get_tenant_id()}
