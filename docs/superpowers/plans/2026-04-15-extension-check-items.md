# 扩展等保题库 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为等保评测系统题库新增 9 大扩展领域（移动互联/物联网/工业控制/边缘计算/大数据/IPv6/区块链/5G接入）的检查项，扩展数据模型、种子数据、API 和前端。

**Architecture:** 在 CheckItem 表新增 extension_type 和 standard_ref 字段，新增 ~285 条扩展检查项种子数据，前端题库管理和评测对象管理页面支持按扩展类型筛选和分组。

**Tech Stack:** Python FastAPI, SQLAlchemy, SQLite, Vue 3, Element Plus, Pinia

---

## Task 1: 后端数据模型变更

**Files:**
- `backend/app/models/models.py`
- `backend/app/main.py`

### 1.1 CheckItem 表新增字段

- [ ] 在 `backend/app/models/models.py` 的 `CheckItem` 类中，`is_cloud_extension` 行之后新增两列：

```python
extension_type = Column(String(50), nullable=True)   # 扩展领域，null=基础通用
standard_ref = Column(String(100), nullable=True)     # 标准来源编号
```

### 1.2 EvalObjectType 枚举新增 16 种对象类型

- [ ] 在 `backend/app/models/models.py` 的 `EvalObjectType` 枚举末尾追加：

```python
    # --- 新增 16 种（扩展领域） ---
    SENSOR_NODE = "感知节点设备"
    GATEWAY_NODE = "网关节点设备"
    ICS_DEVICE = "工业控制设备"
    OUTDOOR_CTRL = "室外控制设备"
    WIRELESS_AP = "无线接入设备"
    MOBILE_TERMINAL = "移动终端"
    MEC_NODE = "MEC节点"
    EDGE_GATEWAY = "边缘网关"
    BIGDATA_PLATFORM = "大数据平台"
    DATA_COLLECTOR = "数据采集节点"
    IPV6_NETWORK = "IPv6网络设备"
    IPV6_SECURITY = "IPv6安全设备"
    BLOCKCHAIN_NODE = "区块链节点"
    SMART_CONTRACT = "智能合约系统"
    BASE_STATION_5G = "5G基站"
    UPF_DEVICE = "UPF设备"
```

### 1.3 数据库迁移逻辑

- [ ] 在 `backend/app/main.py` 中，`Base.metadata.create_all(bind=engine)` 之后、`seed_check_items()` 之前，添加迁移函数并调用：

```python
from sqlalchemy import inspect, text

# 数据库迁移：添加 extension_type 和 standard_ref 列
def migrate_check_items_table():
    with engine.connect() as conn:
        inspector = inspect(engine)
        columns = [col["name"] for col in inspector.get_columns("check_items")]
        if "extension_type" not in columns:
            conn.execute(text("ALTER TABLE check_items ADD COLUMN extension_type VARCHAR(50)"))
            conn.execute(text("ALTER TABLE check_items ADD COLUMN standard_ref VARCHAR(100)"))
            conn.execute(text(
                "UPDATE check_items SET extension_type = '云计算', standard_ref = 'GB/T 22239-2019' "
                "WHERE is_cloud_extension = 1"
            ))
            conn.commit()
            print("迁移完成：check_items 表已添加 extension_type 和 standard_ref 列")

migrate_check_items_table()
```

- [ ] 修改 seed 导入行为：

```python
from app.seed.seed_loader import seed_check_items, seed_extension_items
seed_check_items()
seed_extension_items()
```

### 验证

- [ ] 运行 `cd backend && python -c "from app.models.models import CheckItem, EvalObjectType; print('OK')"` 确认模型无语法错误

---

## Task 2: Schema 和 API 变更

**Files:**
- `backend/app/schemas/schemas.py`
- `backend/app/routers/check_items.py`

### 2.1 Schema 新增字段

- [ ] 在 `backend/app/schemas/schemas.py` 中修改 `CheckItemCreate`，`is_cloud_extension` 之后添加：

```python
    extension_type: Optional[str] = None
    standard_ref: Optional[str] = None
```

- [ ] 同样修改 `CheckItemUpdate`，`is_cloud_extension` 之后添加：

```python
    extension_type: Optional[str] = None
    standard_ref: Optional[str] = None
```

- [ ] 同样修改 `CheckItemOut`，`is_cloud_extension` 之后添加：

```python
    extension_type: Optional[str] = None
    standard_ref: Optional[str] = None
```

### 2.2 API 新增查询参数

- [ ] 在 `backend/app/routers/check_items.py` 的 `list_check_items` 函数签名中新增两个参数：

```python
    extension_type: Optional[str] = None,
    standard_ref: Optional[str] = None,
```

- [ ] 在函数体的过滤逻辑中（`if is_cloud is not None:` 块之后）添加：

```python
    if extension_type:
        if extension_type == "base":
            query = query.filter(CheckItem.extension_type.is_(None))
        else:
            query = query.filter(CheckItem.extension_type == extension_type)
    if standard_ref:
        query = query.filter(CheckItem.standard_ref == standard_ref)
```

### 验证

- [ ] 运行 `cd backend && python -c "from app.schemas.schemas import CheckItemCreate, CheckItemOut; print('OK')"` 确认无语法错误

---

## Task 3: 种子数据加载器变更

**Files:**
- `backend/app/seed/seed_loader.py`

### 3.1 新增 seed_extension_items 函数

- [ ] 在 `backend/app/seed/seed_loader.py` 的 `seed_check_items()` 函数之后追加：

```python
def seed_extension_items():
    db = SessionLocal()
    try:
        ext_count = db.query(CheckItem).filter(CheckItem.extension_type.isnot(None)).count()
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
```

- [ ] 修改 `if __name__ == "__main__":` 块：

```python
if __name__ == "__main__":
    seed_check_items()
    seed_extension_items()
```

### 验证

- [ ] 运行 `cd backend && python -c "from app.seed.seed_loader import seed_extension_items; print('OK')"` 确认无语法错误

---

## Task 4: 编写扩展种子数据 — 国标原生（移动互联/物联网/工业控制）

**Files:**
- `backend/app/seed/check_items_extensions.json`（新建）

### 4.1 创建 check_items_extensions.json

- [ ] 在 `backend/app/seed/` 下创建 `check_items_extensions.json`，包含移动互联、物联网、工业控制三个扩展领域的检查项。数据来源：GB/T 22239-2019。

每条数据结构：

```json
{
  "object_type": "感知节点设备",
  "security_level": "二级",
  "category": "安全物理环境",
  "sub_category": "感知节点设备物理防护",
  "item_code": "L2-PES4-01",
  "content": "...",
  "is_cloud_extension": false,
  "extension_type": "物联网",
  "standard_ref": "GB/T 22239-2019"
}
```

编码规则：
- 移动互联场景码 3（如 `L3-PES3-01`、`L2-ABS3-01`）
- 物联网场景码 4（如 `L3-CES4-01`、`L2-PES4-01`）
- 工业控制场景码 5（如 `L3-ABS5-01`、`L2-CNS5-01`）

object_type 分配规则：
- 物联网：感知节点相关用"感知节点设备"，网关相关用"网关节点设备"
- 工业控制：室外控制设备物理防护相关用"室外控制设备"，其余用"工业控制设备"
- 移动互联：无线接入相关用"无线接入设备"，终端相关用"移动终端"

### 4.2 物联网检查项（35 条）

**二级（14 条）：**

