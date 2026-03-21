from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.models import EvalObject, CheckRecord, Issue

router = APIRouter(prefix="/api/projects/{project_id}/stats", tags=["statistics"])


@router.get("")
def get_project_stats(project_id: int, db: Session = Depends(get_db)):
    obj_ids = [r[0] for r in db.query(EvalObject.id).filter(EvalObject.project_id == project_id).all()]

    total_records = 0
    result_counts = {"符合": 0, "不符合": 0, "部分符合": 0, "不适用": 0, "未填写": 0}
    if obj_ids:
        total_records = db.query(func.count(CheckRecord.id)).filter(
            CheckRecord.eval_object_id.in_(obj_ids)
        ).scalar()
        for result_val in ["符合", "不符合", "部分符合", "不适用"]:
            result_counts[result_val] = db.query(func.count(CheckRecord.id)).filter(
                CheckRecord.eval_object_id.in_(obj_ids),
                CheckRecord.result == result_val
            ).scalar()
        filled = sum(v for k, v in result_counts.items() if k != "未填写")
        result_counts["未填写"] = total_records - filled

    issue_counts = {"高危": 0, "中危": 0, "低危": 0}
    total_issues = db.query(func.count(Issue.id)).filter(Issue.project_id == project_id).scalar()
    for level in ["高危", "中危", "低危"]:
        issue_counts[level] = db.query(func.count(Issue.id)).filter(
            Issue.project_id == project_id, Issue.risk_level == level
        ).scalar()

    obj_type_stats = []
    objects = db.query(EvalObject).filter(EvalObject.project_id == project_id).all()
    for obj in objects:
        obj_total = db.query(func.count(CheckRecord.id)).filter(CheckRecord.eval_object_id == obj.id).scalar()
        obj_filled = db.query(func.count(CheckRecord.id)).filter(
            CheckRecord.eval_object_id == obj.id, CheckRecord.result.isnot(None)
        ).scalar()
        obj_compliant = db.query(func.count(CheckRecord.id)).filter(
            CheckRecord.eval_object_id == obj.id, CheckRecord.result == "符合"
        ).scalar()
        obj_type_stats.append({
            "id": obj.id,
            "name": obj.name,
            "object_type": obj.object_type,
            "total": obj_total,
            "filled": obj_filled,
            "compliant": obj_compliant,
        })

    return {
        "total_records": total_records,
        "result_counts": result_counts,
        "total_issues": total_issues,
        "issue_counts": issue_counts,
        "eval_objects": obj_type_stats,
        "eval_object_count": len(objects),
    }
