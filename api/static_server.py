from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from agents.settings import agent_settings

def setup_static_routes(app: FastAPI) -> None:
    """Setup static file serving"""
    
    # مسیر ذخیره فایل‌های استاتیک
    storage_path = Path("/app/storage")
    
    # اطمینان از وجود مسیر
    if not storage_path.exists():
        storage_path.mkdir(parents=True, exist_ok=True)
        
    # اطمینان از وجود مسیر charts
    charts_path = storage_path / "charts"
    if not charts_path.exists():
        charts_path.mkdir(parents=True, exist_ok=True)
    
    # تنظیم CORS برای دسترسی به فایل‌های استاتیک
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # تنظیم مسیر استاتیک
    app.mount("/static", StaticFiles(directory=str(storage_path)), name="static")