| # | object_type | category | sub_category | item_code | content |
|---|------------|----------|-------------|-----------|---------|
| 1 | 感知节点设备 | 安全物理环境 | 感知节点设备物理防护 | L2-PES4-01 | 感知节点设备所处的物理环境应不对感知节点设备造成物理破坏，如挤压、强振动 |
| 2 | 感知节点设备 | 安全物理环境 | 感知节点设备物理防护 | L2-PES4-02 | 感知节点设备在工作状态所处物理环境应能正确反映环境状态（如温湿度传感器不能安装在阳光直射区域） |
| 3 | 感知节点设备 | 安全区域边界 | 接入控制 | L2-ABS4-01 | 应保证只有授权的感知节点可以接入 |
| 4 | 感知节点设备 | 安全区域边界 | 入侵防范 | L2-ABS4-02 | 应能够限制与感知节点通信的目标地址，以避免对陌生地址的攻击行为 |
| 5 | 网关节点设备 | 安全区域边界 | 入侵防范 | L2-ABS4-03 | 应能够限制与网关节点通信的目标地址，以避免对陌生地址的攻击行为 |
| 6 | 感知节点设备 | 安全计算环境 | 感知节点设备安全 | L2-CES4-01 | 应保证只有授权的用户可以对感知节点设备上的软件应用进行配置或变更 |
| 7 | 网关节点设备 | 安全计算环境 | 网关节点设备安全 | L2-CES4-02 | 应设置最大并发连接数 |
| 8 | 网关节点设备 | 安全计算环境 | 网关节点设备安全 | L2-CES4-03 | 应具备对合法连接设备（包括终端节点、路由节点、数据处理中心）进行标识和鉴别的能力 |
| 9 | 感知节点设备 | 安全计算环境 | 抗数据重放 | L2-CES4-04 | 应能够鉴别数据的新鲜性，避免历史数据的重放攻击 |
| 10 | 感知节点设备 | 安全计算环境 | 抗数据重放 | L2-CES4-05 | 应能够鉴别历史数据的非法修改，避免数据的修改重放攻击 |
| 11 | 网关节点设备 | 安全计算环境 | 数据融合处理 | L2-CES4-06 | 应对来自传感网的数据进行数据融合处理，使不同种类的数据可以在同一个平台被使用 |
| 12 | 感知节点设备 | 安全运维管理 | 感知节点管理 | L2-SMS4-01 | 应指定人员定期巡视感知节点设备、网关节点设备的部署环境，对可能影响感知节点设备、网关节点设备正常工作的环境异常进行记录和维护 |
| 13 | 感知节点设备 | 安全运维管理 | 感知节点管理 | L2-SMS4-02 | 应对感知节点设备、网关节点设备入库、存储、部署、携带、维修、丢失和报废等过程作出明确规定，并进行全程管理 |
| 14 | 感知节点设备 | 安全运维管理 | 感知节点管理 | L2-SMS4-03 | 应加强对感知节点设备、网关节点设备部署环境的保密性管理，包括负责检查和维护的人员调离工作岗位应立即交还相关检查工具和检查维护记录等 |

**三级（21 条）= 二级 14 条（item_code 改 L3 前缀）+ 以下 7 条新增：**

| # | object_type | category | sub_category | item_code | content |
|---|------------|----------|-------------|-----------|---------|
| 15 | 感知节点设备 | 安全物理环境 | 感知节点设备物理防护 | L3-PES4-03 | 感知节点设备在工作状态所处物理环境应不对感知节点设备的正常工作造成影响，如强干扰、阻挡屏蔽等 |
| 16 | 感知节点设备 | 安全物理环境 | 感知节点设备物理防护 | L3-PES4-04 | 关键感知节点设备应具有可供长时间工作的电力供应（关键网关节点设备应具有持久稳定的电力供应能力） |
| 17 | 感知节点设备 | 安全计算环境 | 感知节点设备安全 | L3-CES4-07 | 应具有对其连接的网关节点设备（包括读卡器）进行身份标识和鉴别的能力 |
| 18 | 感知节点设备 | 安全计算环境 | 感知节点设备安全 | L3-CES4-08 | 应具有对其连接的其他感知节点设备（包括路由节点）进行身份标识和鉴别的能力 |
| 19 | 网关节点设备 | 安全计算环境 | 网关节点设备安全 | L3-CES4-09 | 应具备过滤非法节点和伪造节点所发送的数据的能力 |
| 20 | 网关节点设备 | 安全计算环境 | 网关节点设备安全 | L3-CES4-10 | 授权用户应能够在设备使用过程中对关键密钥进行在线更新 |
| 21 | 网关节点设备 | 安全计算环境 | 网关节点设备安全 | L3-CES4-11 | 授权用户应能够在设备使用过程中对关键配置参数进行在线更新 |

### 4.3 移动互联检查项（35 条）

**二级（14 条）：**

| # | object_type | category | sub_category | item_code | content |
|---|------------|----------|-------------|-----------|---------|
| 1 | 无线接入设备 | 安全物理环境 | 无线接入点的物理位置 | L2-PES3-01 | 应为无线接入设备的安装选择合理位置，避免过度覆盖和电磁干扰 |
| 2 | 无线接入设备 | 安全区域边界 | 边界防护 | L2-ABS3-01 | 应保证有线网络与无线网络边界之间的访问和数据流通过无线接入网关设备 |
| 3 | 无线接入设备 | 安全区域边界 | 访问控制 | L2-ABS3-02 | 无线接入设备应开启接入认证功能，并且禁止使用WEP方式进行认证；如使用口令，长度不小于8位字符 |
| 4 | 无线接入设备 | 安全区域边界 | 入侵防范 | L2-ABS3-03 | 应能够检测到非授权无线接入设备和非授权移动终端的接入行为 |
| 5 | 无线接入设备 | 安全区域边界 | 入侵防范 | L2-ABS3-04 | 应能够检测到针对无线接入设备的网络扫描、DDoS攻击、密钥破解、中间人攻击和欺骗攻击等行为 |
| 6 | 无线接入设备 | 安全区域边界 | 入侵防范 | L2-ABS3-05 | 应能够检测到无线接入设备的SSID广播、WPS等高风险功能的开启状态 |
| 7 | 移动终端 | 安全计算环境 | 移动终端管控 | L2-CES3-01 | 应保证移动终端安装、注册并运行终端管理客户端软件 |
| 8 | 移动终端 | 安全计算环境 | 移动终端管控 | L2-CES3-02 | 移动终端应接受移动终端管理服务端的设备生命周期管理、设备远程控制，如：远程锁定、远程擦除等 |
| 9 | 移动终端 | 安全计算环境 | 移动应用管控 | L2-CES3-03 | 应具有选择应用软件安装、运行的功能 |
| 10 | 移动终端 | 安全计算环境 | 移动应用管控 | L2-CES3-04 | 应只允许可靠证书签名的应用软件安装和运行 |
| 11 | 移动终端 | 安全建设管理 | 移动应用软件采购 | L2-SCM3-01 | 应保证移动终端安装、运行的应用软件来自可靠分发渠道或使用可靠证书签名 |
| 12 | 移动终端 | 安全建设管理 | 移动应用软件采购 | L2-SCM3-02 | 应保证移动终端安装、运行的应用软件由可靠的开发者开发 |
| 13 | 移动终端 | 安全建设管理 | 移动应用软件开发 | L2-SCM3-03 | 应对移动业务应用软件开发者进行资格审查 |
| 14 | 移动终端 | 安全建设管理 | 移动应用软件开发 | L2-SCM3-04 | 应保证开发移动业务应用软件的签名证书合法性 |

