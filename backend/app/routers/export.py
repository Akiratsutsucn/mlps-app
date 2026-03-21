from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.models import Project, EvalObject, CheckRecord, Issue
from app.services.excel_export import generate_excel
import io

router = APIRouter(prefix="/api/projects/{project_id}/export", tags=["export"])


@router.get("/excel")
def export_excel(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    eval_objects = db.query(EvalObject).filter(
        EvalObject.project_id == project_id
    ).order_by(EvalObject.id).all()

    records = []
    for obj in eval_objects:
        obj_records = db.query(CheckRecord).options(
            joinedload(CheckRecord.check_item)
        ).filter(CheckRecord.eval_object_id == obj.id).order_by(CheckRecord.check_item_id).all()
        records.append((obj, obj_records))

    issues = db.query(Issue).filter(
        Issue.project_id == project_id
    ).order_by(Issue.created_at).all()

    wb = generate_excel(project, records, issues)
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"{project.organization}_{project.name}_评测记录.xlsx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
    )
