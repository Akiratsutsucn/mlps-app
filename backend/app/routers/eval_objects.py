from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database import get_db
from app.models.models import EvalObject, CheckRecord, CheckItem, Project
from app.schemas.schemas import EvalObjectCreate, EvalObjectUpdate, EvalObjectOut

router = APIRouter(prefix="/api/projects/{project_id}/eval-objects", tags=["eval_objects"])


@router.get("", response_model=List[EvalObjectOut])
def list_eval_objects(project_id: int, db: Session = Depends(get_db)):
    objects = db.query(EvalObject).filter(EvalObject.project_id == project_id).order_by(EvalObject.id).all()
    result = []
    for obj in objects:
        out = EvalObjectOut.model_validate(obj)
        total = db.query(func.count(CheckRecord.id)).filter(CheckRecord.eval_object_id == obj.id).scalar()
        filled = db.query(func.count(CheckRecord.id)).filter(
            CheckRecord.eval_object_id == obj.id, CheckRecord.result.isnot(None)
        ).scalar()
        out.progress = {"total": total, "filled": filled}
        result.append(out)
    return result


@router.post("", response_model=EvalObjectOut)
def create_eval_object(project_id: int, data: EvalObjectCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    obj = EvalObject(project_id=project_id, **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    # Auto-create check records from question bank
    items = db.query(CheckItem).filter(
        CheckItem.object_type == obj.object_type,
        CheckItem.security_level == project.security_level
    ).all()
    for item in items:
        record = CheckRecord(eval_object_id=obj.id, check_item_id=item.id)
        db.add(record)
    db.commit()
    return EvalObjectOut.model_validate(obj)


@router.put("/{obj_id}", response_model=EvalObjectOut)
def update_eval_object(project_id: int, obj_id: int, data: EvalObjectUpdate, db: Session = Depends(get_db)):
    obj = db.query(EvalObject).filter(EvalObject.id == obj_id, EvalObject.project_id == project_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="评测对象不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return EvalObjectOut.model_validate(obj)


@router.delete("/{obj_id}")
def delete_eval_object(project_id: int, obj_id: int, db: Session = Depends(get_db)):
    obj = db.query(EvalObject).filter(EvalObject.id == obj_id, EvalObject.project_id == project_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="评测对象不存在")
    db.delete(obj)
    db.commit()
    return {"message": "已删除"}


@router.post("/{obj_id}/copy-from/{source_id}")
def copy_records(project_id: int, obj_id: int, source_id: int, db: Session = Depends(get_db)):
    target = db.query(EvalObject).filter(EvalObject.id == obj_id, EvalObject.project_id == project_id).first()
    source = db.query(EvalObject).filter(EvalObject.id == source_id, EvalObject.project_id == project_id).first()
    if not target or not source:
        raise HTTPException(status_code=404, detail="评测对象不存在")
    if target.object_type != source.object_type:
        raise HTTPException(status_code=400, detail="评测对象类型不一致")
    source_records = db.query(CheckRecord).filter(CheckRecord.eval_object_id == source_id).all()
    target_records = db.query(CheckRecord).filter(CheckRecord.eval_object_id == obj_id).all()
    target_map = {r.check_item_id: r for r in target_records}
    for sr in source_records:
        if sr.check_item_id in target_map:
            target_map[sr.check_item_id].result = sr.result
            target_map[sr.check_item_id].description = sr.description
    db.commit()
    return {"message": "复制完成"}
