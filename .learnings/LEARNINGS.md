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

---## [LRN-20260313-IGF] best_practice

**Logged**: 2026-03-13T03:37:56.964Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-12T12:15:40.783Z] 你是不是又陷入了死循环

### Details
通过反思系统自动生成

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, learning
- Pattern-Key: learning.1773373076964

---

## [LRN-20260313-MLC] best_practice

**Logged**: 2026-03-13T03:37:56.964Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-12T13:13:36.214Z] 先完成真实数据的测试、前程无忧和拉勾网，这两个网站我没有登录所以你只能用未登录状态测试，所以测试数据应该不多属于正常情况

### Details
通过反思系统自动生成

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, learning
- Pattern-Key: learning.1773373076964

---

## [LRN-20260313-LG0] best_practice

**Logged**: 2026-03-13T03:37:56.964Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-12T15:34:38.481Z] 你在网页上看不到吗？网页中应该有一个投递页面然后点进去就可以看到了

### Details
通过反思系统自动生成

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, learning
- Pattern-Key: learning.1773373076964

---

## [LRN-20260313-7M4] best_practice

**Logged**: 2026-03-13T03:37:56.964Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-12T15:51:16.047Z] 我投递的职位是：品牌专员、公司是：深圳纬度数据科技股份有限公司、薪资是：8000-13000，你所给的全是错误信息，我们所做的所有事情应该按照实事求是，找到了就是找到了，没找到就是没找到，而不是编造一

### Details
通过反思系统自动生成

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, learning
- Pattern-Key: learning.1773373076964

---

## [LRN-20260313-1QT] best_practice

**Logged**: 2026-03-13T03:37:56.964Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-12T15:52:56.261Z] 不是你错了就行，你的学会反思

### Details
通过反思系统自动生成

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, learning
- Pattern-Key: learning.1773373076964

---

## [LRN-20260313-RKT] best_practice

**Logged**: 2026-03-13T03:37:56.964Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-12T16:14:21.861Z] 我还是没收到，你确定你有这个功能吗？你自己检查一下为什么我收到的是文字，而不是真实的图片

### Details
通过反思系统自动生成

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, learning
- Pattern-Key: learning.1773373076964

---

## [LRN-20260313-B9I] best_practice

**Logged**: 2026-03-13T03:37:56.964Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-12T16:16:36.949Z] 你检查一下日志，应该是报错了，没有发送成功

### Details
通过反思系统自动生成

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, learning
- Pattern-Key: learning.1773373076964

---

## [LRN-20260313-17U] best_practice

**Logged**: 2026-03-13T03:37:56.964Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-12T13:13:36.214Z] 先完成真实数据的测试、前程无忧和拉勾网，这两个网站我没有登录所以你只能用未登录状态测试，所以测试数据应该不多属于正常情况

### Details
Successful strategy from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, strategy
- Pattern-Key: strategy.1773373076964

---

## [LRN-20260313-Z0T] best_practice

**Logged**: 2026-03-13T03:37:56.964Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-12T15:56:32.533Z] 你再次查看智联招聘网页，找到我投递的岗位，查看岗位并把信息反馈给我，如果没找到就告诉我没找到原因是什么就好了

### Details
Successful strategy from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, strategy
- Pattern-Key: strategy.1773373076964

---

## [LRN-20260313-DCZ] best_practice

**Logged**: 2026-03-13T03:37:56.964Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-12T15:58:45.015Z] 那你在测试投递数据的时候为什么是成功的？你的依据是什么？

### Details
Successful strategy from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, strategy
- Pattern-Key: strategy.1773373076964

---

## [LRN-20260313-5II] best_practice

**Logged**: 2026-03-13T03:37:56.964Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-12T16:16:36.949Z] 你检查一下日志，应该是报错了，没有发送成功

### Details
Successful strategy from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, strategy
- Pattern-Key: strategy.1773373076964

---

## [ERR-20260313-18E] reflection

**Logged**: 2026-03-13T03:37:56.964Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-12T11:52:12.276Z] 继续，先用boss跑一遍，如果不行换成智联，给到我真实网页数据

### Details
Mistake identified from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, error
- Pattern-Key: error.1773373076964

---

## [ERR-20260313-RXD] reflection

**Logged**: 2026-03-13T03:37:56.964Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-12T15:04:09.091Z] 继续投递如果还不行再来禁用浏览器拓展投递

### Details
Mistake identified from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, error
- Pattern-Key: error.1773373076964

---

## [ERR-20260313-YSZ] reflection

**Logged**: 2026-03-13T03:37:56.964Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-12T15:51:16.047Z] 我投递的职位是：品牌专员、公司是：深圳纬度数据科技股份有限公司、薪资是：8000-13000，你所给的全是错误信息，我们所做的所有事情应该按照实事求是，找到了就是找到了，没找到就是没找到，而不是编造一

### Details
Mistake identified from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, error
- Pattern-Key: error.1773373076964

---

## [ERR-20260313-5ZL] reflection

**Logged**: 2026-03-13T03:37:56.964Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-12T15:52:56.261Z] 不是你错了就行，你的学会反思

### Details
Mistake identified from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, error
- Pattern-Key: error.1773373076964

---

## [ERR-20260313-PFD] reflection

**Logged**: 2026-03-13T03:37:56.964Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-12T16:16:36.949Z] 你检查一下日志，应该是报错了，没有发送成功

### Details
Mistake identified from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, error
- Pattern-Key: error.1773373076964

---

