from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from database import get_db
from models.invoice import Invoice as InvoiceModel, InvoiceStatus
from schemas.invoice import Invoice, InvoiceCreate, InvoiceUpdate, InvoiceStatusEnum
from typing import List, Optional

router = APIRouter()

@router.post("/", response_model=Invoice)
async def create_invoice(invoice: InvoiceCreate, db: AsyncSession = Depends(get_db)):
    # Convert pydantic enum to SQLAlchemy enum if needed
    invoice_data = invoice.dict()
    if invoice_data.get("status"):
        invoice_data["status"] = InvoiceStatus[invoice_data["status"].name]
    
    db_invoice = InvoiceModel(**invoice_data)
    try:
        db.add(db_invoice)
        await db.commit()
        await db.refresh(db_invoice)
        return db_invoice
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Invoice number already exists.")

@router.get("/")
async def get_all_invoices(
    status: Optional[InvoiceStatusEnum] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(InvoiceModel)
    
    # Filter by status if provided
    if status:
        query = query.where(InvoiceModel.status == InvoiceStatus[status.name])
    
    result = await db.execute(query)
    invoices = result.scalars().all()
    return invoices

@router.get("/{invoice_id}")
async def get_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(InvoiceModel).where(InvoiceModel.id == invoice_id))
    invoice = result.scalars().first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.put("/{invoice_id}")
async def update_invoice(invoice_id: int, updated: InvoiceUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(InvoiceModel).where(InvoiceModel.id == invoice_id))
    invoice = result.scalars().first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    update_data = updated.dict(exclude_unset=True)
    
    # Convert status enum if present
    if "status" in update_data and update_data["status"]:
        update_data["status"] = InvoiceStatus[update_data["status"].name]
    
    for key, value in update_data.items():
        if value is not None:  # Only update fields that were actually provided
            setattr(invoice, key, value)
    
    try:
        await db.commit()
        await db.refresh(invoice)
        return invoice
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Invoice update failed.")

@router.patch("/{invoice_id}/status")
async def update_invoice_status(
    invoice_id: int, 
    status: InvoiceStatusEnum,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(InvoiceModel).where(InvoiceModel.id == invoice_id))
    invoice = result.scalars().first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Convert pydantic enum to SQLAlchemy enum
    invoice.status = InvoiceStatus[status.name]
    
    try:
        await db.commit()
        await db.refresh(invoice)
        return invoice
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Status update failed.")

@router.delete("/{invoice_id}")
async def delete_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(InvoiceModel).where(InvoiceModel.id == invoice_id))
    invoice = result.scalars().first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    await db.delete(invoice)
    await db.commit()
    return {"detail": "Invoice deleted"}