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
