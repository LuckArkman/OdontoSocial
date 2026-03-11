from fastapi import APIRouter

from src.api.v1.endpoints import auth, clinics, tenants

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["Tenants"])
api_router.include_router(clinics.router, prefix="/clinics", tags=["Clinics"])