**三级（21 条）= 二级 14 条（item_code 改 L3 前缀，部分内容加强）+ 以下 7 条新增：**

三级加强说明：
- L3-ABS3-02 内容改为：无线接入设备应开启接入认证功能，并支持采用认证服务器认证或国家密码管理机构批准的密码模块进行认证
- L3-CES3-04 内容改为：应只允许指定证书签名的应用软件安装和运行
- L3-SCM3-02 内容改为：应保证移动终端安装、运行的应用软件由指定的开发者开发

| # | object_type | category | sub_category | item_code | content |
|---|------------|----------|-------------|-----------|---------|
| 15 | 无线接入设备 | 安全区域边界 | 入侵防范 | L3-ABS3-06 | 应能够阻断非授权无线接入设备或非授权移动终端 |
| 16 | 无线接入设备 | 安全区域边界 | 入侵防范 | L3-ABS3-07 | 应禁用无线接入设备和无线接入网关存在风险的功能（如SSID广播、WEP认证等） |
| 17 | 无线接入设备 | 安全区域边界 | 入侵防范 | L3-ABS3-08 | 应禁止多个AP使用同一个鉴别密钥 |
| 18 | 移动终端 | 安全计算环境 | 移动终端管控 | L3-CES3-05 | 应保证移动终端只用于处理指定业务 |
| 19 | 移动终端 | 安全计算环境 | 移动应用管控 | L3-CES3-06 | 应具有软件白名单功能，应能根据白名单控制应用软件安装、运行 |
| 20 | 移动终端 | 安全计算环境 | 移动应用管控 | L3-CES3-07 | 应具有接受移动终端管理服务端推送的移动应用软件管理策略，并根据该策略对软件实施管控的能力 |
| 21 | 无线接入设备 | 安全运维管理 | 配置管理 | L3-SMS3-01 | 应建立合法无线接入设备和合法移动终端配置库，用于对非法无线接入设备和非法移动终端的识别 |

### 4.4 工业控制检查项（43 条）

**二级（20 条）：**

| # | object_type | category | sub_category | item_code | content |
|---|------------|----------|-------------|-----------|---------|
| 1 | 室外控制设备 | 安全物理环境 | 室外控制设备物理防护 | L2-PES5-01 | 室外控制设备应放置于采用铁板或其他防火材料制作的箱体或装置中并紧固；箱体或装置具有透风、散热、防盗、防雨和防火能力等 |
| 2 | 室外控制设备 | 安全物理环境 | 室外控制设备物理防护 | L2-PES5-02 | 室外控制设备放置应远离强电磁干扰、强热源等环境，如无法避免应及时做好应急处置及检修，保证设备正常运行 |
| 3 | 工业控制设备 | 安全通信网络 | 网络架构 | L2-CNS5-01 | 工业控制系统与企业其他系统之间应划分为两个区域，区域间应采用技术隔离手段 |
| 4 | 工业控制设备 | 安全通信网络 | 网络架构 | L2-CNS5-02 | 工业控制系统内部应根据业务特点划分为不同的安全域，安全域之间应采用技术隔离手段 |
| 5 | 工业控制设备 | 安全通信网络 | 网络架构 | L2-CNS5-03 | 涉及实时控制和数据传输的工业控制系统，应使用独立的网络设备组网，在物理层面上实现与其他数据网及外部公共信息网的安全隔离 |
| 6 | 工业控制设备 | 安全通信网络 | 通信传输 | L2-CNS5-04 | 在工业控制系统内使用广域网进行控制指令或相关数据交换的，应采用加密认证技术手段实现身份认证、访问控制和数据加密传输 |
| 7 | 工业控制设备 | 安全区域边界 | 访问控制 | L2-ABS5-01 | 应在工业控制系统与企业其他系统之间部署访问控制设备，配置访问控制策略，禁止任何穿越区域边界的E-Mail、Web、Telnet、Rlogin、FTP等通用网络服务 |
| 8 | 工业控制设备 | 安全区域边界 | 访问控制 | L2-ABS5-02 | 应在工业控制系统内安全域和安全域之间的边界防护机制失效时，及时进行报警 |
| 9 | 工业控制设备 | 安全区域边界 | 拨号使用控制 | L2-ABS5-03 | 工业控制系统确需使用拨号访问服务的，应限制具有拨号访问权限的用户数量，并采取用户身份鉴别和访问控制等措施 |
| 10 | 工业控制设备 | 安全区域边界 | 无线使用控制 | L2-ABS5-04 | 应对所有参与无线通信的用户（人员、软件进程或设备）提供唯一性标识和鉴别 |
| 11 | 工业控制设备 | 安全区域边界 | 无线使用控制 | L2-ABS5-05 | 应对所有参与无线通信的用户（人员、软件进程或设备）进行授权以及执行使用进行限制 |
| 12 | 工业控制设备 | 安全区域边界 | 无线使用控制 | L2-ABS5-06 | 应对无线通信采取传输加密的安全措施，实现传输报文的机密性保护 |
| 13 | 工业控制设备 | 安全计算环境 | 控制设备安全 | L2-CES5-01 | 控制设备自身应实现相应级别安全通用要求提出的身份鉴别、访问控制和安全审计等安全功能要求；如受条件限制控制设备无法实现上述要求，应由其上位控制或管理设备实现同等功能或通过管理手段控制 |
| 14 | 工业控制设备 | 安全计算环境 | 控制设备安全 | L2-CES5-02 | 应在经过充分测试评估后，在不影响系统安全稳定运行的情况下对控制设备进行补丁更新、固件更新等工作 |
| 15 | 工业控制设备 | 安全计算环境 | 控制设备安全 | L2-CES5-03 | 应关闭或拆除控制设备的软盘驱动、光盘驱动、USB接口、串行口或多余网口等，确需保留的必须通过相关的技术措施实施严格的监控管理 |
| 16 | 工业控制设备 | 安全计算环境 | 控制设备安全 | L2-CES5-04 | 应使用专用设备和专用软件对控制设备进行更新 |
| 17 | 工业控制设备 | 安全计算环境 | 控制设备安全 | L2-CES5-05 | 应在控制设备上线前进行安全性检测，避免控制设备固件中存在恶意代码程序 |
| 18 | 工业控制设备 | 安全建设管理 | 产品采购和使用 | L2-SCM5-01 | 工业控制系统重要设备应通过专业机构的安全性检测后方可采购使用 |
| 19 | 工业控制设备 | 安全建设管理 | 外包软件开发 | L2-SCM5-02 | 应在外包开发合同中规定针对开发单位、供应商的约束条款，包括设备及系统在生命周期内有关保密、禁止关键技术扩散和设备行业专用等方面的内容 |
| 20 | 工业控制设备 | 安全建设管理 | 产品采购和使用 | L2-SCM5-03 | 应密切关注产品供应商发布的补丁或更新程序，在充分测试后及时进行更新 |

**三级（23 条）= 二级 20 条（item_code 改 L3 前缀，部分内容加强）+ 以下 3 条新增：**

三级加强说明：
- L3-CNS5-01 内容改为：工业控制系统与企业其他系统之间应划分为两个区域，区域间应采用单向的技术隔离手段

