from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.invoice import Invoice as InvoiceModel
from schemas.invoice import Invoice, InvoiceCreate
from typing import List
from sqlalchemy.exc import IntegrityError


router = APIRouter(prefix="/invoices", tags=["Invoices"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=Invoice)
def create_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db)):
    db_invoice = InvoiceModel(**invoice.dict())
    try:
        db.add(new_invoice)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invoice number already exists.")
    db.refresh(db_invoice)
    return db_invoice

@router.get("/", response_model=List[Invoice])
def get_all_invoices(db: Session = Depends(get_db)):
    return db.query(InvoiceModel).all()

@router.get("/{invoice_id}", response_model=Invoice)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(InvoiceModel).get(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.put("/{invoice_id}", response_model=Invoice)
def update_invoice(invoice_id: int, updated: InvoiceCreate, db: Session = Depends(get_db)):
    invoice = db.query(InvoiceModel).get(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    for key, value in updated.dict().items():
        setattr(invoice, key, value)
    db.commit()
    db.refresh(invoice)
    return invoice

@router.delete("/{invoice_id}")
def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(InvoiceModel).get(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    db.delete(invoice)
    db.commit()
    return {"detail": "Invoice deleted"}
