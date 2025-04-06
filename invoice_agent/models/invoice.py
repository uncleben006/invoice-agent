from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class OCRRequest(BaseModel):
    """
    OCR 請求模型
    """
    file_url: str
    file_type: Optional[str] = None  # 可選的文件類型，例如 "image/png" 或 "application/pdf"
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "file_url": "https://drive.google.com/uc?id=1wOyPl78VCiFkU-uIogrBNbAvAqzIKy_z&export=download",
                "file_type": "image/png"
            }
        }
    }

class OCRFileInfo(BaseModel):
    """
    OCR 批量請求的文件資訊
    """
    filename: str
    mimetype: str
    size: int
    link: str

class OCRBatchRequest(BaseModel):
    """
    OCR 批量請求模型
    """
    files: List[OCRFileInfo]
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "files": [
                    {
                        "filename": "訂單圖片1.png",
                        "mimetype": "image/png",
                        "size": 231729,
                        "link": "https://drive.google.com/uc?id=1wOyPl78VCiFkU-uIogrBNbAvAqzIKy_z&export=download"
                    }
                ]
            }
        }
    }

class OCRResponse(BaseModel):
    """
    OCR 響應模型
    """
    raw_text: str
    file_url: Optional[str]
    # 移除 LLM 相關欄位，OCR 純文字夠用

class OCRBatchResponse(BaseModel):
    """
    OCR 批量響應模型
    """
    results: List[Dict[str, Any]]
