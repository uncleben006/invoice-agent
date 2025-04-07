"""
產品服務 - 負責產品查詢和比對
"""
import os
import csv
import asyncio
from typing import List, Dict, Any, Tuple
from rapidfuzz import fuzz
from invoice_agent.models.product import Product, ProductMatchResult
from invoice_agent.core.logging import logger

class ProductService:
    """處理產品資料和比對相關功能"""
    
    def __init__(self):
        self.products: List[Product] = []
        self.products_dict: Dict[str, Product] = {}  # 以產品 ID 為鍵的字典
        self.products_name_dict: Dict[str, Product] = {}  # 以產品名稱為鍵的字典
        self.products_loaded = False
        # 使用相對路徑，使其在任何環境中都能正常工作
        # 在容器內會是 /app/products_list.csv，在本地會是 products_list.csv
        self.products_file_path = os.path.join(os.getcwd(), "products_list.csv")
    
    async def load_products(self) -> bool:
        """
        載入產品資料
        
        Returns:
            bool: 是否成功載入產品資料
        """
        try:
            logger.info(f"開始載入產品資料：{self.products_file_path}")
            
            if not os.path.exists(self.products_file_path):
                logger.error(f"產品資料檔案不存在：{self.products_file_path}")
                return False
            
            # 清空產品資料
            self.products = []
            self.products_dict = {}
            self.products_name_dict = {}
            
            # 讀取 CSV 檔案
            with open(self.products_file_path, 'r', encoding='utf-8-sig') as file:
                reader = csv.reader(file)
                # 跳過標題行
                headers = next(reader)
                
                # 檢查標題行格式是否正確
                if len(headers) < 4 or '品號' not in headers[0] or '品名' not in headers[1]:
                    logger.error(f"產品資料檔案格式不正確，標題行：{headers}")
                    return False
                
                # 讀取產品資料
                for row in reader:
                    if len(row) >= 4:
                        product = Product(
                            product_id=row[0],
                            name=row[1],
                            unit=row[2],
                            currency=row[3]
                        )
                        
                        self.products.append(product)
                        self.products_dict[product.product_id] = product
                        self.products_name_dict[product.name] = product
            
            logger.info(f"成功載入 {len(self.products)} 筆產品資料")
            self.products_loaded = True
            return True
            
        except Exception as e:
            logger.error(f"載入產品資料時發生錯誤：{str(e)}")
            return False
    
    async def get_all_products(self) -> List[Product]:
        """
        獲取所有產品
        
        Returns:
            List[Product]: 所有產品清單
        """
        if not self.products_loaded:
            await self.load_products()
        
        return self.products
    
    async def check_product(self, product_name: str, max_results: int = 5, threshold: float = 0.4) -> Tuple[bool, List[ProductMatchResult]]:
        """
        檢查產品是否存在，若不存在則返回最接近的產品
        
        Args:
            product_name: 要檢查的產品名稱
            max_results: 返回最大的結果數量
            threshold: 最小相似度閾值 (0-1)
            
        Returns:
            Tuple[bool, List[ProductMatchResult]]: 
                - 是否有完全匹配
                - 匹配的產品清單
        """
        if not self.products_loaded:
            await self.load_products()
        
        # 如果產品名稱為空，返回空結果
        if not product_name or not product_name.strip():
            return False, []
        
        # 標準化產品名稱 (去除空白)
        normalized_name = product_name.strip()
        
        # 檢查是否有完全匹配
        exact_match = False
        result_products = []
        
        # 如果有完全匹配，直接返回
        if normalized_name in self.products_name_dict:
            product = self.products_name_dict[normalized_name]
            result_products.append(
                ProductMatchResult(
                    product_id=product.product_id,
                    name=product.name,
                    unit=product.unit,
                    currency=product.currency,
                    match_score=1.0,
                    original_input=product_name
                )
            )
            exact_match = True
            
            # 如果只要求精確匹配，則直接返回
            if max_results == 1:
                return exact_match, result_products
        
        # 計算所有產品與輸入產品名稱的編輯距離，並按相似度排序
        match_scores = []
        
        for product in self.products:
            # 使用 rapidfuzz 計算相似度
            # 比較多種相似度計算方法，並取最高分
            ratio_score = fuzz.ratio(normalized_name, product.name) / 100.0
            partial_ratio_score = fuzz.partial_ratio(normalized_name, product.name) / 100.0
            token_sort_ratio_score = fuzz.token_sort_ratio(normalized_name, product.name) / 100.0
            
            # 取最高分作為最終相似度
            similarity = max(ratio_score, partial_ratio_score, token_sort_ratio_score)
            
            # 只保留相似度超過閾值的結果
            if similarity >= threshold:
                match_scores.append((product, similarity))
        
        # 根據相似度排序 (由高到低)
        match_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 轉換為結果格式
        for product, score in match_scores[:max_results]:
            # 避免重複添加完全匹配的產品
            if exact_match and product.name == normalized_name:
                continue
                
            result_products.append(
                ProductMatchResult(
                    product_id=product.product_id,
                    name=product.name,
                    unit=product.unit,
                    currency=product.currency,
                    match_score=score,
                    original_input=product_name
                )
            )
        
        return exact_match, result_products

# 創建單例
product_service = ProductService()
