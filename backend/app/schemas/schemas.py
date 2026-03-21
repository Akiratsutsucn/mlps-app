from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# Project
class ProjectCreate(BaseModel):
    name: str
    security_level: str
    organization: str
    eval_date: Optional[str] = None
    reviewer: Optional[str] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    security_level: Optional[str] = None
    organization: Optional[str] = None
    eval_date: Optional[str] = None
    reviewer: Optional[str] = None

class ProjectOut(BaseModel):
    id: int
    name: str
    security_level: str
    organization: str
    eval_date: Optional[str]
    reviewer: Optional[str]
    created_at: datetime
    updated_at: datetime
    eval_object_count: Optional[int] = 0
    issue_count: Optional[int] = 0
    model_config = {"from_attributes": True}


# EvalObject
class EvalObjectCreate(BaseModel):
    object_type: str
    name: str
    sub_type: Optional[str] = None
    extra_info: Optional[str] = None

class EvalObjectUpdate(BaseModel):
    name: Optional[str] = None
    sub_type: Optional[str] = None
    extra_info: Optional[str] = None

class EvalObjectOut(BaseModel):
    id: int
    project_id: int
    object_type: str
    name: str
    sub_type: Optional[str]
    extra_info: Optional[str]
    created_at: datetime
    progress: Optional[dict] = None
    model_config = {"from_attributes": True}


# CheckItem
class CheckItemCreate(BaseModel):
    object_type: str
    security_level: str
    category: str
    sub_category: Optional[str] = None
    item_code: Optional[str] = None
    content: str
    is_cloud_extension: bool = False

class CheckItemUpdate(BaseModel):
    object_type: Optional[str] = None
    security_level: Optional[str] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    item_code: Optional[str] = None
    content: Optional[str] = None
    is_cloud_extension: Optional[bool] = None

class CheckItemOut(BaseModel):
    id: int
    object_type: str
    security_level: str
    category: str
    sub_category: Optional[str]
    item_code: Optional[str]
    content: str
    is_cloud_extension: bool
    created_at: datetime
    model_config = {"from_attributes": True}


# CheckRecord
class CheckRecordCreate(BaseModel):
    check_item_id: int
    result: Optional[str] = None
    description: Optional[str] = None

class CheckRecordUpdate(BaseModel):
    result: Optional[str] = None
    description: Optional[str] = None

class CheckRecordOut(BaseModel):
    id: int
    eval_object_id: int
    check_item_id: int
    result: Optional[str]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    check_item: Optional[CheckItemOut] = None
    model_config = {"from_attributes": True}


# Issue
class IssueCreate(BaseModel):
    check_record_id: Optional[int] = None
    description: str
    risk_level: str
    suggestion: Optional[str] = None

class IssueUpdate(BaseModel):
    description: Optional[str] = None
    risk_level: Optional[str] = None
    suggestion: Optional[str] = None
    client_opinion: Optional[str] = None

class IssueOut(BaseModel):
    id: int
    project_id: int
    check_record_id: Optional[int]
    description: str
    risk_level: str
    suggestion: Optional[str]
    client_opinion: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}


# Attachment
class AttachmentOut(BaseModel):
    id: int
    check_record_id: int
    file_path: str
    file_name: str
    created_at: datetime
    model_config = {"from_attributes": True}
