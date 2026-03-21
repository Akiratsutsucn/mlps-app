from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import os
import uuid
from app.database import get_db
from app.models.models import CheckRecord, EvalObject, Attachment
from app.schemas.schemas import CheckRecordOut, CheckRecordUpdate, AttachmentOut

router = APIRouter(prefix="/api/eval-objects/{obj_id}/records", tags=["check_records"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")


@router.get("", response_model=List[CheckRecordOut])
def list_records(obj_id: int, category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(CheckRecord).options(
        joinedload(CheckRecord.check_item)
    ).filter(CheckRecord.eval_object_id == obj_id)
    if category:
        query = query.join(CheckRecord.check_item).filter(
            CheckRecord.check_item.has(category=category)
        )
    records = query.order_by(CheckRecord.check_item_id).all()
    return [CheckRecordOut.model_validate(r) for r in records]


@router.put("/{record_id}", response_model=CheckRecordOut)
def update_record(obj_id: int, record_id: int, data: CheckRecordUpdate, db: Session = Depends(get_db)):
    record = db.query(CheckRecord).options(
        joinedload(CheckRecord.check_item)
    ).filter(CheckRecord.id == record_id, CheckRecord.eval_object_id == obj_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="检查记录不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return CheckRecordOut.model_validate(record)


@router.post("/{record_id}/attachments", response_model=AttachmentOut)
async def upload_attachment(obj_id: int, record_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    record = db.query(CheckRecord).filter(CheckRecord.id == record_id, CheckRecord.eval_object_id == obj_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="检查记录不存在")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename)[1] if file.filename else ""
    saved_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, saved_name)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    attachment = Attachment(
        check_record_id=record_id,
        file_path=saved_name,
        file_name=file.filename or saved_name
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return AttachmentOut.model_validate(attachment)


@router.get("/{record_id}/attachments", response_model=List[AttachmentOut])
def list_attachments(obj_id: int, record_id: int, db: Session = Depends(get_db)):
    attachments = db.query(Attachment).filter(Attachment.check_record_id == record_id).all()
    return [AttachmentOut.model_validate(a) for a in attachments]


@router.delete("/{record_id}/attachments/{att_id}")
def delete_attachment(obj_id: int, record_id: int, att_id: int, db: Session = Depends(get_db)):
    att = db.query(Attachment).filter(Attachment.id == att_id, Attachment.check_record_id == record_id).first()
    if not att:
        raise HTTPException(status_code=404, detail="附件不存在")
    file_path = os.path.join(UPLOAD_DIR, att.file_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.delete(att)
    db.commit()
    return {"message": "已删除"}
