# 求职 Agent - Qing Agent

**版本：** v1.1  
**状态：** ✅ 核心模块已完成

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd qing-agent
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件（可选）
```

### 3. 启动服务

```bash
# 开发模式
fastapi dev main.py

# 或生产模式
fastapi run main.py

# 或直接用 uvicorn
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. 访问 API

- **服务地址：** http://127.0.0.1:8000
- **API 文档：** http://127.0.0.1:8000/docs
- **健康检查：** http://127.0.0.1:8000/health

---

## 📁 项目结构

```
qing-agent/
├── main.py                     # FastAPI 入口
├── agent/
│   ├── agent_core.py           # Agent 核心
│   └── planner.py              # 任务规划器
├── pipeline/
│   └── job_pipeline.py         # 求职流水线
├── services/
│   ├── resume_service.py       # 简历服务
│   ├── job_service.py          # 职位服务
│   └── match_service.py        # 匹配服务
├── platform/
│   ├── base_adapter.py         # 适配器基类
│   ├── boss_adapter.py         # BOSS 适配器
│   └── adapter_factory.py      # 适配器工厂
├── tools/
│   ├── resume_parser.py        # 简历解析
│   ├── jd_parser.py            # JD 解析
│   ├── matcher.py              # 匹配引擎（7 维）
│   ├── industry_matcher.py     # 行业匹配
│   └── recommender.py          # 推荐引擎
├── database/
│   ├── db.py                   # 数据库连接
│   ├── models.py               # 数据模型
│   └── cache.py                # 缓存管理
├── routes/                     # API 路由（待实现）
├── config/
│   └── settings.py             # 配置
├── data/
│   ├── industry_tree.json      # 行业树
│   └── qing_agent.db           # SQLite 数据库
├── logs/                       # 日志
├── tests/                      # 测试
├── requirements.txt            # 依赖
└── README.md                   # 说明
```

---

## ✅ 已完成模块

| 模块 | 文件 | 状态 |
|------|------|------|
| **行业匹配系统** | `tools/industry_matcher.py` | ✅ 完成 |
| **匹配引擎（7 维）** | `tools/matcher.py` | ✅ 完成 |
| **推荐引擎** | `tools/recommender.py` | ✅ 完成 |
| **简历解析器** | `tools/resume_parser.py` | ✅ 框架完成 |
| **JD 解析器** | `tools/jd_parser.py` | ✅ 框架完成 |
| **平台适配器基类** | `platform/base_adapter.py` | ✅ 完成 |
| **BOSS 适配器** | `platform/boss_adapter.py` | ✅ 框架完成 |
| **适配器工厂** | `platform/adapter_factory.py` | ✅ 完成 |
| **任务流水线** | `pipeline/job_pipeline.py` | ✅ 完成 |
| **Agent 规划器** | `agent/planner.py` | ✅ 完成 |
| **Agent 核心** | `agent/agent_core.py` | ✅ 完成 |
| **简历服务** | `services/resume_service.py` | ✅ 完成 |
| **职位服务** | `services/job_service.py` | ✅ 完成 |
| **匹配服务** | `services/match_service.py` | ✅ 完成 |
| **数据库模型** | `database/models.py` | ✅ 完成 |
| **缓存管理** | `database/cache.py` | ✅ 完成 |
| **配置文件** | `config/settings.py` | ✅ 完成 |
| **FastAPI 入口** | `main.py` | ✅ 完成 |

---

## 🔧 测试

### 测试行业匹配

```bash
cd qing-agent
python tools/industry_matcher.py
```

### 测试匹配引擎

```bash
python tools/matcher.py
```

### 测试 API

```bash
# 启动服务
fastapi dev main.py

# 访问测试端点
curl http://127.0.0.1:8000/api/test/match
curl http://127.0.0.1:8000/api/test/industry
```

---

## 📊 匹配算法（7 维）

```
match_score = 
  industry * 0.25 +   # 行业匹配
  skill * 0.25 +      # 技能匹配
  experience * 0.15 + # 经验匹配
  salary * 0.10 +     # 薪资匹配
  location * 0.10 +   # 地点匹配
  education * 0.10 +  # 学历匹配
  tools * 0.05        # 工具匹配
```

---

## 🎯 下一步

### 待完成

- [ ] 完善简历解析器（AI 提取）
- [ ] 完善 JD 解析器（AI 提取）
- [ ] 实现 BOSS 适配器浏览器自动化
- [ ] 实现智联招聘适配器
- [ ] 实现 API 路由（users, jobs, matches, applications）
- [ ] 添加单元测试
- [ ] 添加前端 UI（可选）

---

## 📝 使用说明

### 1. 创建用户

```python
from services.resume_service import ResumeService

service = ResumeService()
user = await service.parse_and_save("resume.docx")
```

### 2. 搜索职位

```python
from services.job_service import JobService

service = JobService()
jobs = await service.search("品牌策划", "深圳")
```

### 3. 计算匹配

```python
from services.match_service import MatchService

service = MatchService()
match = await service.calculate(user_profile, job_profile)
```

### 4. 执行 Pipeline

```python
from pipeline.job_pipeline import JobPipeline

pipeline = JobPipeline()
results = await pipeline.run(user_id=1, keywords=["品牌策划"])
```

---

## 📄 许可证

MIT License

---

**创建时间：** 2026-03-08  
**作者：** 青（OpenClaw Agent）
