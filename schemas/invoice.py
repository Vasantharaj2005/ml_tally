from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

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
    pass

class Invoice(InvoiceBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
