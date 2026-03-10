# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice
**Areas**: frontend | backend | infra | tests | docs | config
**Statuses**: pending | in_progress | resolved | wont_fix | promoted | promoted_to_skill

## Status Definitions

| Status | Meaning |
|--------|---------|
| `pending` | Not yet addressed |
| `in_progress` | Actively being worked on |
| `resolved` | Issue fixed or knowledge integrated |
| `wont_fix` | Decided not to address (reason in Resolution) |
| `promoted` | Elevated to CLAUDE.md, AGENTS.md, or copilot-instructions.md |
| `promoted_to_skill` | Extracted as a reusable skill |

## Skill Extraction Fields

When a learning is promoted to a skill, add these fields:

```markdown
**Status**: promoted_to_skill
**Skill-Path**: skills/skill-name
```

Example:
```markdown
## [LRN-20250115-001] best_practice

**Logged**: 2025-01-15T10:00:00Z
**Priority**: high
**Status**: promoted_to_skill
**Skill-Path**: skills/docker-m1-fixes
**Area**: infra

### Summary
Docker build fails on Apple Silicon due to platform mismatch
...
```

---

## [LRN-20260310-001] correction

**Logged**: 2026-03-10T14:36:00+08:00
**Priority**: critical
**Status**: in_progress
**Area**: config

### Summary
用户纠正：反思汇报格式不规范 + 未养成记忆同步习惯 + 技能使用不完整

### Details
庆提出三点纠正：
1. **反思汇报格式** — 应以"做了什么 → 发现问题 → 解决问题 → 吸取教训"为主
2. **记忆同步** — 每天的记忆必须自动上传到 GitHub 仓库 `https://github.com/Ching-W0121/Qing-OpenClaw-memory`（这是 Viking 的核心用途）
3. **技能使用** — 检查所有技能，确保都用上

### Suggested Action
1. 创建每日记忆自动同步机制（cron 或 heartbeat）
2. 配置 Viking 与 GitHub 仓库的连接
3. 列出所有可用技能并逐一启用
4. 规范反思汇报格式

### Metadata
- Source: user_correction
- Tags: workflow, memory, skills, reflection
- Pattern-Key: memory.sync.github | skills.activation | reflection.format
- Recurrence-Count: 1
- First-Seen: 2026-03-10

---