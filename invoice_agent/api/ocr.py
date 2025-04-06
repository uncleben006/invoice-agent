"""
OCR 相關 API 路由
"""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from invoice_agent.models.invoice import OCRRequest, OCRBatchRequest, OCRBatchResponse
from invoice_agent.services.ocr_service import ocr_service
from invoice_agent.core.logging import logger

router = APIRouter(prefix="/ocr", tags=["OCR"])

@router.post("/text")
async def extract_text_only(request: OCRRequest):
    """
    從單一 URL 提取文字及相關詳細資訊

    此端點接收 URL（通常為 Google Drive）和檔案類型，使用 OCR 提取文本和位置信息
    
    返回：
        - 對於圖像文件：完整文本、區塊信息（包含文本、位置座標和置信度）
        - 對於 PDF 文件：僅返回提取的文本
    """
    try:
        # 使用 OCR 服務處理圖像，傳入檔案類型（如果提供）
        result = await ocr_service.extract_text(request.image_url, file_type=request.file_type)
        
        # 直接返回結果（包含文本和區塊信息）
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"處理圖像時出錯: {str(e)}")

@router.post("/batch", response_model=OCRBatchResponse)
async def extract_batch_text(request: OCRBatchRequest):
    """
    批量處理多個文件，提取文字

    此端點接收多個文件的資訊（包含文件名、MIME類型、大小和連結），使用 OCR 提取文本
    """
    try:
        # 從請求中提取文件資訊列表
        files = [file.dict() for file in request.files]
        
        # 批量處理所有文件
        results = await ocr_service.extract_batch_text(files)
        
        # 返回處理結果
        return OCRBatchResponse(results=results)
        
    except Exception as e:
        logger.error(f"批量處理文件時出錯: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量處理文件時出錯: {str(e)}")
