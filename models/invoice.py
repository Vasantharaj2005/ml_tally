from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from sqlalchemy.sql import func
from database import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    buyer_details = Column(String)
    invoice_no = Column(String, unique=True, index=True)
    invoice_date = Column(Date)
    vehicle_number = Column(String)
    description = Column(String)
    hsn_sac = Column(String)
    quantity = Column(Float)
    unit = Column(String)
    rate = Column(Float)
    amount = Column(Float)
    amount_in_words = Column(String)
    gstin = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
