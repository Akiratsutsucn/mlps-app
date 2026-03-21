import json
import os
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models.models import CheckItem


def seed_check_items():
    db = SessionLocal()
    try:
        existing = db.query(CheckItem).count()
        if existing > 0:
            print(f"题库已有 {existing} 条数据，跳过导入")
            return
        seed_file = os.path.join(os.path.dirname(__file__), "check_items.json")
        if not os.path.exists(seed_file):
            print("种子数据文件不存在，跳过导入")
            return
        with open(seed_file, "r", encoding="utf-8") as f:
            items = json.load(f)
        for item_data in items:
            item = CheckItem(
                object_type=item_data["object_type"],
                security_level=item_data["security_level"],
                category=item_data["category"],
                sub_category=item_data.get("sub_category", ""),
                item_code=item_data.get("item_code", ""),
                content=item_data["content"],
                is_cloud_extension=item_data.get("is_cloud_extension", False),
            )
            db.add(item)
        db.commit()
        print(f"成功导入 {len(items)} 条检查项")
    finally:
        db.close()


if __name__ == "__main__":
    seed_check_items()
