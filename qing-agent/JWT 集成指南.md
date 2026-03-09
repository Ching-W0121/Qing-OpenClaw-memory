# JWT 认证集成指南 - v1.3

**集成时间**: 2026-03-09  
**版本**: v1.3.0

---

## 📋 概述

求职 Agent API 现已支持 Auth0 JWT 认证，所有 API 端点都需要有效的 JWT Token 才能访问。

---

## 🔧 配置步骤

### 1. 复制环境变量文件

```bash
cd C:\Users\TR\.openclaw\workspace\qing-agent
copy .env.example .env
```

### 2. 配置 Auth0 凭证

编辑 `.env` 文件，确保以下配置正确：

```bash
AUTH0_DOMAIN=qing-personal-domain.au.auth0.com
AUTH0_CLIENT_ID=81DY4R0s11wzhFyJNCZd6NbSQrrULVF9
AUTH0_CLIENT_SECRET=UECmgRh7U1_HEL8OzUl1J2-DmHm4mB-HCmU0VPtKL0kIK40B9GOHdoFalw2DcK1F
AUTH0_API_AUDIENCE=https://qing-agent-api
AUTH0_ALGORITHM=RS256
```

### 3. 安装依赖

```bash
pip install PyJWT cryptography requests python-jose
```

---

## 🚀 启动服务

```bash
# 方式 1: 直接运行
python main.py

# 方式 2: 使用 uvicorn
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 🔐 获取 JWT Token

### 方式 1: 使用 Auth0 测试工具

1. 访问 Auth0 Dashboard: https://manage.auth0.com/dashboard/au/qing-personal-domain/applications
2. 进入 "Qing Agent API" 应用
3. 点击 "Test" 标签
4. 点击 "Request Token"
5. 复制返回的 Access Token

### 方式 2: 使用 curl 请求

```bash
curl --request POST \
  --url https://qing-personal-domain.au.auth0.com/oauth/token \
  --header 'content-type: application/json' \
  --data '{
    "client_id": "81DY4R0s11wzhFyJNCZd6NbSQrrULVF9",
    "client_secret": "UECmgRh7U1_HEL8OzUl1J2-DmHm4mB-HCmU0VPtKL0kIK40B9GOHdoFalw2DcK1F",
    "audience": "https://qing-agent-api",
    "grant_type": "client_credentials"
  }'
```

响应示例：
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "scope": "read:jobs write:jobs",
  "expires_in": 86400,
  "token_type": "Bearer"
}
```

---

## 📝 使用 API

### 1. 搜索职位（需要 read:jobs 权限）

```bash
curl -X POST "http://127.0.0.1:8000/api/jobs/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "keyword": "品牌策划",
    "city": "深圳",
    "page": 1
  }'
```

### 2. 获取职位详情（需要 read:jobs 权限）

```bash
curl "http://127.0.0.1:8000/api/jobs/job_001" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. 创建用户画像（需要 write:users 权限）

```bash
curl -X POST "http://127.0.0.1:8000/api/users/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "industry": "广告",
    "skills": ["品牌策划", "文案写作"],
    "tools": ["Photoshop"],
    "experience_years": 3,
    "education": "本科",
    "expected_city": "深圳",
    "expected_salary_min": 10000,
    "expected_salary_max": 15000
  }'
```

### 4. 计算匹配度（需要 read:jobs 权限）

```bash
curl -X POST "http://127.0.0.1:8000/api/matches/calculate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "user": {
      "industry": "广告",
      "skills": ["品牌策划"],
      "tools": ["Photoshop"],
      "experience_years": 3,
      "education": "本科",
      "expected_city": "深圳",
      "expected_salary_min": 10000,
      "expected_salary_max": 15000
    },
    "jobs": [...]
  }'
```

---

## 🛡️ 权限说明

| 端点 | 需要权限 |
|------|----------|
| `POST /api/jobs/search` | `read:jobs` |
| `GET /api/jobs/{id}` | `read:jobs` |
| `POST /api/users/` | `write:users` |
| `GET /api/users/{id}` | `read:users` |
| `PUT /api/users/{id}` | `write:users` |
| `POST /api/matches/calculate` | `read:jobs` |
| `GET /api/matches/recommend/{id}` | `read:jobs` |
| `POST /api/applications/submit` | `write:jobs` |
| `GET /api/applications/{id}` | `read:users` |

---

## 🧪 测试 JWT 认证

```bash
cd C:\Users\TR\.openclaw\workspace\qing-agent
python tests/test_jwt_auth.py
```

预期输出：
```
============================================================
JWT 认证测试 - 阶段 5
============================================================
[OK] JWTAuth 初始化成功
[OK] JWKS URL: https://qing-personal-domain.au.auth0.com/.well-known/jwks.json
[OK] 从 permissions 字段提取权限成功
[OK] 从 scope 字段提取权限成功
[OK] 权限检查成功
[OK] 测试 Token 生成成功：eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
[INFO] 注意：测试 token 是自签名的，仅用于开发环境

============================================================
[PASS] 所有 JWT 认证测试通过！
============================================================
```

---

## ⚠️ 错误处理

### 401 Unauthorized

```json
{
  "detail": "Authorization credentials missing"
}
```

**原因**: 未提供 Token 或 Token 格式错误

**解决**: 确保请求头包含 `Authorization: Bearer YOUR_TOKEN`

### 403 Forbidden

```json
{
  "detail": "Missing required permission: read:jobs"
}
```

**原因**: Token 有效但缺少所需权限

**解决**: 在 Auth0 Dashboard 中为用户分配相应权限

### Token 过期

```json
{
  "detail": "Token has expired"
}
```

**原因**: Token 已过期（默认 24 小时）

**解决**: 重新请求新的 Token

---

## 🔒 安全建议

1. **不要将 `.env` 文件提交到 Git**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **定期轮换 Client Secret**
   - 在 Auth0 Dashboard 中点击 "Rotate Secret"

3. **使用 HTTPS**
   - 生产环境必须使用 HTTPS

4. **限制 Token 有效期**
   - 开发环境：24 小时
   - 生产环境：1 小时或更短

5. **实施刷新 Token 机制**
   - 使用 refresh token 获取新的 access token

---

## 📚 相关文件

- `auth/jwt_auth.py` - JWT 认证核心模块
- `auth/__init__.py` - 认证模块导出
- `config/settings.py` - 配置加载
- `.env.example` - 环境变量示例
- `tests/test_jwt_auth.py` - JWT 认证测试

---

## 🆘 故障排查

### 问题：无法获取 Token

**检查**:
1. Client ID 和 Client Secret 是否正确
2. API Audience 是否匹配 (`https://qing-agent-api`)
3. Auth0 Domain 是否正确

### 问题：Token 验证失败

**检查**:
1. JWKS URL 是否可访问
2. Algorithm 是否匹配 (RS256)
3. Token 是否过期

### 问题：权限不足

**检查**:
1. 在 Auth0 Dashboard 中检查应用权限
2. 确认 Token 包含所需 scope/permissions
3. 检查 API 权限配置

---

## 📞 支持

如有问题，请查看：
- Auth0 文档：https://auth0.com/docs
- JWT.io 调试器：https://jwt.io
- 项目文档：`qing-agent/README.md`
