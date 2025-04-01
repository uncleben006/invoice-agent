from typing import List, Optional
from invoice_agent.models.invoice import Invoice, InvoiceCreate

class InvoiceService:
    """
    發票服務層示例
    實際應用中應與資料庫交互
    """
    
    async def get_invoices(self) -> List[Invoice]:
        """
        獲取所有發票
        """
        # 此為示例，實際應用應從資料庫獲取
        return [
            Invoice(
                id=1, 
                number="AB-12345678", 
                date="2025-04-01", 
                amount=1000
            ),
            Invoice(
                id=2, 
                number="AB-87654321", 
                date="2025-03-25", 
                amount=500
            )
        ]
    
    async def get_invoice_by_id(self, invoice_id: int) -> Optional[Invoice]:
        """
        通過 ID 獲取特定發票
        """
        # 此為示例，實際應用應從資料庫查詢
        if invoice_id <= 0:
            return None
            
        return Invoice(
            id=invoice_id,
            number=f"AB-{10000000 + invoice_id}",
            date="2025-04-01",
            amount=1000
        )
    
    async def create_invoice(self, invoice_data: InvoiceCreate) -> Invoice:
        """
        創建新發票
        """
        # 實際應用中應儲存到資料庫並返回儲存的實體
        # 此處僅為示例
        return Invoice(
            id=999,  # 假設 ID
            number=invoice_data.number,
            date=invoice_data.date,
            amount=sum(item.get_total() for item in invoice_data.items),
            items=invoice_data.items
        )

# 服務單例
invoice_service = InvoiceService()
