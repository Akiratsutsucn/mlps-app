from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.database import engine, Base
from app.models.models import *
from app.routers import projects, eval_objects, check_items, check_records, issues, statistics, export

Base.metadata.create_all(bind=engine)

from sqlalchemy import inspect, text


# 数据库迁移：添加 extension_type 和 standard_ref 列
def migrate_check_items_table():
    with engine.connect() as conn:
        inspector = inspect(engine)
        columns = [col["name"] for col in inspector.get_columns("check_items")]
        if "extension_type" not in columns:
            conn.execute(text("ALTER TABLE check_items ADD COLUMN extension_type VARCHAR(50)"))
            conn.execute(text("ALTER TABLE check_items ADD COLUMN standard_ref VARCHAR(100)"))
            conn.execute(text(
                "UPDATE check_items SET extension_type = '云计算', standard_ref = 'GB/T 22239-2019' "
                "WHERE is_cloud_extension = 1"
            ))
            conn.commit()
            print("迁移完成：check_items 表已添加 extension_type 和 standard_ref 列")


migrate_check_items_table()

# Seed question bank on first run
from app.seed.seed_loader import seed_check_items, seed_extension_items
seed_check_items()
seed_extension_items()

app = FastAPI(title="等级保护评测过程记录系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(eval_objects.router)
app.include_router(check_items.router)
app.include_router(check_records.router)
app.include_router(issues.router)
app.include_router(statistics.router)
app.include_router(export.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Serve uploaded files
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Serve frontend static files if built
FRONTEND_DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")
if os.path.exists(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
