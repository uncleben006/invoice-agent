from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime

class InvoiceItem(BaseModel):
    """
    發票項目模型
    """
    name: str
    quantity: int
    price: float
    
    def get_total(self) -> float:
        """計算項目總價"""
        return self.quantity * self.price

class Invoice(BaseModel):
    """
    發票模型
    """
    id: Optional[int] = None
    number: str
    date: date
    amount: float
    items: Optional[List[InvoiceItem]] = None

class InvoiceCreate(BaseModel):
    """
    創建發票的請求模型
    """
    number: str
    date: date
    items: List[InvoiceItem]
