from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional
from enum import Enum

class InvoiceStatusEnum(str, Enum):
    DRAFT = "draft"
    PAYMENT_PENDING = "payment_pending"
    PAYMENT_VALIDATED = "payment_validated"
    PAYMENT_NOT_CREDITED = "payment_not_credited"
    MONEY_NOT_YET_PROCESSED = "money_not_yet_processed"

class InvoiceBase(BaseModel):
    company_name: str
    buyer_details: str
    invoice_no: str
    invoice_date: date
    vehicle_number: str
    description: str
    hsn_sac: str
    quantity: float
    unit: str
    rate: float
    amount: float
    amount_in_words: str
    gstin: str

class InvoiceCreate(InvoiceBase):
    status: Optional[InvoiceStatusEnum] = InvoiceStatusEnum.DRAFT

class InvoiceUpdate(BaseModel):
    company_name: Optional[str] = None
    buyer_details: Optional[str] = None
    invoice_no: Optional[str] = None
    invoice_date: Optional[date] = None
    vehicle_number: Optional[str] = None
    description: Optional[str] = None
    hsn_sac: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    rate: Optional[float] = None
    amount: Optional[float] = None
    amount_in_words: Optional[str] = None
    gstin: Optional[str] = None
    status: Optional[InvoiceStatusEnum] = None

class Invoice(InvoiceBase):
    id: int
    status: InvoiceStatusEnum
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None
        }
    )
    invoice_no: Optional[str] = None
    invoice_date: Optional[date] = None
    vehicle_number: Optional[str] = None
    description: Optional[str] = None
    hsn_sac: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    rate: Optional[float] = None
    amount: Optional[float] = None
    amount_in_words: Optional[str] = None
    gstin: Optional[str] = None
    status: Optional[InvoiceStatusEnum] = None

class Invoice(InvoiceBase):
    id: int
    status: InvoiceStatusEnum
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }