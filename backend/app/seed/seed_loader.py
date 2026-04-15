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
        # 标记云计算扩展项
        db.query(CheckItem).filter(
            CheckItem.is_cloud_extension == True,
            CheckItem.extension_type.is_(None)
        ).update({"extension_type": "云计算", "standard_ref": "GB/T 22239-2019"})
        db.commit()
        print(f"成功导入 {len(items)} 条检查项")
    finally:
        db.close()


def seed_extension_items():
    db = SessionLocal()
    try:
        # 用非云计算的扩展类型判断是否已导入扩展种子数据
        ext_count = db.query(CheckItem).filter(
            CheckItem.extension_type.isnot(None),
            CheckItem.extension_type != '云计算'
        ).count()
        if ext_count > 0:
            print(f"扩展题库已有 {ext_count} 条数据，跳过导入")
            return
        seed_file = os.path.join(os.path.dirname(__file__), "check_items_extensions.json")
        if not os.path.exists(seed_file):
            print("扩展种子数据文件不存在，跳过导入")
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
                extension_type=item_data.get("extension_type"),
                standard_ref=item_data.get("standard_ref"),
            )
            db.add(item)
        db.commit()
        print(f"成功导入 {len(items)} 条扩展检查项")
    finally:
        db.close()


if __name__ == "__main__":
    seed_check_items()
    seed_extension_items()
