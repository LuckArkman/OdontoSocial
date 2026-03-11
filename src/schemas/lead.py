from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field

from src.models.lead import LeadStatus


class LeadBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    phone: str = Field(..., description="Telefone no formato E.164")
    email: Optional[EmailStr] = None
    origin: Optional[str] = "manual"
    meta_data: Optional[dict[str, Any]] = None


class LeadCreate(LeadBase):
    clinic_id: Optional[int] = None


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[LeadStatus] = None
    email: Optional[EmailStr] = None
    meta_data: Optional[dict[str, Any]] = None


class LeadRead(LeadBase):
    id: int
    status: LeadStatus
    tenant_id: int
    clinic_id: Optional[int] = None
    created_at: datetime
    last_contact: Optional[datetime] = None

    class Config:
        from_attributes = True
