from typing import Optional

from pydantic import BaseModel, Field


class ClinicBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    cnpj: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None


class ClinicCreate(ClinicBase):
    pass


class ClinicRead(ClinicBase):
    id: int
    tenant_id: int

    class Config:
        from_attributes = True


class ClinicRegistration(BaseModel):
    """
    Schema composto para o fluxo de onboarding.
    Cria a Clínica e o Usuário Administrador de uma só vez.
    """

    clinic_name: str
    admin_email: str
    admin_password: str
    admin_full_name: Optional[str] = None
    cnpj: Optional[str] = None
