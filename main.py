from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import pdf_router, key_router, status_router

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PDF Translation Service",
    description="PDF文件管理和翻译服务API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(pdf_router.router, prefix="/api/pdf", tags=["PDF管理"])
app.include_router(key_router.router, prefix="/api/key", tags=["密钥管理"])
app.include_router(status_router.router, prefix="/api/status", tags=["状态管理"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 