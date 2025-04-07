from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from invoice_agent.api import ocr, product
from invoice_agent.db.mongodb import connect_to_mongo, close_mongo_connection
from invoice_agent.core.logging import logger

app = FastAPI(
    title="Invoice Agent API",
    description="API 服務用於處理發票相關操作",
    version="0.1.0",
    docs_url=None,  # 自定義文檔 URL
    redoc_url=None  # 自定義 ReDoc URL
)

# 註冊啟動和關閉事件
@app.on_event("startup")
async def startup():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown():
    await close_mongo_connection()

# 註冊 OCR API 路由
app.include_router(ocr.router, prefix="/api")

# 註冊產品 API 路由
app.include_router(product.router, prefix="/api")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """自定義 Swagger UI 頁面"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - API 文檔",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """ReDoc 文檔頁面"""
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在實際生產環境中應該限制來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "歡迎使用 Invoice Agent API"}

@app.get("/health")
async def health_check():
    return {"status": "健康", "version": "0.1.0"}