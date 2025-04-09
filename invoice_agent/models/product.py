"""
產品模型定義
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Product(BaseModel):
    """
    產品模型 - 對應產品清單中的每一筆資料
    """
    product_id: str  # 品號
    name: str  # 品名
    unit: str  # 單位
    currency: str  # 幣別
    price: float = 0.0  # 價格

class ProductMatchResult(BaseModel):
    """
    產品比對結果
    """
    product_id: str
    name: str
    unit: str
    currency: str
    price: float = 0.0  # 價格
    match_score: float  # 匹配分數 (0-1)
    original_input: str  # 原始輸入的產品名稱

class ProductsResponse(BaseModel):
    """
    所有產品響應
    """
    products: List[Product]
    total: int

class ProductCheckRequest(BaseModel):
    """
    產品檢查請求
    """
    product_name: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "product_name": "豬肉絲"
            }
        }
    }

class ProductCheckResponse(BaseModel):
    """
    產品檢查響應
    """
    exact_match: bool  # 是否有完全匹配
    matching_products: List[ProductMatchResult]  # 匹配的產品清單
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "exact_match": False,
                "matching_products": [
                    {
                        "product_id": "J009030",
                        "name": "豬肉絲",
                        "unit": "斤",
                        "currency": "NTD",
                        "price": 85.0,
                        "match_score": 1.0,
                        "original_input": "豬肉絲"
                    },
                    {
                        "product_id": "J009031",
                        "name": "豬柳",
                        "unit": "斤",
                        "currency": "NTD",
                        "price": 90.0,
                        "match_score": 0.6,
                        "original_input": "豬肉絲"
                    }
                ]
            }
        }
    }
