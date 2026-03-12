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
