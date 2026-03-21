from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum


class SecurityLevel(str, enum.Enum):
    LEVEL2 = "二级"
    LEVEL3 = "三级"


class CheckResult(str, enum.Enum):
    COMPLIANT = "符合"
    NON_COMPLIANT = "不符合"
    PARTIAL = "部分符合"
    NOT_APPLICABLE = "不适用"


class RiskLevel(str, enum.Enum):
    HIGH = "高危"
    MEDIUM = "中危"
    LOW = "低危"


class EvalObjectType(str, enum.Enum):
    PHYSICAL_ROOM = "物理机房"
    NETWORK_DEVICE = "网络设备"
    SECURITY_DEVICE = "安全设备"
    SERVER_STORAGE = "服务器/存储"
    TERMINAL = "终端设备"
    OTHER_DEVICE = "其他系统或设备"
    SYSTEM_SOFTWARE = "系统管理软件/平台"
    BUSINESS_APP = "业务应用系统/平台"
    DATA_RESOURCE = "数据资源"
    SECURITY_PERSONNEL = "安全相关人员"
    SECURITY_DOCUMENT = "安全管理文档"
    VULN_SCAN = "漏洞扫描"
    PENTEST = "渗透测试"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    security_level = Column(String(10), nullable=False)
    organization = Column(String(200), nullable=False)
    eval_date = Column(String(20))
    reviewer = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    eval_objects = relationship("EvalObject", back_populates="project", cascade="all, delete-orphan")
    issues = relationship("Issue", back_populates="project", cascade="all, delete-orphan")


class EvalObject(Base):
    __tablename__ = "eval_objects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    object_type = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    sub_type = Column(String(100))
    extra_info = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    project = relationship("Project", back_populates="eval_objects")
    check_records = relationship("CheckRecord", back_populates="eval_object", cascade="all, delete-orphan")


class CheckItem(Base):
    __tablename__ = "check_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    object_type = Column(String(50), nullable=False)
    security_level = Column(String(10), nullable=False)
    category = Column(String(100), nullable=False)
    sub_category = Column(String(100))
    item_code = Column(String(50))
    content = Column(Text, nullable=False)
    is_cloud_extension = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)


class CheckRecord(Base):
    __tablename__ = "check_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    eval_object_id = Column(Integer, ForeignKey("eval_objects.id", ondelete="CASCADE"), nullable=False)
    check_item_id = Column(Integer, ForeignKey("check_items.id"), nullable=False)
    result = Column(String(20))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    eval_object = relationship("EvalObject", back_populates="check_records")
    check_item = relationship("CheckItem")
    attachments = relationship("Attachment", back_populates="check_record", cascade="all, delete-orphan")


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    check_record_id = Column(Integer, ForeignKey("check_records.id"), nullable=True)
    description = Column(Text, nullable=False)
    risk_level = Column(String(10), nullable=False)
    suggestion = Column(Text)
    client_opinion = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    project = relationship("Project", back_populates="issues")
    check_record = relationship("CheckRecord")


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    check_record_id = Column(Integer, ForeignKey("check_records.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    check_record = relationship("CheckRecord", back_populates="attachments")
