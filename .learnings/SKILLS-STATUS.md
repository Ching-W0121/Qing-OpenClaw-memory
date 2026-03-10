# 技能状态清单 - 2026-03-10

**总计**: 56 个技能  
**就绪**: 9 个 (16%)  
**缺失依赖**: 47 个 (84%)

---

## ✅ 已就绪技能 (9 个)

| 技能 | 用途 | 依赖 |
|------|------|------|
| `coding-agent` | 委托编码任务 | 无 |
| `healthcheck` | 安全审计 | 无 |
| `skill-creator` | 创建技能 | 无 |
| `weather` | 天气查询 | curl (已安装) |
| `find-skills` | 查找技能 | 无 |
| `self-improvement` | 学习日志 | 无 |
| `self-improving` | 自我反思 | 无 |
| `tavily` | AI 搜索 | 无 |
| `word-document-processor` | Word 文档 | 无 |

---

## ⏳ 需配置技能 (47 个)

### 🔐 账户/API 类 (需要 API Key 或登录)

| 技能 | 需要什么 | 配置难度 |
|------|----------|----------|
| `1password` | 1Password 账户 + op CLI | 🟡 中 |
| `bluebubbles` | BlueBubbles 服务器配置 | 🔴 高 |
| `discord` | Discord Bot Token | 🟡 中 |
| `gog` | Google Workspace OAuth | 🔴 高 |
| `himalaya` | IMAP/SMTP 邮箱账户 | 🟡 中 |
| `notion` | Notion API Token | 🟢 低 |
| `openai-image-gen` | OpenAI API Key | 🟢 低 |
| `openai-whisper-api` | OpenAI API Key | 🟢 低 |
| `openhue` | Philips Hue Bridge | 🟡 中 |
| `slack` | Slack Bot Token | 🟡 中 |
| `songsee` | 音频处理依赖 | 🟡 中 |
| `spotify-player` | Spotify OAuth | 🟡 中 |
| `trello` | Trello API Token | 🟢 低 |
| `wacli` | WhatsApp 配置 | 🔴 高 |
| `xurl` | Twitter API v2 | 🔴 高 |
| `gh-issues` | GitHub Token + gh CLI | 🟢 低 |
| `github` | GitHub Token + gh CLI | 🟢 低 |

### 🛠️ CLI 工具类 (需要安装二进制文件)

| 技能 | 需要什么 | 配置难度 |
|------|----------|----------|
| `apple-notes` | macOS + memo CLI | 🔴 仅 macOS |
| `apple-reminders` | macOS + remindctl | 🔴 仅 macOS |
| `bear-notes` | macOS + grizzly CLI | 🔴 仅 macOS |
| `blogwatcher` | blogwatcher CLI | 🟢 低 |
| `blucli` | blu CLI (BluOS) | 🟡 中 |
| `camsnap` | camsnap CLI + RTSP 相机 | 🟡 中 |
| `eightctl` | Eight Sleep API | 🟡 中 |
| `gemini` | Gemini CLI + API Key | 🟢 低 |
| `gifgrep` | GIF 搜索 CLI | 🟢 低 |
| `imsg` | macOS Messages.app | 🔴 仅 macOS |
| `mcporter` | MCP CLI | 🟢 低 |
| `model-usage` | CodexBar CLI | 🟢 低 |
| `nano-banana-pro` | Gemini CLI | 🟢 低 |
| `nano-pdf` | nano-pdf CLI | 🟢 低 |
| `obsidian` | obsidian-cli + Vault | 🟢 低 |
| `openai-whisper` | Whisper CLI (本地) | 🟡 中 |
| `oracle` | oracle CLI | 🟢 低 |
| `ordercli` | Foodora 账户 | 🟡 中 |
| `peekaboo` | macOS UI 自动化 | 🔴 仅 macOS |
| `sag` | ElevenLabs API Key | 🟢 低 |
| `sherpa-onnx-tts` | sherpa-onnx (本地 TTS) | 🟡 中 |
| `sonoscli` | Sonos 音响 + CLI | 🟡 中 |
| `things-mac` | macOS + Things 3 | 🔴 仅 macOS |
| `tmux` | tmux + SSH | 🟡 中 |
| `video-frames` | ffmpeg | 🟢 低 |
| `voice-call` | 语音通话配置 | 🟡 中 |

### 📦 其他类

| 技能 | 需要什么 | 配置难度 |
|------|----------|----------|
| `canvas` | 浏览器控制 | 已内置 |
| `clawhub` | clawhub CLI | 🟢 低 |
| `session-logs` | jq + 日志访问 | 🟢 低 |
| `summarize` | 无特殊依赖 | 可能已就绪 |

---

## 🎯 推荐优先配置 (按实用性排序)

### 优先级 1 - 高实用性 (建议配置)

| 技能 | 用途 | 配置步骤 |
|------|------|----------|
| `github` | GitHub 操作 | `gh auth login` |
| `notion` | 笔记管理 | 创建 Notion Integration |
| `obsidian` | 本地笔记 | `npm i -g obsidian-cli` |
| `video-frames` | 视频处理 | 安装 ffmpeg |

### 优先级 2 - 中等实用性 (按需配置)

| 技能 | 用途 |
|------|------|
| `discord` | 如果要用 Discord |
| `slack` | 如果要用 Slack |
| `sag` | 如果需要语音输出 |

### 优先级 3 - 低实用性 (暂不配置)

- macOS 专用技能 (当前是 Windows)
- 特定硬件技能 (Sonos、Hue、Eight Sleep 等)
- 区域限制技能 (Foodora 等)

---

## 📝 配置建议

**原则**: 按需配置，不预装闲置技能

1. **现在配置**: `github` (庆有 GitHub 仓库)
2. **后续按需**: 遇到需求时再配置对应技能
3. **不用配置**: macOS 专用、硬件依赖、区域限制

---

**更新时间**: 2026-03-10 14:50  
**下次审查**: 2026-03-17 (一周后)
