from contextvars import ContextVar
from typing import Optional

# Variável de contexto para armazenar o ID do Tenant durante a request
tenant_context: ContextVar[Optional[int]] = ContextVar("tenant_id", default=None)


def get_tenant_id() -> Optional[int]:
    return tenant_context.get()


def set_tenant_id(tenant_id: Optional[int]):
    tenant_context.set(tenant_id)
