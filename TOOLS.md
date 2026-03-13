# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

---

## 🧠 Memory System (v3.0)

### Quick Commands

```bash
# Working Memory (current session)
python memory/memory_search.py --layer working

# Episodic Memory (today)
python memory/memory_search.py --layer episodic

# Episodic Memory (specific date)
python memory/memory_search.py --layer episodic --date 2026-03-11

# Semantic Memory (user profile)
python memory/memory_search.py --layer semantic --type profile

# Smart query
python memory/memory_search.py --query "今天做了什么"
```

### File Locations

| Layer | Path | Content |
|-------|------|---------|
| Working | `memory/working/session_current.json` | Current session context |
| Episodic | `memory/episodic/YYYY-MM-DD.jsonl` | User requests (13 entries today) |
| Semantic | `memory/semantic/*.json` | User profile, preferences, knowledge |
| Summaries | `memory/summaries/YYYY-Www.json` | Weekly summaries |
| Archive | `memory/archive/old_markdown/` | Old Markdown files (38 files) |

### Memory Sync

- **Schedule**: Hourly (0 * * * *)
- **Target**: GitHub `Qing-OpenClaw-memory`
- **Content**: `memory/`, `.learnings/`

---

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## 工作习惯

- **任务完成后必须汇报**：告诉庆任务已完成，并简述做了什么

---

## 📸 飞书发图片（重要！）

**问题**: OpenClaw 的 `message` 工具在飞书上发图有 bug，飞书收到的是文件路径文本，不是真正的图片。

**正确方法**: 用 `exec` 工具执行 curl 调用飞书 API，分三步：

### Step 1: 获取 tenant_access_token

```powershell
# 从 openclaw.json 读取 appSecret
$CONFIG = Get-Content "$env:APPDATA\openclaw\openclaw.json" | ConvertFrom-Json
$APP_ID = $CONFIG.channels.feishu.appId
$APP_SECRET = $CONFIG.channels.feishu.appSecret

# 获取 token
$TOKEN_RESPONSE = Invoke-RestMethod -Uri 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' -Method Post -ContentType 'application/json' -Body (@{app_id=$APP_ID;app_secret=$APP_SECRET} | ConvertTo-Json)
$TOKEN = $TOKEN_RESPONSE.tenant_access_token
```

### Step 2: 上传图片获取 image_key

```powershell
# 上传图片（支持 JPEG, PNG, WEBP, GIF, TIFF, BMP, ICO）
$IMAGE_PATH = "C:/path/to/image.png"
$IMAGE_RESPONSE = Invoke-RestMethod -Uri 'https://open.feishu.cn/open-apis/im/v1/images' -Method Post -Headers @{Authorization="Bearer $TOKEN"} -Form @{image_type="message";image=(Get-Item $IMAGE_PATH)}
$IMAGE_KEY = $IMAGE_RESPONSE.data.image_key
```

### Step 3: 发送图片消息

```powershell
# 发送图片消息
$RECEIVE_ID = "ou_xxxxxxxx"  # 收信人 open_id
$CONTENT = (@{image_key=$IMAGE_KEY} | ConvertTo-Json -Compress)
Invoke-RestMethod -Uri 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id' -Method Post -Headers @{Authorization="Bearer $TOKEN";'Content-Type'='application/json'} -Body (@{receive_id=$RECEIVE_ID;msg_type="image";content=$CONTENT} | ConvertTo-Json)
```

### 关键信息

| 配置项 | 值 |
|--------|-----|
| App ID | `cli_a93ba86cdfba5bcc` |
| 用户 open_id | 待获取（在飞书开发者后台查看） |
| 支持格式 | JPEG, PNG, WEBP, GIF, TIFF, BMP, ICO |
| 最大文件大小 | 10MB |

### 完整示例（PowerShell 脚本）

```powershell
# 飞书发图完整脚本
param(
    [string]$ImagePath,
    [string]$ReceiveId
)

# 读取配置
$CONFIG = Get-Content "$env:APPDATA\openclaw\openclaw.json" | ConvertFrom-Json
$APP_ID = $CONFIG.channels.feishu.appId
$APP_SECRET = $CONFIG.channels.feishu.appSecret

# Step 1: 获取 token
$TOKEN_RESPONSE = Invoke-RestMethod -Uri 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' -Method Post -ContentType 'application/json' -Body (@{app_id=$APP_ID;app_secret=$APP_SECRET} | ConvertTo-Json)
$TOKEN = $TOKEN_RESPONSE.tenant_access_token

# Step 2: 上传图片
$IMAGE_RESPONSE = Invoke-RestMethod -Uri 'https://open.feishu.cn/open-apis/im/v1/images' -Method Post -Headers @{Authorization="Bearer $TOKEN"} -Form @{image_type="message";image=(Get-Item $ImagePath)}
$IMAGE_KEY = $IMAGE_RESPONSE.data.image_key

# Step 3: 发送消息
$CONTENT = (@{image_key=$IMAGE_KEY} | ConvertTo-Json -Compress)
Invoke-RestMethod -Uri 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id' -Method Post -Headers @{Authorization="Bearer $TOKEN";'Content-Type'='application/json'} -Body (@{receive_id=$ReceiveId;msg_type="image";content=$CONTENT} | ConvertTo-Json)

Write-Host "图片发送成功！image_key: $IMAGE_KEY"
```

**使用方法**: 当用户要求发送图片时，执行上述 PowerShell 脚本，替换 `$ImagePath` 和 `$ReceiveId` 参数。

---

## 🧠 豆包向量模型配置（多模态）

| 配置项 | 值 |
|--------|-----|
| Base URL | `https://ark.cn-beijing.volces.com/api/v3` |
| API Key | `fddc1778-d04c-403e-8327-ab68ec1ec9dd` |
| 模型 ID | `doubao-embedding-vision-251215` |
| Embedding 维度 | 2048 |
| API Endpoint | `/embeddings/multimodal` |
| 支持类型 | text, image_url, video_url |

### 调用示例

```bash
curl -X POST "https://ark.cn-beijing.volces.com/api/v3/embeddings/multimodal" \
  -H "Authorization: Bearer fddc1778-d04c-403e-8327-ab68ec1ec9dd" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-embedding-vision-251215",
    "encoding_format": "float",
    "input": [
      {"type": "text", "text": "文本内容"},
      {"type": "image_url", "image_url": {"url": "https://example.com/image.png"}}
    ]
  }'
```

### 响应格式

```json
{
  "created": 1743575029,
  "data": {
    "embedding": [-0.123, -0.355, ...],
    "object": "embedding"
  },
  "id": "021743575029461...",
  "model": "doubao-embedding-vision-251215",
  "usage": {
    "prompt_tokens": 13987,
    "total_tokens": 13987
  }
}
```

### 调用示例

```bash
curl -X POST "https://ark.cn-beijing.volces.com/api/v3/embeddings" \
  -H "Authorization: Bearer fddc1778-d04c-403e-8327-ab68ec1ec9dd" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Doubao-embedding-vision",
    "input": ["文本 1", "文本 2"]
  }'
```

### 响应格式

```json
{
  "data": [
    {
      "embedding": [0.1, 0.2, ...],
      "index": 0
    }
  ],
  "model": "Doubao-embedding-vision",
  "usage": {
    "prompt_tokens": 10,
    "total_tokens": 10
  }
}
```

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
