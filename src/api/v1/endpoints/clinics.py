import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core import security
from src.db.session import get_db
from src.models.tenant import Clinic, Tenant
from src.models.user import User
from src.schemas.clinic import ClinicRead, ClinicRegistration

router = APIRouter()


def slugify(text: str) -> str:
    return re.sub(r"[\W_]+", "-", text.lower()).strip("-")


@router.post(
    "/register", response_model=ClinicRead, status_code=status.HTTP_201_CREATED
)
def register_clinic(*, db: Session = Depends(get_db), registration: ClinicRegistration):
    """
    Fluxo de Onboarding:
    1. Cria um Tenant único a partir do nome da clínica.
    2. Cria a Clínica vinculada ao Tenant.
    3. Cria o primeiro Usuário Administrador vinculado ao Tenant.
    """
    # 1. Verificar se usuário já existe
    user_exists = db.query(User).filter(User.email == registration.admin_email).first()
    if user_exists:
        raise HTTPException(
            status_code=400, detail="Este e-mail já está cadastrado no sistema."
        )

    # 2. Criar Tenant
    tenant_slug = slugify(registration.clinic_name)
    # Garantir unicidade simples do slug (apenas para MVP)
    existing_tenant = db.query(Tenant).filter(Tenant.slug == tenant_slug).first()
    if existing_tenant:
        tenant_slug = (
            f"{tenant_slug}-{security.pwd_context.hash(registration.admin_email)[:5]}"
        )

    new_tenant = Tenant(name=registration.clinic_name, slug=tenant_slug)
    db.add(new_tenant)
    db.flush()  # Para obter o ID do tenant

    # 3. Criar Clínica
    new_clinic = Clinic(
        name=registration.clinic_name, cnpj=registration.cnpj, tenant_id=new_tenant.id
    )
    db.add(new_clinic)

    # 4. Criar Usuário Admin
    new_admin = User(
        email=registration.admin_email,
        hashed_password=security.get_password_hash(registration.admin_password),
        full_name=registration.admin_full_name,
        tenant_id=new_tenant.id,
        is_active=True,
        is_superuser=False,  # Admins de clínica não são superusers globais
    )
    db.add(new_admin)

    try:
        db.commit()
        db.refresh(new_clinic)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar registro: {str(e)}"
        )

    return new_clinic