| # | object_type | category | sub_category | item_code | content |
|---|------------|----------|-------------|-----------|---------|
| 21 | 工业控制设备 | 安全区域边界 | 拨号使用控制 | L3-ABS5-07 | 拨号服务器和客户端均应使用经安全加固的操作系统，并采取数字证书认证、传输加密和访问控制等措施 |
| 22 | 工业控制设备 | 安全区域边界 | 无线使用控制 | L3-ABS5-08 | 应对所有可能被利用进行攻击的无线通信参数进行检查，识别物理环境中发射的未授权无线设备，报告试图接入或干扰控制系统的行为 |
| 23 | 工业控制设备 | 安全计算环境 | 控制设备安全 | L3-CES5-06 | 应支持对控制设备的固件进行完整性校验，防止固件被篡改 |

### 验证

- [ ] 确认 JSON 文件语法正确：`cd backend && python -c "import json; json.load(open('app/seed/check_items_extensions.json', encoding='utf-8')); print('JSON OK')"`
- [ ] 确认国标原生条目数量：移动互联 35 条 + 物联网 35 条 + 工业控制 43 条 = 113 条

---

## Task 5: 编写扩展种子数据 — 行业补充 + 专项技术

**Files:**
- `backend/app/seed/check_items_extensions.json`（追加）

- [ ] 向 `check_items_extensions.json` 追加以下 5 个扩展领域的检查项（基于公开资料整理，后续可修正）。

### 5.1 边缘计算（GA/T 1390.6-2025）— 约 35 条

object_type 用"MEC节点"或"边缘网关"，编码场景码 E（如 `L3-CES-E01`）

**二级（15 条）：**

| # | object_type | category | sub_category | item_code | content |
|---|------------|----------|-------------|-----------|---------|
| 1 | MEC节点 | 安全物理环境 | MEC节点物理防护 | L2-PES-E01 | MEC节点设备应部署在具备物理访问控制的机柜或机房中，防止未授权物理接触 |
| 2 | MEC节点 | 安全物理环境 | MEC节点物理防护 | L2-PES-E02 | MEC节点设备应具备防盗、防破坏的物理保护措施 |
| 3 | MEC节点 | 安全物理环境 | MEC节点物理防护 | L2-PES-E03 | 部署在非受控环境的MEC节点应具备环境监测能力（温湿度、烟感等） |
| 4 | 边缘网关 | 安全物理环境 | MEC节点物理防护 | L2-PES-E04 | 边缘网关设备应具备防水、防尘、抗振动的物理防护能力 |
| 5 | MEC节点 | 安全通信网络 | 通信加密 | L2-CNS-E01 | MEC节点与中心云之间的通信应采用加密传输，保证数据传输的机密性 |
| 6 | MEC节点 | 安全通信网络 | 通信加密 | L2-CNS-E02 | MEC节点与终端设备之间的通信应采用双向身份认证 |
| 7 | 边缘网关 | 安全通信网络 | 网络隔离 | L2-CNS-E03 | 边缘网关应实现边缘网络与核心网络之间的逻辑隔离 |
| 8 | 边缘网关 | 安全通信网络 | 网络隔离 | L2-CNS-E04 | 不同租户的边缘计算资源应实现网络层面的隔离 |
| 9 | MEC节点 | 安全区域边界 | 访问控制 | L2-ABS-E01 | 应在MEC节点部署访问控制策略，限制对边缘计算资源的非授权访问 |
| 10 | MEC节点 | 安全区域边界 | 访问控制 | L2-ABS-E02 | 应对MEC节点的管理接口实施访问控制，仅允许授权管理终端访问 |
| 11 | 边缘网关 | 安全区域边界 | 边界防护 | L2-ABS-E03 | 边缘网关应具备流量过滤和入侵检测能力 |
| 12 | 边缘网关 | 安全区域边界 | 边界防护 | L2-ABS-E04 | 应对边缘节点与外部网络之间的数据交换进行安全审计 |
| 13 | MEC节点 | 安全计算环境 | 容器安全 | L2-CES-E01 | MEC节点上运行的容器镜像应经过安全扫描，不得包含已知高危漏洞 |
| 14 | MEC节点 | 安全计算环境 | 容器安全 | L2-CES-E02 | 应对MEC节点上的容器实施资源限制，防止单个容器耗尽节点资源 |
| 15 | MEC节点 | 安全计算环境 | 安全基线 | L2-CES-E03 | MEC节点操作系统应按照安全基线进行加固配置 |

**三级（20 条）= 二级 15 条（item_code 改 L3 前缀）+ 以下 5 条新增：**

| # | object_type | category | sub_category | item_code | content |
|---|------------|----------|-------------|-----------|---------|
| 16 | MEC节点 | 安全计算环境 | 容器安全 | L3-CES-E04 | 应对容器运行时行为进行监控，检测异常进程、异常网络连接等行为 |
| 17 | MEC节点 | 安全计算环境 | 安全基线 | L3-CES-E05 | 应支持对MEC节点的安全配置进行远程集中管理和基线核查 |
| 18 | MEC节点 | 安全建设管理 | 风险评估 | L3-SCM-E01 | 应定期对边缘计算平台进行安全风险评估，识别新增风险 |
| 19 | MEC节点 | 安全建设管理 | 风险评估 | L3-SCM-E02 | 边缘计算应用上线前应进行安全评审，确保满足安全要求 |
| 20 | MEC节点 | 安全运维管理 | 审计与监控 | L3-SMS-E01 | 应对MEC节点的操作日志进行集中采集和分析，保留不少于6个月 |

### 5.2 大数据（GA/T 1390.7-2025）— 约 42 条

object_type 用"大数据平台"或"数据采集节点"，编码场景码 B

**二级（18 条）：**

| # | object_type | category | sub_category | item_code | content |
|---|------------|----------|-------------|-----------|---------|
| 1 | 大数据平台 | 安全通信网络 | 数据传输加密 | L2-CNS-B01 | 大数据平台各组件之间的数据传输应采用加密措施，防止数据在传输过程中被窃取 |
| 2 | 数据采集节点 | 安全通信网络 | 数据传输加密 | L2-CNS-B02 | 数据采集节点与大数据平台之间的数据传输应采用安全传输协议 |
| 3 | 大数据平台 | 安全通信网络 | 数据传输加密 | L2-CNS-B03 | 应对大数据平台的API接口通信进行加密和身份认证 |
| 4 | 大数据平台 | 安全区域边界 | 数据交换边界 | L2-ABS-B01 | 应在大数据平台与外部系统的数据交换边界部署安全防护措施 |
| 5 | 大数据平台 | 安全区域边界 | 数据交换边界 | L2-ABS-B02 | 应对进入大数据平台的数据进行格式校验和恶意内容检测 |
| 6 | 数据采集节点 | 安全区域边界 | 数据交换边界 | L2-ABS-B03 | 数据采集节点应具备数据源身份验证能力，防止非法数据注入 |
| 7 | 大数据平台 | 安全区域边界 | 数据交换边界 | L2-ABS-B04 | 应对大数据平台的数据导出操作进行审批和记录 |
| 8 | 大数据平台 | 安全计算环境 | 数据脱敏 | L2-CES-B01 | 应对包含个人信息和敏感数据的字段实施脱敏处理后方可用于开发测试和数据分析 |
| 9 | 大数据平台 | 安全计算环境 | 数据脱敏 | L2-CES-B02 | 应支持静态脱敏和动态脱敏两种方式，根据使用场景选择合适的脱敏策略 |
| 10 | 大数据平台 | 安全计算环境 | 数据分类分级 | L2-CES-B03 | 应建立数据分类分级制度，对平台中的数据按照敏感程度进行分类标记 |
| 11 | 大数据平台 | 安全计算环境 | 数据分类分级 | L2-CES-B04 | 应根据数据分类分级结果实施差异化的访问控制策略 |
| 12 | 大数据平台 | 安全计算环境 | 数据溯源 | L2-CES-B05 | 应记录数据的来源、加工和流转过程，支持数据血缘追溯 |
| 13 | 大数据平台 | 安全计算环境 | 数据溯源 | L2-CES-B06 | 应对数据的访问和使用行为进行审计记录，支持事后追溯 |
| 14 | 大数据平台 | 安全管理中心 | 数据资产管理 | L2-SMC-B01 | 应建立数据资产目录，对大数据平台中的数据资产进行统一登记和管理 |
| 15 | 大数据平台 | 安全管理中心 | 数据资产管理 | L2-SMC-B02 | 应定期对数据资产进行盘点，识别无主数据和过期数据 |
| 16 | 大数据平台 | 安全管理中心 | 数据资产管理 | L2-SMC-B03 | 应对数据资产的共享和开放进行审批管理 |
| 17 | 大数据平台 | 安全运维管理 | 数据生命周期管理 | L2-SMS-B01 | 应制定数据保留策略，对超过保留期限的数据进行安全销毁 |
| 18 | 大数据平台 | 安全运维管理 | 数据生命周期管理 | L2-SMS-B02 | 应对数据备份和恢复过程进行安全管理，确保备份数据的完整性和可用性 |

