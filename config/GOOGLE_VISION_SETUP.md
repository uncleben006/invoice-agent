# Google Vision API 設置指南

本文件提供了如何設置和獲取 Google Vision API 憑證的詳細步驟。

## 步驟 1: 創建 Google Cloud 項目

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 點擊頁面頂部的"選擇項目"（或"Select a project"）下拉菜單
3. 點擊"新建項目"（"New Project"）
4. 輸入項目名稱，例如 "invoice-agent"
5. 點擊"創建"

## 步驟 2: 啟用 Vision API

1. 在左側導航欄中，點擊"API 和服務" > "API 庫"（或 "APIs & Services" > "Library"）
2. 在搜索欄中輸入 "Vision API"
3. 點擊 "Cloud Vision API" 結果
4. 點擊 "啟用" 按鈕

## 步驟 3: 創建服務帳號和下載憑證

1. 在左側導航欄中，點擊 "IAM 和管理" > "服務帳號"（或 "IAM & Admin" > "Service Accounts"）
2. 點擊頁面頂部的 "創建服務帳號"（"Create Service Account"）
3. 輸入服務帳號名稱，例如 "invoice-ocr"
4. 點擊 "創建並繼續"
5. 點擊角色選擇器並選擇 "Cloud Vision" > "Cloud Vision API 用戶"（"Cloud Vision API User"）
6. 點擊 "完成"
7. 在服務帳號列表中，找到剛剛創建的服務帳號，點擊服務帳號名稱
8. 在詳情頁面，點擊 "密鑰" 標籤
9. 點擊 "添加密鑰" > "創建新密鑰"（"Add Key" > "Create New Key"）
10. 確保選擇了 "JSON" 格式，然後點擊 "創建"
11. 瀏覽器將自動下載 JSON 憑證文件

## 步驟 4: 配置您的應用

1. 將下載的 JSON 憑證文件重命名為 `vision-credentials.json`
2. 將此文件放在項目的 `/config` 目錄下
3. 確保 `docker-compose.yml` 文件中已正確配置了卷掛載，以便容器可以訪問此文件
4. 重新啟動您的 Docker 容器

## 步驟 5: 測試 API

1. 在 Swagger UI 介面（http://localhost:8008/docs）中嘗試 OCR 接口
2. 提供一個影像 URL 並檢查 API 是否可以成功提取文本

## 排錯

如果遇到 "Google Vision API 憑證不存在" 錯誤，請檢查:

1. 憑證文件是否已放置在正確位置
2. 容器是否可以訪問該文件（檢查卷掛載）
3. 環境變數 `GOOGLE_APPLICATION_CREDENTIALS` 是否正確設置
4. API 是否已在 Google Cloud Console 中啟用
5. 服務帳號是否擁有正確的權限

## 注意事項

- Google Vision API 是付費服務，請查看 [Google Cloud 定價頁面](https://cloud.google.com/vision/pricing) 了解詳情
- 每月有免費額度，通常足夠用於測試和小規模使用
- 保護好您的憑證文件，不要將其提交到版本控制系統中
