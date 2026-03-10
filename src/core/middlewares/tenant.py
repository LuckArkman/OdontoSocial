from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.middlewares.tenant_context import set_tenant_id

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """
        Middleware que extrai o ID do Tenant dos headers da requisição.
        No futuro, isso pode ser extraído do JWT ou subdomínio.
        """
        tenant_id_str = request.headers.get("X-Tenant-ID")
        
        if tenant_id_str and tenant_id_str.isdigit():
            set_tenant_id(int(tenant_id_str))
        else:
            set_tenant_id(None)
            
        response: Response = await call_next(request)
        return response
