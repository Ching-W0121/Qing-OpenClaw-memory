# 求职 Agent - Qing Agent

**版本:** v1.3.0 (JWT 认证版)  
**状态:** ✅ 阶段 1-5 已完成 (75%)  
**最后更新:** 2026-03-10

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

# 编辑 .env 文件，配置 Auth0 JWT 认证
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

- **服务地址:** http://127.0.0.1:8000
- **API 文档:** http://127.0.0.1:8000/docs
- **健康检查:** http://127.0.0.1:8000/health

---

## 📁 项目结构

```
qing-agent/
├── main.py                     # FastAPI 入口 (v1.3.0)
├── requirements.txt            # 依赖列表
├── .env                        # 环境变量 (Auth0 配置)
├── README.md                   # 本文件
│
├── auth/                       # JWT 认证模块 ⭐ NEW
│   ├── __init__.py
│   └── jwt_auth.py            # Auth0 JWT 验证
│
├── routes/                     # API 路由 ⭐ NEW
│   ├── users.py               # 用户管理
│   ├── jobs.py                # 职位管理
│   ├── matches.py             # 匹配推荐
│   └── applications.py        # 投递管理
│
├── platform/                   # 平台适配器
│   ├── base_adapter.py        # 基础适配器
│   ├── boss_adapter.py        # BOSS 直聘 (⚠️ 网页端受限)
│   └── zhilian_adapter.py     # 智联招聘 ✅ 可用
│
├── tools/                      # 核心工具
│   ├── matcher.py             # 匹配引擎 (7 维)
│   ├── industry_matcher.py    # 行业匹配
│   ├── jd_parser.py           # JD 解析器
│   ├── resume_parser.py       # 简历解析器
│   ├── circuit_breaker.py     # 熔断器
│   ├── operation_limiter.py   # 限流器
│   └── session_manager.py     # 会话管理
│
├── tests/                      # 测试套件
│   ├── test_integration.py    # 集成测试
│   ├── test_jwt_auth.py       # JWT 测试
│   └── test_boss_*.py         # BOSS 直聘测试
│
└── config/
    └── settings.py            # 配置 (含 Auth0)
```

---

## 🔐 JWT 认证配置

### Auth0 设置

| 配置项 | 值 |
|--------|-----|
| Domain | `qing-personal-domain.au.auth0.com` |
| Client ID | `81DY4R0s11wzhFyJNCZd6NbSQrrULVF9` |
| API Audience | `https://qing-agent-api` |
| 算法 | RS256 |

### 权限范围

- `read:jobs` - 获取职位
- `write:jobs` - 写入职位/投递
- `read:users` - 获取用户
- `write:users` - 写入用户

### API 调用示例

```bash
# 1. 获取 Token (从 Auth0)
TOKEN="your_jwt_token"

# 2. 调用受保护的 API
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/api/users/1
```

---

## 📊 开发进度

| 阶段 | 内容 | 状态 | 完成时间 |
|------|------|------|----------|
| 阶段 1 | MVP 核心功能 | ✅ 100% | 2026-03-08 |
| 阶段 2 | 多平台适配 | ✅ 100% | 2026-03-08 |
| 阶段 3 | 防封禁保护 | ✅ 100% | 2026-03-08 |
| 阶段 4 | 产品级 API | ✅ 100% | 2026-03-08 |
| 阶段 5 | JWT 认证 | ✅ 100% | 2026-03-09 |
| 阶段 6 | SQLite 数据库 | ⏳ 0% | 待执行 |
| 阶段 7 | 前端 UI | ⏳ 0% | 待执行 |

**总体进度:** 75% 完成

---

## 🧪 测试

```bash
# JWT 认证测试
python tests/test_jwt_auth.py

# 集成测试
python tests/test_integration.py

# BOSS 直聘测试 (需 OpenClaw 环境)
python tests/test_boss_openclaw.py
```

---

## 📋 API 端点

### 公开端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 根路径 |
| GET | `/health` | 健康检查 |
| GET | `/docs` | API 文档 |

### 受保护端点 (需要 JWT)

#### 用户管理
| 方法 | 路径 | 权限 |
|------|------|------|
| POST | `/api/users/` | write:users |
| GET | `/api/users/{id}` | read:users |
| PUT | `/api/users/{id}` | write:users |

#### 职位管理
| 方法 | 路径 | 权限 |
|------|------|------|
| POST | `/api/jobs/search` | read:jobs |
| GET | `/api/jobs/{id}` | read:jobs |

#### 匹配推荐
| 方法 | 路径 | 权限 |
|------|------|------|
| POST | `/api/matches/calculate` | read:jobs |
| GET | `/api/matches/recommend/{id}` | read:jobs |

#### 投递管理
| 方法 | 路径 | 权限 |
|------|------|------|
| POST | `/api/applications/submit` | write:jobs |
| GET | `/api/applications/{id}` | read:jobs |

---

## 🎯 匹配算法

### 7 维度匹配

| 维度 | 权重 | 说明 |
|------|------|------|
| 行业 | 25% | 5 级相似度 |
| 技能 | 25% | 关键词匹配 |
| 经验 | 15% | 年限匹配 |
| 薪资 | 10% | 期望 vs 提供 |
| 地点 | 10% | 城市匹配 |
| 学历 | 10% | 学历要求 |
| 工具 | 5% | 工具技能 |

---

## ⚠️ 平台状态

| 平台 | 状态 | 说明 |
|------|------|------|
| BOSS 直聘 | ❌ 受限 | 网页端无法搜索，强制 APP |
| 智联招聘 | ✅ 可用 | 网页端功能完整 |

---

## 📈 技术指标

| 指标 | 数值 |
|------|------|
| 总文件数 | 87 个 |
| 代码行数 | ~4500 行 |
| 测试覆盖率 | ~88% |
| API 端点数 | 10 个 |
| 适配器数 | 2 个 |

---

## 📝 更新日志

### v1.3.0 (2026-03-09)
- ✅ 添加 Auth0 JWT 认证
- ✅ 所有写操作添加 JWT 验证
- ✅ 添加 JWT 测试套件

### v1.2.0 (2026-03-08)
- ✅ 产品级 API 路由
- ✅ 防封禁组件集成
- ✅ 完整测试套件

### v1.1.0 (2026-03-08)
- ✅ 核心模块完成
- ✅ 多平台适配器

---

## 🔗 相关文档

- [项目进度报告](项目进度报告 -2026-03-10.md)
- [BOSS 直聘测试报告](tests/BOSS 直聘测试报告.md)
- [阶段 5-JWT 认证完成报告](阶段 5-JWT 认证完成报告.md)

---

**维护者:** 青 (OpenClaw Agent) 🌿  
**GitHub:** https://github.com/Ching-W0121/Qing-SQLite
