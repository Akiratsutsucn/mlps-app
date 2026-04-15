from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.models import CheckItem
from app.schemas.schemas import CheckItemCreate, CheckItemUpdate, CheckItemOut

router = APIRouter(prefix="/api/check-items", tags=["check_items"])


@router.get("", response_model=List[CheckItemOut])
def list_check_items(
    object_type: Optional[str] = None,
    security_level: Optional[str] = None,
    category: Optional[str] = None,
    is_cloud: Optional[bool] = None,
    extension_type: Optional[str] = None,
    standard_ref: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(CheckItem)
    if object_type:
        query = query.filter(CheckItem.object_type == object_type)
    if security_level:
        query = query.filter(CheckItem.security_level == security_level)
    if category:
        query = query.filter(CheckItem.category == category)
    if is_cloud is not None:
        query = query.filter(CheckItem.is_cloud_extension == is_cloud)
    if extension_type:
        if extension_type == "base":
            query = query.filter(CheckItem.extension_type.is_(None))
        else:
            query = query.filter(CheckItem.extension_type == extension_type)
    if standard_ref:
        query = query.filter(CheckItem.standard_ref == standard_ref)
    if keyword:
        query = query.filter(CheckItem.content.contains(keyword))
    total = query.count()
    items = query.order_by(CheckItem.id).offset((page - 1) * page_size).limit(page_size).all()
    return items


@router.get("/count")
def count_check_items(db: Session = Depends(get_db)):
    total = db.query(CheckItem).count()
    return {"total": total}


@router.post("", response_model=CheckItemOut)
def create_check_item(data: CheckItemCreate, db: Session = Depends(get_db)):
    item = CheckItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return CheckItemOut.model_validate(item)


@router.put("/{item_id}", response_model=CheckItemOut)
def update_check_item(item_id: int, data: CheckItemUpdate, db: Session = Depends(get_db)):
    item = db.query(CheckItem).filter(CheckItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="检查项不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return CheckItemOut.model_validate(item)


@router.delete("/{item_id}")
def delete_check_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(CheckItem).filter(CheckItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="检查项不存在")
    db.delete(item)
    db.commit()
    return {"message": "已删除"}


@router.get("/categories")
def get_categories(object_type: Optional[str] = None, security_level: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(CheckItem.category).distinct()
    if object_type:
        query = query.filter(CheckItem.object_type == object_type)
    if security_level:
        query = query.filter(CheckItem.security_level == security_level)
    categories = [row[0] for row in query.all()]
    return categories