**三级（24 条）= 二级 18 条（item_code 改 L3 前缀）+ 以下 6 条新增：**

| # | object_type | category | sub_category | item_code | content |
|---|------------|----------|-------------|-----------|---------|
| 19 | 大数据平台 | 安全计算环境 | 数据脱敏 | L3-CES-B07 | 应对脱敏效果进行验证，确保脱敏后的数据无法被反向还原 |
| 20 | 大数据平台 | 安全计算环境 | 数据分类分级 | L3-CES-B08 | 应支持自动化的数据分类分级识别，对新入库数据自动进行敏感度标记 |
| 21 | 大数据平台 | 安全计算环境 | 数据溯源 | L3-CES-B09 | 应支持跨平台的数据血缘追溯，记录数据在不同系统间的流转路径 |
| 22 | 大数据平台 | 安全区域边界 | 数据交换边界 | L3-ABS-B05 | 应对大数据平台的批量数据导出实施数据量阈值告警 |
| 23 | 数据采集节点 | 安全通信网络 | 数据传输加密 | L3-CNS-B04 | 数据采集节点应支持数据传输完整性校验，防止数据在传输过程中被篡改 |
| 24 | 大数据平台 | 安全运维管理 | 数据生命周期管理 | L3-SMS-B03 | 应对数据销毁过程进行审计，确保敏感数据被彻底清除且不可恢复 |

### 5.3 IPv6（GA/T 1390.8-2025）— 约 28 条

object_type 用"IPv6网络设备"或"IPv6安全设备"，编码场景码 V

**二级（12 条）：**

| # | object_type | category | sub_category | item_code | content |
|---|------------|----------|-------------|-----------|---------|
| 1 | IPv6网络设备 | 安全通信网络 | IPv6地址管理 | L2-CNS-V01 | 应建立IPv6地址分配和管理制度，对IPv6地址的申请、分配、回收进行统一管理 |
| 2 | IPv6网络设备 | 安全通信网络 | IPv6地址管理 | L2-CNS-V02 | 应对IPv6网络中的地址自动配置（SLAAC）进行安全管控，防止地址欺骗 |
| 3 | IPv6网络设备 | 安全通信网络 | 路由安全 | L2-CNS-V03 | 应对IPv6路由协议实施认证机制，防止路由欺骗和路由劫持 |
| 4 | IPv6网络设备 | 安全通信网络 | 路由安全 | L2-CNS-V04 | 应对IPv6网络中的NDP（邻居发现协议）进行安全防护，防止NDP欺骗攻击 |
| 5 | IPv6安全设备 | 安全区域边界 | IPv6防火墙 | L2-ABS-V01 | 安全设备应支持基于IPv6地址的访问控制策略配置 |
| 6 | IPv6安全设备 | 安全区域边界 | IPv6防火墙 | L2-ABS-V02 | 安全设备应能够识别和过滤IPv6扩展头中的异常报文 |
| 7 | IPv6网络设备 | 安全区域边界 | 过渡机制安全 | L2-ABS-V03 | 采用IPv4/IPv6双栈或隧道过渡机制的，应对隧道流量进行安全检测和过滤 |
| 8 | IPv6网络设备 | 安全区域边界 | 过渡机制安全 | L2-ABS-V04 | 应对IPv6过渡机制中的协议转换进行安全审计，防止利用过渡机制绕过安全策略 |
| 9 | IPv6网络设备 | 安全计算环境 | IPv6协议栈安全 | L2-CES-V01 | 网络设备和主机的IPv6协议栈应及时更新补丁，修复已知安全漏洞 |
| 10 | IPv6网络设备 | 安全计算环境 | IPv6协议栈安全 | L2-CES-V02 | 应关闭不必要的IPv6服务和端口，减少攻击面 |
| 11 | IPv6安全设备 | 安全计算环境 | IPv6协议栈安全 | L2-CES-V03 | IPv6安全设备应支持对IPv6流量的深度包检测（DPI） |
| 12 | IPv6网络设备 | 安全运维管理 | IPv6资产管理 | L2-SMS-V01 | 应建立IPv6网络资产清单，记录所有启用IPv6的设备和服务 |

**三级（16 条）= 二级 12 条（item_code 改 L3 前缀）+ 以下 4 条新增：**

| # | object_type | category | sub_category | item_code | content |
|---|------------|----------|-------------|-----------|---------|
| 13 | IPv6网络设备 | 安全通信网络 | IPv6地址管理 | L3-CNS-V05 | 应部署IPv6地址溯源机制，支持根据IPv6地址追溯到具体用户或设备 |
| 14 | IPv6安全设备 | 安全区域边界 | IPv6防火墙 | L3-ABS-V05 | 应支持基于IPv6流标签的流量分类和安全策略实施 |
| 15 | IPv6网络设备 | 安全计算环境 | IPv6协议栈安全 | L3-CES-V04 | 应对IPv6网络中的ICMPv6报文进行安全过滤，仅允许必要的ICMPv6类型通过 |
| 16 | IPv6网络设备 | 安全运维管理 | IPv6资产管理 | L3-SMS-V02 | 应定期扫描网络中未授权启用的IPv6服务，及时发现和处置安全隐患 |

### 5.4 区块链（GA/T 1390.9-2025）— 约 35 条

object_type 用"区块链节点"或"智能合约系统"，编码场景码 K

**二级（15 条）：**

