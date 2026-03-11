import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.orm import Session

from src.core import security
from src.core.config import settings
from src.core.middlewares.tenant_context import set_tenant_id
from src.db.session import get_db
from src.models.user import User
from src.schemas.token import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    """
    Valida o token JWT e retorna o usuário atual.
    Também injeta o tenant_id no contexto para garantir o isolamento.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não foi possível validar as credenciais",
        )

    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Usuário inativo")

    # Importante: Seta o tenant_id no contexto a partir do Token (confiável)
    # Isso sobrescreve qualquer valor vindo de headers (segurança)
    if user.tenant_id:
        set_tenant_id(user.tenant_id)

    return user


class RoleChecker:
    """
    Guardião de permissões baseado em superuser ou presença de tenant.
    """

    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.is_superuser:
            return True

        if user.role in self.allowed_roles:
            return True

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar este recurso",
        )


# Instâncias comuns de permissão
get_current_active_superuser = RoleChecker(["superuser"])
get_current_clinic_owner = RoleChecker(["dono"])
get_current_clinic_user = RoleChecker(["dono", "atendente"])
