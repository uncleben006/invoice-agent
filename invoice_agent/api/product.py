"""
產品相關 API 路由
"""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from invoice_agent.models.product import ProductsResponse, ProductCheckRequest, ProductCheckResponse
from invoice_agent.services.product_service import product_service
from invoice_agent.core.logging import logger

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", response_model=ProductsResponse)
async def get_all_products():
    """
    獲取所有產品清單
    
    Returns:
        ProductsResponse: 包含所有產品的清單
    """
    try:
        # 載入並獲取所有產品
        products = await product_service.get_all_products()
        return ProductsResponse(products=products, total=len(products))
        
    except Exception as e:
        logger.error(f"獲取產品清單時發生錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取產品清單時發生錯誤: {str(e)}")

@router.post("/check", response_model=ProductCheckResponse)
async def check_product(
    request: ProductCheckRequest,
    max_results: int = Query(5, description="最大返回結果數", ge=1, le=20),
    threshold: float = Query(0.4, description="最小相似度閾值 (0-1)", ge=0, le=1)
):
    """
    檢查產品是否存在，若不存在則返回最接近的產品
    
    Args:
        request: 包含要檢查的產品名稱
        max_results: 返回最大的結果數量 (默認 5)
        threshold: 最小相似度閾值 (0-1) (默認 0.4)
        
    Returns:
        ProductCheckResponse: 包含匹配結果的響應
    """
    try:
        # 檢查產品是否存在
        exact_match, matching_products = await product_service.check_product(
            request.product_name, 
            max_results=max_results,
            threshold=threshold
        )
        
        return ProductCheckResponse(
            exact_match=exact_match,
            matching_products=matching_products
        )
        
    except Exception as e:
        logger.error(f"檢查產品時發生錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=f"檢查產品時發生錯誤: {str(e)}")