| # | object_type | category | sub_category | item_code | content |
|---|------------|----------|-------------|-----------|---------|
| 1 | 区块链节点 | 安全通信网络 | P2P网络安全 | L2-CNS-K01 | 区块链节点之间的P2P通信应采用加密传输，防止数据被窃听 |
| 2 | 区块链节点 | 安全通信网络 | P2P网络安全 | L2-CNS-K02 | 应对区块链网络中的节点通信进行身份认证，防止伪造节点接入 |
| 3 | 区块链节点 | 安全通信网络 | 共识安全 | L2-CNS-K03 | 应选择经过安全验证的共识算法，确保在一定比例节点异常时系统仍能正常运行 |
| 4 | 区块链节点 | 安全通信网络 | 共识安全 | L2-CNS-K04 | 应对共识过程进行监控，及时发现和处置共识异常行为 |
| 5 | 区块链节点 | 安全区域边界 | 节点准入控制 | L2-ABS-K01 | 应建立节点准入机制，对申请加入区块链网络的节点进行身份审核 |
| 6 | 区块链节点 | 安全区域边界 | 节点准入控制 | L2-ABS-K02 | 应具备将异常节点或恶意节点从网络中移除的能力 |
| 7 | 区块链节点 | 安全区域边界 | 节点准入控制 | L2-ABS-K03 | 应对区块链节点的RPC接口进行访问控制，防止未授权调用 |
| 8 | 智能合约系统 | 安全计算环境 | 智能合约审计 | L2-CES-K01 | 智能合约上线前应进行代码安全审计，检查常见漏洞（如重入攻击、整数溢出等） |
| 9 | 智能合约系统 | 安全计算环境 | 智能合约审计 | L2-CES-K02 | 应建立智能合约的版本管理和升级机制，支持合约的安全更新 |
| 10 | 区块链节点 | 安全计算环境 | 密钥管理 | L2-CES-K03 | 应对区块链节点的私钥进行安全存储，采用硬件安全模块或加密存储 |
| 11 | 区块链节点 | 安全计算环境 | 密钥管理 | L2-CES-K04 | 应建立密钥备份和恢复机制，防止密钥丢失导致资产损失 |
| 12 | 区块链节点 | 安全计算环境 | 数据上链 | L2-CES-K05 | 应对上链数据进行合规性检查，防止违法违规信息上链 |
| 13 | 区块链节点 | 安全建设管理 | 链上数据治理 | L2-SCM-K01 | 应建立链上数据治理制度，明确数据上链的审批流程和责任主体 |
| 14 | 区块链节点 | 安全建设管理 | 链上数据治理 | L2-SCM-K02 | 应具备对链上违规数据进行标记或屏蔽的技术能力 |
| 15 | 区块链节点 | 安全运维管理 | 节点运维 | L2-SMS-K01 | 应对区块链节点的运行状态进行持续监控，包括区块同步状态、交易处理性能等 |

**三级（20 条）= 二级 15 条（item_code 改 L3 前缀）+ 以下 5 条新增：**

| # | object_type | category | sub_category | item_code | content |
|---|------------|----------|-------------|-----------|---------|
| 16 | 智能合约系统 | 安全计算环境 | 智能合约审计 | L3-CES-K06 | 应采用形式化验证等方法对关键智能合约进行深度安全验证 |
| 17 | 区块链节点 | 安全计算环境 | 密钥管理 | L3-CES-K07 | 应支持密钥的定期轮换机制，降低密钥泄露风险 |
| 18 | 智能合约系统 | 安全计算环境 | 数据上链 | L3-CES-K08 | 应对链上敏感数据进行加密存储，仅授权用户可解密访问 |
| 19 | 区块链节点 | 安全运维管理 | 节点运维 | L3-SMS-K02 | 应建立区块链网络的应急响应预案，包括分叉处理、节点故障恢复等场景 |
| 20 | 区块链节点 | 安全通信网络 | 共识安全 | L3-CNS-K05 | 应具备抵御51%攻击或拜占庭攻击的能力，确保共识结果的可靠性 |

### 5.5 5G接入（GA/T 2348-2025）— 约 32 条

object_type 用"5G基站"或"UPF设备"，编码场景码 G

**二级（14 条）：**

| # | object_type | category | sub_category | item_code | content |
|---|------------|----------|-------------|-----------|---------|
| 1 | 5G基站 | 安全物理环境 | 基站物理防护 | L2-PES-G01 | 5G基站设备应部署在具备物理访问控制的场所，防止未授权人员接触设备 |
| 2 | 5G基站 | 安全物理环境 | 基站物理防护 | L2-PES-G02 | 室外部署的5G基站应具备防盗、防破坏、防雷击的物理防护措施 |
| 3 | 5G基站 | 安全物理环境 | 基站物理防护 | L2-PES-G03 | 5G基站设备应具备断电保护和来电自启动能力 |
| 4 | 5G基站 | 安全通信网络 | 空口加密 | L2-CNS-G01 | 5G空口通信应启用加密保护，防止无线信号被窃听 |
| 5 | 5G基站 | 安全通信网络 | 空口加密 | L2-CNS-G02 | 应支持5G NAS层和AS层的独立加密和完整性保护 |
| 6 | UPF设备 | 安全通信网络 | 切片隔离 | L2-CNS-G03 | 不同网络切片之间应实现数据面的安全隔离，防止切片间的数据泄露 |
| 7 | UPF设备 | 安全通信网络 | 切片隔离 | L2-CNS-G04 | 应对网络切片的资源使用进行监控和限制，防止单个切片耗尽共享资源 |
| 8 | 5G基站 | 安全区域边界 | UE认证 | L2-ABS-G01 | 应支持5G AKA（认证和密钥协商）协议，对用户设备进行双向认证 |
| 9 | 5G基站 | 安全区域边界 | UE认证 | L2-ABS-G02 | 应支持SUPI（用户永久标识）的隐私保护，使用SUCI（用户隐藏标识）进行传输 |
| 10 | UPF设备 | 安全区域边界 | 切片边界 | L2-ABS-G03 | 应在网络切片边界部署安全策略，控制跨切片的数据流动 |
| 11 | UPF设备 | 安全区域边界 | 切片边界 | L2-ABS-G04 | 应对UPF设备的N6接口（连接数据网络）实施访问控制和流量过滤 |
| 12 | UPF设备 | 安全计算环境 | 核心网元安全 | L2-CES-G01 | 5G核心网网元应按照安全基线进行加固配置，关闭不必要的服务和端口 |
| 13 | UPF设备 | 安全计算环境 | 核心网元安全 | L2-CES-G02 | 应对5G核心网网元之间的服务化接口（SBI）通信进行TLS加密和OAuth2.0认证 |
| 14 | 5G基站 | 安全运维管理 | 基站运维 | L2-SMS-G01 | 应对5G基站的配置变更进行审批和记录，防止未授权配置修改 |

**三级（18 条）= 二级 14 条（item_code 改 L3 前缀）+ 以下 4 条新增：**

| # | object_type | category | sub_category | item_code | content |
|---|------------|----------|-------------|-----------|---------|
| 15 | UPF设备 | 安全计算环境 | 核心网元安全 | L3-CES-G03 | 应对5G核心网的网络功能虚拟化（NFV）环境进行安全加固，包括虚拟机隔离和镜像完整性校验 |
| 16 | UPF设备 | 安全计算环境 | 核心网元安全 | L3-CES-G04 | 应支持对5G网络切片的安全策略进行动态调整，适应不同业务场景的安全需求 |
| 17 | 5G基站 | 安全运维管理 | 基站运维 | L3-SMS-G02 | 应建立5G网络的安全态势感知能力，实时监控网络安全状态和威胁事件 |
| 18 | 5G基站 | 安全通信网络 | 空口加密 | L3-CNS-G05 | 应支持256位密钥长度的加密算法，满足高安全等级业务的加密需求 |

### 验证

