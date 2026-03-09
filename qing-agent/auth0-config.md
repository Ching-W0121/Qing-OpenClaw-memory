# Auth0 JWT 认证配置

**配置时间**: 2026-03-09 15:00

## 🔐 核心配置

| 配置项 | 值 |
|--------|-----|
| **Domain** | `qing-personal-domain.au.auth0.com` |
| **Client ID** | `81DY4R0s11wzhFyJNCZd6NbSQrrULVF9` |
| **Client Secret** | `UECmgRh7U1_HEL8OzUl1J2-DmHm4mB-HCmU0VPtKL0kIK40B9GOHdoFalw2DcK1F` |
| **API Identifier** | `https://qing-agent-api` |
| **Signing Algorithm** | `RS256` |
| **JWKS URL** | `https://qing-personal-domain.au.auth0.com/.well-known/jwks.json` |

## 📋 可用权限 (Scopes)

| 权限 | 描述 |
|------|------|
| `read:jobs` | 读取职位列表 |
| `write:jobs` | 写入职位列表 |

## 🔧 环境变量配置 (.env)

```bash
# Auth0 配置
AUTH0_DOMAIN=qing-personal-domain.au.auth0.com
AUTH0_CLIENT_ID=81DY4R0s11wzhFyJNCZd6NbSQrrULVF9
AUTH0_CLIENT_SECRET=UECmgRh7U1_HEL8OzUl1J2-DmHm4mB-HCmU0VPtKL0kIK40B9GOHdoFalw2DcK1F
AUTH0_API_AUDIENCE=https://qing-agent-api
AUTH0_ALGORITHM=RS256
AUTH0_JWKS_URL=https://qing-personal-domain.au.auth0.com/.well-known/jwks.json
```

## 📝 Python 配置示例 (settings.py)

```python
AUTH0_CONFIG = {
    "domain": "qing-personal-domain.au.auth0.com",
    "client_id": "81DY4R0s11wzhFyJNCZd6NbSQrrULVF9",
    "client_secret": "UECmgRh7U1_HEL8OzUl1J2-DmHm4mB-HCmU0VPtKL0kIK40B9GOHdoFalw2DcK1F",
    "api_audience": "https://qing-agent-api",
    "algorithm": "RS256",
    "jwks_url": "https://qing-personal-domain.au.auth0.com/.well-known/jwks.json"
}
```

## 🔗 Auth0 控制台链接

- **Applications**: https://manage.auth0.com/dashboard/au/qing-personal-domain/applications
- **APIs**: https://manage.auth0.com/dashboard/au/qing-personal-domain/apis
- **Qing Agent API 设置**: https://manage.auth0.com/dashboard/au/qing-personal-domain/applications/81DY4R0s11wzhFyJNCZd6NbSQrrULVF9/settings

## ⚠️ 安全提示

- Client Secret 不应提交到 Git
- 生产环境请使用环境变量
- 定期轮换 Client Secret
- 不要在前端代码中暴露 Client Secret
