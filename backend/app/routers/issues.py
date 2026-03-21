from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import Issue
from app.schemas.schemas import IssueCreate, IssueUpdate, IssueOut

router = APIRouter(prefix="/api/projects/{project_id}/issues", tags=["issues"])


@router.get("", response_model=List[IssueOut])
def list_issues(project_id: int, db: Session = Depends(get_db)):
    issues = db.query(Issue).filter(Issue.project_id == project_id).order_by(Issue.created_at.desc()).all()
    return [IssueOut.model_validate(i) for i in issues]


@router.post("", response_model=IssueOut)
def create_issue(project_id: int, data: IssueCreate, db: Session = Depends(get_db)):
    issue = Issue(project_id=project_id, **data.model_dump())
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return IssueOut.model_validate(issue)


@router.put("/{issue_id}", response_model=IssueOut)
def update_issue(project_id: int, issue_id: int, data: IssueUpdate, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.id == issue_id, Issue.project_id == project_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="问题不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(issue, key, value)
    db.commit()
    db.refresh(issue)
    return IssueOut.model_validate(issue)


@router.delete("/{issue_id}")
def delete_issue(project_id: int, issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.id == issue_id, Issue.project_id == project_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="问题不存在")
    db.delete(issue)
    db.commit()
    return {"message": "已删除"}