- [ ] 确认 JSON 文件语法正确：`cd backend && python -c "import json; data=json.load(open('app/seed/check_items_extensions.json', encoding='utf-8')); print(f'Total: {len(data)} items')"`
- [ ] 确认行业补充+专项条目数量：边缘计算 35 + 大数据 42 + IPv6 28 + 区块链 35 + 5G接入 32 = 172 条
- [ ] 确认总计：113（国标原生）+ 172（行业补充+专项）= 285 条

---

## Task 6: 前端 — 题库管理页面变更（QuestionBank.vue）

**Files:**
- `frontend/src/views/QuestionBank.vue`

### 6.1 扩展 OBJECT_TYPES 数组

- [ ] 将 `OBJECT_TYPES` 数组扩展为包含全部 29 种对象类型：

```javascript
const OBJECT_TYPES = [
  '物理机房', '网络设备', '安全设备', '服务器/存储', '终端设备',
  '其他系统或设备', '系统管理软件/平台', '业务应用系统/平台',
  '数据资源', '安全相关人员', '安全管理文档', '漏洞扫描', '渗透测试',
  '感知节点设备', '网关节点设备', '工业控制设备', '室外控制设备',
  '无线接入设备', '移动终端', 'MEC节点', '边缘网关',
  '大数据平台', '数据采集节点', 'IPv6网络设备', 'IPv6安全设备',
  '区块链节点', '智能合约系统', '5G基站', 'UPF设备'
]
```

### 6.2 新增扩展类型和标准来源常量

- [ ] 在 `OBJECT_TYPES` 之后添加：

```javascript
const EXTENSION_TYPES = [
  { label: '全部', value: '' },
  { label: '基础通用', value: 'base' },
  { label: '云计算', value: '云计算' },
  { label: '移动互联', value: '移动互联' },
  { label: '物联网', value: '物联网' },
  { label: '工业控制', value: '工业控制' },
  { label: '边缘计算', value: '边缘计算' },
  { label: '大数据', value: '大数据' },
  { label: 'IPv6', value: 'IPv6' },
  { label: '区块链', value: '区块链' },
  { label: '5G接入', value: '5G接入' },
]

const STANDARD_REFS = [
  { label: '全部', value: '' },
  { label: 'GB/T 22239-2019', value: 'GB/T 22239-2019' },
  { label: 'GA/T 1390.6-2025', value: 'GA/T 1390.6-2025' },
  { label: 'GA/T 1390.7-2025', value: 'GA/T 1390.7-2025' },
  { label: 'GA/T 1390.8-2025', value: 'GA/T 1390.8-2025' },
  { label: 'GA/T 1390.9-2025', value: 'GA/T 1390.9-2025' },
  { label: 'GA/T 2348-2025', value: 'GA/T 2348-2025' },
]

// 扩展类型 → 标准号映射（用于表单自动填充）
const EXTENSION_STANDARD_MAP = {
  '云计算': 'GB/T 22239-2019',
  '移动互联': 'GB/T 22239-2019',
  '物联网': 'GB/T 22239-2019',
  '工业控制': 'GB/T 22239-2019',
  '边缘计算': 'GA/T 1390.6-2025',
  '大数据': 'GA/T 1390.7-2025',
  'IPv6': 'GA/T 1390.8-2025',
  '区块链': 'GA/T 1390.9-2025',
  '5G接入': 'GA/T 2348-2025',
}

// 扩展类型颜色标签
const getExtensionTagType = (extType) => {
  if (!extType) return 'info'           // 基础通用 → 灰色
  const national = ['云计算', '移动互联', '物联网', '工业控制']
  if (national.includes(extType)) return ''  // 国标原生 → 蓝色（默认）
  if (extType === '5G接入') return 'warning' // 专项技术 → 橙色（与行业补充同色）
  return 'warning'                       // 行业补充 → 橙色
}

const getExtensionLabel = (extType) => extType || '基础通用'
```

### 6.3 筛选器新增

- [ ] 在 `filters` ref 中新增字段：

```javascript
const filters = ref({
  object_type: '', security_level: '', keyword: '',
  extension_type: '', standard_ref: '',
  page: 1, page_size: 20
})
```

- [ ] 在模板的筛选表单中，"等保级别"之后添加两个下拉：

```html
<el-form-item label="扩展类型">
  <el-select v-model="filters.extension_type" clearable placeholder="全部" @change="loadData" style="width: 130px;">
    <el-option v-for="t in EXTENSION_TYPES" :key="t.value" :label="t.label" :value="t.value" />
  </el-select>
</el-form-item>
<el-form-item label="标准来源">
  <el-select v-model="filters.standard_ref" clearable placeholder="全部" @change="loadData" style="width: 170px;">
    <el-option v-for="t in STANDARD_REFS" :key="t.value" :label="t.label" :value="t.value" />
  </el-select>
</el-form-item>
```

### 6.4 表格列调整

- [ ] 移除"云扩展"列（删除整个 `<el-table-column label="云扩展" ...>` 块）

- [ ] 在"检查内容"列之后、"操作"列之前，新增两列：

```html
<el-table-column label="扩展类型" width="100" align="center">
  <template #default="{ row }">
    <el-tag :type="getExtensionTagType(row.extension_type)" size="small">
      {{ getExtensionLabel(row.extension_type) }}
    </el-tag>
  </template>
</el-table-column>
<el-table-column prop="standard_ref" label="标准来源" width="160" />
```

### 6.5 表单调整

- [ ] 修改 `form` ref 初始值：

```javascript
const form = ref({
  object_type: '', security_level: '三级', category: '', sub_category: '',
  item_code: '', content: '', is_cloud_extension: false,
  extension_type: '', standard_ref: ''
})
```

- [ ] 在 `openCreate` 和 `openEdit` 中同步新字段：

```javascript
const openCreate = () => {
  editingId.value = null
  form.value = {
    object_type: '', security_level: '三级', category: '', sub_category: '',
    item_code: '', content: '', is_cloud_extension: false,
    extension_type: '', standard_ref: ''
  }
  showDialog.value = true
}

const openEdit = (item) => {
  editingId.value = item.id
  form.value = {
    object_type: item.object_type, security_level: item.security_level,
    category: item.category, sub_category: item.sub_category || '',
    item_code: item.item_code || '', content: item.content,
    is_cloud_extension: item.is_cloud_extension,
    extension_type: item.extension_type || '',
    standard_ref: item.standard_ref || ''
  }
  showDialog.value = true
}
```

- [ ] 新增 watch 实现扩展类型选择后自动填充标准号：

```javascript
import { ref, onMounted, watch } from 'vue'

watch(() => form.value.extension_type, (newVal) => {
  if (newVal && EXTENSION_STANDARD_MAP[newVal]) {
    form.value.standard_ref = EXTENSION_STANDARD_MAP[newVal]
  }
})
```

- [ ] 在对话框表单中，移除"云计算扩展"开关，替换为：

```html
<el-form-item label="扩展类型">
  <el-select v-model="form.extension_type" clearable placeholder="基础通用（不选）" style="width: 100%;">
    <el-option v-for="t in EXTENSION_TYPES.filter(t => t.value && t.value !== 'base')" :key="t.value" :label="t.label" :value="t.value" />
  </el-select>
</el-form-item>
<el-form-item label="标准来源">
  <el-select v-model="form.standard_ref" clearable placeholder="选择标准" style="width: 100%;">
    <el-option v-for="t in STANDARD_REFS.filter(t => t.value)" :key="t.value" :label="t.label" :value="t.value" />
  </el-select>
</el-form-item>
```

