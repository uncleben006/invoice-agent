"""
OCR 服務 - 負責圖像文字識別
"""
# 標準庫
import io
import os
import json
import tempfile
from typing import Dict, Any, Optional, Tuple, List

# 第三方庫
import requests
import pypdf as PyPDF2  # 使用 pypdf 但命名為 PyPDF2 以維持代碼兼容性
from pdf2image import convert_from_path
from PIL import Image
from google.cloud import vision
from google.oauth2 import service_account

# 內部模組
from invoice_agent.core.logging import logger

class OCRService:
    """處理圖像 OCR 相關功能"""
    
    def __init__(self):
        # 從配置中獲取 Google Vision API 憑證路徑
        from invoice_agent.core.config import settings
        self.vision_credentials_path = settings.GOOGLE_VISION_CREDENTIALS_PATH
    
    async def extract_text(self, file_url: str, file_type: str) -> Dict[str, Any]:
        """
        從 URL 獲取圖像並處理 OCR
        
        Args:
            file_url: 圖像的 URL (Google Drive)
            file_type: 檔案類型 (image/png, application/pdf 等)
            
        Returns:
            Dict[str, Any]: 包含識別出的文字和圖像 URL 的字典
        """
        try:
            logger.info(f"===================== 開始處理新的 URL =====================")
            logger.info(f"處理 URL: {file_url}")
            
            # 下載檔案
            content = await self.download_file(file_url)
            
            # 根據檔案類型處理
            if file_type.startswith('image/'):
                # 影像檔案，直接使用 Google Vision API
                logger.info("處理為圖像文件，使用 Google Vision API")
                result = await self.process_image_with_vision(content)
                # 添加圖像 URL 到結果
                result["file_url"] = file_url
                # 返回完整結果而不只是文本
                return result
                
            elif file_type == 'application/pdf':
                # PDF 檔案處理 - 首先檢查是否有文本層，然後決定是否使用 OCR
                logger.info("處理為 PDF 文件")
                text_result = await self.process_pdf(content)
                # 對於 PDF，仍然返回結構化結果，包含 file_url
                return {"text": text_result, "paragraphs": [], "file_url": file_url}
            else:
                # 默認作為圖像處理，也使用 Google Vision API
                logger.warning(f"未知檔案類型: {file_type}，默認作為圖像處理，使用 Google Vision API")
                result = await self.process_image_with_vision(content)
                # 添加圖像 URL 到結果
                result["file_url"] = file_url
                return result
            
        except Exception as e:
            logger.error(f"處理 URL 圖像時發生錯誤: {e}")
            # 返回一些錯誤資訊，以便於調試
            return f"處理錯誤: {str(e)}"
    
    async def download_file(self, url: str) -> bytes:
        """
        從 URL 下載檔案
        
        Args:
            url: 檔案的 URL (Google Drive)
            
        Returns:
            bytes: 檔案的二進制內容
        """
        try:
            logger.info(f"從 URL 下載檔案: {url}")
            
            # 直接嘗試下載
            response = requests.get(url, stream=True, timeout=15)
            response.raise_for_status()  # 確保請求成功
            
            logger.info(f"下載成功，檔案大小約: {len(response.content) / 1024:.2f} KB")
            return response.content
                
        except Exception as e:
            logger.error(f"下載檔案失敗: {e}")
            raise ValueError(f"無法從 URL 下載檔案: {str(e)}")

    # process_image 函數已移除，我們現在只使用 process_image_with_vision 進行 OCR
    
    async def process_pdf(self, pdf_data: bytes) -> str:
        """
        處理 PDF 檔案，優先檢查是否所有頁面都有文本層
        只有當所有頁面都有文本層時（all_pages_have_text=True），才直接提取文本
        如果有任何一頁不包含文本層，則使用 OCR 方式處理整個 PDF
        
        Args:
            pdf_data: PDF 的二進制數據
            
        Returns:
            str: 識別出的文字
        """
        temp_path = None
        try:
            logger.info("開始處理 PDF，首先檢查是否有文本層...")
            
            # 使用臨時文件存儲 PDF
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as pdf_file:
                pdf_file.write(pdf_data)
                pdf_path = pdf_file.name
                temp_path = pdf_path
                logger.info(f"PDF 已保存到臨時文件: {pdf_path}")
            
            # 嘗試從 PDF 直接提取文本
            extracted_text_pages, all_pages_have_text = await self._extract_text_from_pdf(pdf_path)
            
            # 如果所有頁面都有文本，直接返回
            if all_pages_have_text:
                logger.info("PDF 所有頁面都有文本層，直接返回提取的文本")
                return "\n\n".join(extracted_text_pages)
            
            # 如果不是所有頁面都有文本，使用 OCR 處理
            logger.info("PDF 不是所有頁面都有文本層，使用 OCR 處理...")
            return await self._process_pdf_with_ocr(pdf_path)
                
        except Exception as e:
            logger.error(f"處理 PDF 時發生錯誤: {e}")
            # 返回錯誤資訊
            return f"處理 PDF 時出錯: {str(e)}"
        finally:
            # 清理臨時文件
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                    logger.info(f"臨時文件已刪除: {temp_path}")
                except Exception as e:
                    logger.error(f"刪除臨時文件時出錯: {e}")

    async def _extract_text_from_pdf(self, pdf_path: str) -> Tuple[List[str], bool]:
        """
        嘗試使用 PyPDF2 直接從 PDF 提取文本層
        判斷邏輯：只有當所有頁面都有文本時，才認為整篇 PDF 都是文本格式
        
        Args:
            pdf_path: PDF 檔案的路徑
            
        Returns:
            Tuple[List[str], bool]: 
                - 提取的文本頁面列表
                - 是否所有頁面都有文本（all_pages_have_text）
        """
        try:
            logger.info("嘗試直接從 PDF 提取文本...")
            with open(pdf_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                
                # 檢查 PDF 是否有文本層
                extracted_text_pages = []
                for i, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text and len(page_text.strip()) > 50:  # 有足夠的文字
                        extracted_text_pages.append(page_text)
                        logger.info(f"從 PDF 第 {i+1} 頁成功提取文本，長度: {len(page_text)}")
                    else:
                        logger.info(f"PDF 第 {i+1} 頁沒有足夠的文本，將需要 OCR")
                
                # 判斷是否所有頁面都有文本層
                all_pages_have_text = (
                    extracted_text_pages and 
                    len(extracted_text_pages) == len(pdf_reader.pages)  # 確保所有頁面都有文本
                )
                
                if all_pages_have_text:
                    logger.info(f"成功從 PDF 所有頁面直接提取文本，共 {len(extracted_text_pages)} 頁")
                else:
                    missing_pages = len(pdf_reader.pages) - len(extracted_text_pages)
                    logger.info(f"PDF 有 {missing_pages}/{len(pdf_reader.pages)} 頁沒有足夠的文本層，將使用 OCR 處理整個文檔")
                
                return extracted_text_pages, all_pages_have_text
                
        except Exception as extract_error:
            logger.warning(f"直接從 PDF 提取文本失敗: {extract_error}")
            return [], False
    
    async def _process_pdf_with_ocr(self, pdf_path: str) -> str:
        """
        使用 Google Vision API 處理 PDF 文件，將其轉換為文字
        
        Args:
            pdf_path: PDF 檔案的路徑
            
        Returns:
            str: OCR 識別出的文字
        """
        # 使用 pdf2image 將 PDF 轉換為高質量圖像
        logger.info("使用 Google Vision API 處理 PDF...")
        
        # 轉換 PDF 頁面為圖像
        images = convert_from_path(
            pdf_path, 
            dpi=400,  # 高解析度
            use_pdftocairo=True,
            first_page=1,
            last_page=5,  # 處理前5頁
            grayscale=False,  # 保留彩色信息
            transparent=False
        )
        logger.info(f"PDF 成功轉換為 {len(images)} 個高質量圖像")
        
        # 對每個頁面進行 OCR 處理
        all_text = []
        for i, img in enumerate(images):
            logger.info(f"處理 PDF 第 {i+1} 頁...")
            
            # 將圖像轉換為二進制
            with io.BytesIO() as img_binary:
                img.save(img_binary, format='PNG', quality=100)  # 使用最高質量
                img_binary.seek(0)
                image_data = img_binary.read()
            
            # 使用 Google Vision API
            try:
                result = await self.process_image_with_vision(image_data)
                page_text = result.get("text", "")
                if page_text and len(page_text.strip()) > 50:  # 確保提取到有意義的文本
                    all_text.append(page_text)
                    logger.info(f"第 {i+1} 頁 Vision OCR 完成，文本長度: {len(page_text)}")
                else:
                    logger.warning(f"第 {i+1} 頁 Vision OCR 提取文本不足")
            except Exception as vision_error:
                logger.error(f"使用 Vision API 處理第 {i+1} 頁時出錯: {vision_error}")
        
        # 合併所有頁面的文本
        if all_text:
            result = "\n\n".join(all_text)
            logger.info(f"PDF OCR 處理完成，總文本長度: {len(result)}")
            return result
        else:
            return "無法從 PDF 提取有效文本，請嘗試上傳更清晰的檔案或轉換為圖像格式。"

    async def process_image_with_vision(self, image_data: bytes) -> Dict[str, Any]:
        """
        使用 Google Vision API 處理圖像進行 OCR
        
        Args:
            image_data: 圖像的二進制數據
            
        Returns:
            Dict[str, Any]: 包含文字和詳細信息的字典，結構:
            {
                "text": "識別的完整文字",
                "width": 圖像寬度,
                "height": 圖像高度,
                "blocks": [
                    {
                        "text": "區塊文字",
                        "bounding_box": {
                            "vertices": [
                                {"x": x1, "y": y1},
                                {"x": x2, "y": y2},
                                {"x": x3, "y": y3},
                                {"x": x4, "y": y4}
                            ]
                        },
                        "confidence": 置信度
                    },
                    ...
                ]
            }
        """
        try:
            logger.info("使用 Google Vision API 進行 OCR 處理...")
            
            # 使用來自配置的憑證路徑
            credentials_path = self.vision_credentials_path

            # 使用服務帳戶憑證
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            client = vision.ImageAnnotatorClient(credentials=credentials)
            logger.info("成功使用憑證文件建立 Google Vision 客戶端")
                
            # 創建 vision API 圖像
            image = vision.Image(content=image_data)
            
            # 配置語言提示 (支援中文繁體和英文)
            image_context = vision.ImageContext(
                language_hints=['zh-Hant', 'en']
            )
            
            # 使用 document_text_detection 替代 text_detection，它更適合文檔結構，並提供更詳細的置信度
            response = client.document_text_detection(image=image, image_context=image_context)
            
            # 檢查錯誤
            if response.error.message:
                raise Exception(f"Vision API 錯誤: {response.error.message}")
            
            # 提取完整文本
            full_text = response.text_annotations[0].description if response.text_annotations else ""
            
            # 記錄結果
            logger.info(f"Google Vision API 成功提取文本，長度: {len(full_text)}")
            
            # 創建結果字典 - 主要返回 paragraph 層級的結果
            result = {
                "text": full_text,
                "width": 0,
                "height": 0,
                "paragraphs": []   # 以段落作為主要返回層級
            }
            
            # 如果有完整的文本註釋
            if response.full_text_annotation and response.full_text_annotation.pages:
                # 獲取頁面大小
                page = response.full_text_annotation.pages[0]  # 僅處理第一頁
                result["width"] = page.width
                result["height"] = page.height
                
                # 處理詳細的文本區塊
                try:
                    # 從完整的文本註釋中提取段落
                    paragraph_count = 0
                    
                    # 檢查頁面中是否有 blocks 屬性
                    if hasattr(page, 'blocks') and page.blocks:
                        blocks = page.blocks
                    else:
                        # 如果沒有 blocks 屬性，嘗試使用 text_annotations
                        logger.warning("頁面沒有 blocks 屬性，改用 text_annotations")
                        blocks = []
                    
                    for block in blocks:
                        block_id = block.block_type if hasattr(block, 'block_type') else "UNKNOWN"
                        
                        # 提取段落文本
                        for paragraph in block.paragraphs:
                            paragraph_count += 1
                            paragraph_text = ""
                            
                            # 使用段落的置信度（如果有）
                            paragraph_confidence = paragraph.confidence if hasattr(paragraph, 'confidence') and paragraph.confidence else 0.0
                            
                            # 提取單詞文本以構建段落文本
                            for word in paragraph.words:
                                word_text = ''.join([symbol.text for symbol in word.symbols])
                                paragraph_text += word_text + " "
                            
                            # 添加此段落的信息
                            if paragraph.bounding_box:
                                paragraph_vertices = [
                                    {"x": vertex.x, "y": vertex.y} 
                                    for vertex in paragraph.bounding_box.vertices
                                ]
                                
                                # 將段落置信度轉換為百分比
                                paragraph_confidence_percent = round(paragraph_confidence * 100, 2) if paragraph_confidence > 0 else 0
                                
                                result["paragraphs"].append({
                                    "text": paragraph_text.strip(),
                                    "bounding_box": {
                                        "vertices": paragraph_vertices
                                    },
                                    "confidence": paragraph_confidence_percent,
                                    "paragraph_id": paragraph_count,
                                    "block_type": str(block_id)
                                })
                except Exception as block_error:
                    logger.warning(f"提取詳細區塊信息時出錯: {block_error}")
            
            # 如果沒有從 full_text_annotation 獲得段落信息，則從 text_annotations 獲取
            if not result["paragraphs"] and len(response.text_annotations) > 1:
                # 跳過第一個（它是完整文本），提取其餘的文本區塊
                paragraph_count = 0
                for text_annotation in response.text_annotations[1:]:
                    paragraph_count += 1
                    
                    # 檢查是否有邊界框
                    if not hasattr(text_annotation, 'bounding_poly') or not text_annotation.bounding_poly:
                        continue
                    
                    vertices = [
                        {"x": vertex.x, "y": vertex.y} 
                        for vertex in text_annotation.bounding_poly.vertices
                    ]
                    
                    # 獲取置信度（如果有）
                    confidence = 0.0
                    if hasattr(text_annotation, 'confidence') and text_annotation.confidence:
                        confidence = text_annotation.confidence
                    
                    # 將置信度轉換為百分比
                    confidence_percent = round(confidence * 100, 2) if confidence > 0 else 0
                    
                    result["paragraphs"].append({
                        "text": text_annotation.description,
                        "bounding_box": {
                            "vertices": vertices
                        },
                        "confidence": confidence_percent,
                        "paragraph_id": paragraph_count,
                        "block_type": "TEXT_ANNOTATION"
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"Google Vision API 調用失敗: {e}")
            return {
                "text": "OCR 處理失敗，請確認 Google Vision API 憑證是否正確設置。",
                "width": 0,
                "height": 0,
                "paragraphs": []
            }

    async def extract_batch_text(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        處理多個文件進行 OCR
        
        Args:
            files: 文件資訊列表，每個元素應包含 filename, mimetype, size, link
            
        Returns:
            List[Dict[str, Any]]: 每個文件的處理結果清單
        """
        logger.info(f"===================== 開始批量處理 {len(files)} 個文件 =====================")
        
        results = []
        
        for file_info in files:
            try:
                file_url = file_info.get("link")
                file_type = file_info.get("mimetype")
                filename = file_info.get("filename")
                
                logger.info(f"處理文件: {filename} ({file_type})")
                
                # 使用現有的 extract_text 方法處理每個文件
                result = await self.extract_text(file_url, file_type)
                
                # 獲取文本和其他信息
                if isinstance(result, dict):
                    text = result.get("text", "")
                    # 複製結果並添加文件信息
                    file_result = result.copy()
                    file_result.update({
                        "filename": filename,
                        "mimetype": file_type,
                        "success": True,
                        "file_url": file_url
                    })
                    results.append(file_result)
                else:
                    # 兼容舊的純文本結果
                    results.append({
                        "filename": filename,
                        "mimetype": file_type,
                        "text": result,
                        "success": True,
                        "file_url": file_url
                    })
                
            except Exception as e:
                logger.error(f"處理文件 {file_info.get('filename')} 時出錯: {e}")
                
                # 即使發生錯誤，也添加到結果中
                results.append({
                    "filename": file_info.get("filename"),
                    "mimetype": file_info.get("mimetype"),
                    "text": f"處理錯誤: {str(e)}",
                    "success": False,
                    "error": str(e)
                })
        
        logger.info(f"批量處理完成，成功: {sum(1 for r in results if r.get('success', False))}/{len(results)}")
        
        return results

# 服務單例
ocr_service = OCRService()
