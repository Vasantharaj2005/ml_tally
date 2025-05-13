from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Enum, func
from sqlalchemy.orm import declarative_base
import enum
from datetime import datetime

Base = declarative_base()

# SQLAlchemy Enum class that matches the Pydantic Enum
class InvoiceStatus(enum.Enum):
    DRAFT = "draft"
    PAYMENT_PENDING = "payment_pending"
    PAYMENT_VALIDATED = "payment_validated"
    PAYMENT_NOT_CREDITED = "payment_not_credited"
    MONEY_NOT_YET_PROCESSED = "money_not_yet_processed"

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    buyer_details = Column(String, nullable=False)
    invoice_no = Column(String, unique=True, nullable=False)
    invoice_date = Column(Date, nullable=False)
    vehicle_number = Column(String, nullable=False)
    description = Column(String, nullable=False)
    hsn_sac = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    rate = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    amount_in_words = Column(String, nullable=False)
    gstin = Column(String, nullable=False)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())