### 验证

- [ ] 前端构建无报错：`cd frontend && npm run build`

---

## Task 7: 前端 — 评测对象管理页面变更（ProjectDetail.vue）

**Files:**
- `frontend/src/views/ProjectDetail.vue`

### 7.1 OBJECT_TYPES 改为分组结构

- [ ] 将 `ProjectDetail.vue` 中的 `OBJECT_TYPES` 数组替换为分组结构：

```javascript
const OBJECT_TYPE_GROUPS = [
  {
    label: '通用',
    types: ['物理机房', '网络设备', '安全设备', '服务器/存储', '终端设备',
            '其他系统或设备', '系统管理软件/平台', '业务应用系统/平台',
            '数据资源', '安全相关人员', '安全管理文档', '漏洞扫描', '渗透测试']
  },
  { label: '物联网', types: ['感知节点设备', '网关节点设备'] },
  { label: '工业控制', types: ['工业控制设备', '室外控制设备'] },
  { label: '移动互联', types: ['无线接入设备', '移动终端'] },
  { label: '边缘计算', types: ['MEC节点', '边缘网关'] },
  { label: '大数据', types: ['大数据平台', '数据采集节点'] },
  { label: 'IPv6', types: ['IPv6网络设备', 'IPv6安全设备'] },
  { label: '区块链', types: ['区块链节点', '智能合约系统'] },
  { label: '5G接入', types: ['5G基站', 'UPF设备'] },
]

// 保留扁平数组用于其他逻辑
const OBJECT_TYPES = OBJECT_TYPE_GROUPS.flatMap(g => g.types)
```

### 7.2 对象类型选择器改为分组

- [ ] 将对话框中的 `<el-select>` 改为使用 `<el-option-group>`：

```html
<el-form-item label="对象类型" required>
  <el-select v-model="objForm.object_type" placeholder="选择类型" style="width: 100%;">
    <el-option-group v-for="group in OBJECT_TYPE_GROUPS" :key="group.label" :label="group.label">
      <el-option v-for="t in group.types" :key="t" :label="t" :value="t" />
    </el-option-group>
  </el-select>
</el-form-item>
```

### 验证

- [ ] 前端构建无报错：`cd frontend && npm run build`

---

## Task 8: 前端 — 统计看板变更（Dashboard.vue + statistics.py）

**Files:**
- `backend/app/routers/statistics.py`
- `frontend/src/views/Dashboard.vue`
- `frontend/src/api/index.js`

### 8.1 后端新增扩展类型统计 API

- [ ] 在 `backend/app/routers/statistics.py` 中导入 `CheckItem`（已导入），新增全局统计端点：

```python
from app.models.models import EvalObject, CheckRecord, Issue, CheckItem

# 在文件末尾添加新的路由器用于全局统计
global_stats_router = APIRouter(prefix="/api/stats", tags=["global_statistics"])

@global_stats_router.get("/extension-distribution")
def get_extension_distribution(db: Session = Depends(get_db)):
    """按扩展类型统计题库分布"""
    from sqlalchemy import case
    results = db.query(
        func.coalesce(CheckItem.extension_type, '基础通用').label('ext_type'),
        func.count(CheckItem.id).label('count')
    ).group_by('ext_type').all()
    return [{"name": r.ext_type, "count": r.count} for r in results]
```

- [ ] 在 `backend/app/main.py` 中注册新路由器：

```python
from app.routers.statistics import global_stats_router
app.include_router(global_stats_router)
```

### 8.2 前端 API 新增

- [ ] 在 `frontend/src/api/index.js` 中添加：

```javascript
// Global Statistics
export const getExtensionDistribution = () => api.get('/stats/extension-distribution')
```

### 8.3 Dashboard.vue 新增饼图

- [ ] 在 `frontend/src/views/Dashboard.vue` 的 `<script setup>` 中导入新 API 并添加数据：

```javascript
import { getStats, getProject, getExtensionDistribution } from '../api'

const extensionStats = ref(null)

const EXTENSION_COLORS = {
  '基础通用': '#909399',
  '云计算': '#409EFF',
  '移动互联': '#409EFF',
  '物联网': '#409EFF',
  '工业控制': '#409EFF',
  '边缘计算': '#E6A23C',
  '大数据': '#E6A23C',
  'IPv6': '#E6A23C',
  '区块链': '#E6A23C',
  '5G接入': '#9B59B6',
}

const extensionPieOption = computed(() => {
  if (!extensionStats.value) return {}
  const data = extensionStats.value.map(item => ({
    name: item.name,
    value: item.count,
    itemStyle: { color: EXTENSION_COLORS[item.name] || '#909399' }
  })).filter(d => d.value > 0)
  return {
    title: { text: '题库扩展类型分布', left: 'center' },
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0 },
    series: [{ type: 'pie', radius: ['40%', '70%'], data, label: { formatter: '{b}\n{d}%' } }]
  }
})
```

- [ ] 修改 `loadData` 函数，并行加载扩展统计：

```javascript
const loadData = async () => {
  const [pRes, sRes, eRes] = await Promise.all([
    getProject(projectId.value),
    getStats(projectId.value),
    getExtensionDistribution()
  ])
  project.value = pRes.data
  stats.value = sRes.data
  extensionStats.value = eRes.data
}
```

- [ ] 在模板中，在问题风险分布饼图之后添加扩展类型饼图：

```html
<el-row :gutter="16" style="margin-top: 16px;">
  <el-col :span="12">
    <el-card><v-chart :option="extensionPieOption" style="height: 350px;" /></el-card>
  </el-col>
</el-row>
```

### 验证

- [ ] 前端构建无报错：`cd frontend && npm run build`
- [ ] 后端语法检查：`cd backend && python -c "from app.routers.statistics import global_stats_router; print('OK')"`

---

## Task 9: 验证与提交

### 9.1 后端语法检查

- [ ] `cd backend && python -c "from app.main import app; print('FastAPI app OK')"`

### 9.2 前端构建

- [ ] `cd frontend && npm run build`

### 9.3 验证种子数据导入

- [ ] 删除旧数据库（如果存在）：`rm -f backend/data/mlps.db`
- [ ] 启动后端验证种子导入：`cd backend && python -c "from app.main import app; print('Seed OK')"`
- [ ] 验证数据量：`cd backend && python -c "from app.database import SessionLocal; from app.models.models import CheckItem; db=SessionLocal(); total=db.query(CheckItem).count(); ext=db.query(CheckItem).filter(CheckItem.extension_type.isnot(None)).count(); print(f'Total: {total}, Extensions: {ext}'); db.close()"`

### 9.4 Git 提交

- [ ] `cd /path/to/mlps-app && git add -A`
- [ ] `git commit -m "feat: 扩展等保题库，新增9大扩展领域~285条检查项

- 数据模型：CheckItem 新增 extension_type/standard_ref 字段
- 枚举：EvalObjectType 新增 16 种对象类型
- 种子数据：新增 check_items_extensions.json（~285条）
- 覆盖：移动互联/物联网/工业控制/边缘计算/大数据/IPv6/区块链/5G接入
- API：check_items 新增 extension_type/standard_ref 查询参数
- 前端：题库管理支持扩展类型筛选和颜色标签
- 前端：评测对象类型选择器按扩展领域分组
- 前端：统计看板新增扩展类型分布饼图
- 迁移：自动检测并添加新列，云计算记录自动标记"`
