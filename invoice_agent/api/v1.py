from fastapi import APIRouter, HTTPException, Depends, status
from typing import List

from invoice_agent.models.invoice import Invoice, InvoiceCreate
from invoice_agent.services.invoice_service import invoice_service

router = APIRouter(prefix="/api/v1", tags=["v1"])

@router.get("/invoices", response_model=List[Invoice])
async def get_invoices():
    """
    獲取發票列表
    """
    return await invoice_service.get_invoices()

@router.get("/invoices/{invoice_id}", response_model=Invoice)
async def get_invoice(invoice_id: int):
    """
    獲取特定發票詳情
    """
    invoice = await invoice_service.get_invoice_by_id(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="發票不存在")
    return invoice

@router.post("/invoices", response_model=Invoice, status_code=status.HTTP_201_CREATED)
async def create_invoice(invoice_data: InvoiceCreate):
    """
    創建新發票
    """
    return await invoice_service.create_invoice(invoice_data)
