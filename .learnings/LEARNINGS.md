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

## [LRN-20260313-46O] best_practice

**Logged**: 2026-03-13T08:12:46.892Z
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
- Pattern-Key: learning.1773389566892

---

## [LRN-20260313-RVI] best_practice

**Logged**: 2026-03-13T08:12:46.892Z
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
- Pattern-Key: learning.1773389566892

---

## [LRN-20260313-V1P] best_practice

**Logged**: 2026-03-13T08:12:46.892Z
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
- Pattern-Key: learning.1773389566892

---

## [LRN-20260313-X2W] best_practice

**Logged**: 2026-03-13T08:12:46.892Z
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
- Pattern-Key: learning.1773389566892

---

## [LRN-20260313-JRQ] best_practice

**Logged**: 2026-03-13T08:12:46.892Z
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
- Pattern-Key: learning.1773389566892

---

## [LRN-20260313-05X] best_practice

**Logged**: 2026-03-13T08:12:46.892Z
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
- Pattern-Key: learning.1773389566892

---

## [LRN-20260313-MIZ] best_practice

**Logged**: 2026-03-13T08:12:46.892Z
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
- Pattern-Key: learning.1773389566892

---

## [LRN-20260313-PYY] best_practice

**Logged**: 2026-03-13T08:12:46.892Z
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
- Pattern-Key: strategy.1773389566892

---

## [LRN-20260313-FWQ] best_practice

**Logged**: 2026-03-13T08:12:46.892Z
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
- Pattern-Key: strategy.1773389566892

---

## [LRN-20260313-AHZ] best_practice

**Logged**: 2026-03-13T08:12:46.892Z
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
- Pattern-Key: strategy.1773389566892

---

## [LRN-20260313-M69] best_practice

**Logged**: 2026-03-13T08:12:46.892Z
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
- Pattern-Key: strategy.1773389566892

---

## [ERR-20260313-59V] reflection

**Logged**: 2026-03-13T08:12:46.892Z
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
- Pattern-Key: error.1773389566892

---

## [ERR-20260313-P9N] reflection

**Logged**: 2026-03-13T08:12:46.892Z
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
- Pattern-Key: error.1773389566892

---

## [ERR-20260313-D5H] reflection

**Logged**: 2026-03-13T08:12:46.892Z
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
- Pattern-Key: error.1773389566892

---

## [ERR-20260313-DEX] reflection

**Logged**: 2026-03-13T08:12:46.892Z
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
- Pattern-Key: error.1773389566892

---

## [ERR-20260313-MCQ] reflection

**Logged**: 2026-03-13T08:12:46.892Z
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
- Pattern-Key: error.1773389566892

---

## [LRN-20260313-4SU] best_practice

**Logged**: 2026-03-13T14:12:48.308Z
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
- Pattern-Key: learning.1773411168308

---

## [LRN-20260313-FMQ] best_practice

**Logged**: 2026-03-13T14:12:48.308Z
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
- Pattern-Key: learning.1773411168308

---

## [LRN-20260313-LGG] best_practice

**Logged**: 2026-03-13T14:12:48.308Z
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
- Pattern-Key: learning.1773411168308

---

## [LRN-20260313-W1T] best_practice

**Logged**: 2026-03-13T14:12:48.308Z
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
- Pattern-Key: learning.1773411168308

---

## [LRN-20260313-1YK] best_practice

**Logged**: 2026-03-13T14:12:48.308Z
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
- Pattern-Key: learning.1773411168308

---

## [LRN-20260313-KSL] best_practice

**Logged**: 2026-03-13T14:12:48.308Z
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
- Pattern-Key: learning.1773411168308

---

## [LRN-20260313-B48] best_practice

**Logged**: 2026-03-13T14:12:48.308Z
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
- Pattern-Key: learning.1773411168308

---

## [LRN-20260313-OPO] best_practice

**Logged**: 2026-03-13T14:12:48.308Z
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
- Pattern-Key: strategy.1773411168308

---

## [LRN-20260313-0I7] best_practice

**Logged**: 2026-03-13T14:12:48.308Z
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
- Pattern-Key: strategy.1773411168308

---

## [LRN-20260313-9S5] best_practice

**Logged**: 2026-03-13T14:12:48.308Z
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
- Pattern-Key: strategy.1773411168308

---

## [LRN-20260313-LP9] best_practice

**Logged**: 2026-03-13T14:12:48.308Z
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
- Pattern-Key: strategy.1773411168308

---

## [ERR-20260313-3B9] reflection

**Logged**: 2026-03-13T14:12:48.308Z
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
- Pattern-Key: error.1773411168308

---

## [ERR-20260313-G7X] reflection

**Logged**: 2026-03-13T14:12:48.308Z
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
- Pattern-Key: error.1773411168308

---

## [ERR-20260313-2PT] reflection

**Logged**: 2026-03-13T14:12:48.308Z
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
- Pattern-Key: error.1773411168308

---

## [ERR-20260313-MNS] reflection

**Logged**: 2026-03-13T14:12:48.308Z
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
- Pattern-Key: error.1773411168308

---

## [ERR-20260313-SHN] reflection

**Logged**: 2026-03-13T14:12:48.308Z
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
- Pattern-Key: error.1773411168308

---

## [LRN-20260314-JUC] best_practice

**Logged**: 2026-03-14T04:17:38.549Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T07:09:12.495Z] 智联测试完成后你是不是给了我反馈的信息，那信息里面是不是有相关公司数据？

### Details
通过反思系统自动生成

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, learning
- Pattern-Key: learning.1773461858549

---

## [LRN-20260314-71R] best_practice

**Logged**: 2026-03-14T04:17:38.549Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T08:32:33.670Z] 所有的投递测试都是一样的流程，都是打开chrome浏览器，我登陆了所以是不需要登陆的，搜索岗位——先排除行业、薪资、地址——点击进入岗位查看jd——匹配度≥80%——点击投递。我现在怀疑你反思系统还是

### Details
通过反思系统自动生成

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, learning
- Pattern-Key: learning.1773461858549

---

## [LRN-20260314-CBS] best_practice

**Logged**: 2026-03-14T04:17:38.549Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T16:07:35.274Z] 为了防止你再次失忆先把所有对话内容都记忆，如果你聪明的话，你应该以及记忆了，而不是我提醒你

### Details
通过反思系统自动生成

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, learning
- Pattern-Key: learning.1773461858549

---

## [LRN-20260314-ZWY] best_practice

**Logged**: 2026-03-14T04:17:38.549Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T07:09:12.495Z] 智联测试完成后你是不是给了我反馈的信息，那信息里面是不是有相关公司数据？

### Details
Successful strategy from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, strategy
- Pattern-Key: strategy.1773461858549

---

## [LRN-20260314-VE0] best_practice

**Logged**: 2026-03-14T04:17:38.550Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T07:41:47.760Z] ok，我们现在来继续我们的求职agent，智联已经能够真实投递了，你帮我写一句大概内容是：您好，我是王庆的个人求职Ai助手，通过分析匹配贵司的招聘详情，庆的个人经验匹配度挺高的.....这类型的话，总

### Details
Successful strategy from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, strategy
- Pattern-Key: strategy.1773461858550

---

## [LRN-20260314-OL3] best_practice

**Logged**: 2026-03-14T04:17:38.550Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T07:57:42.786Z] ok，我们来继续完善求职agent，我们做到那一步了

### Details
Successful strategy from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, strategy
- Pattern-Key: strategy.1773461858550

---

## [LRN-20260314-EFE] best_practice

**Logged**: 2026-03-14T04:17:38.550Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T11:02:54.729Z] https://github.com/liugedapiqiu-dev/vectorbrain，你用chrome浏览器打开这个网站，然后阅读它的使用文档，一步一步完成它

### Details
Successful strategy from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, strategy
- Pattern-Key: strategy.1773461858550

---

## [LRN-20260314-Z90] best_practice

**Logged**: 2026-03-14T04:17:38.550Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T13:08:10.067Z] 你根据官方文档的步骤一步一步操作就行，对于embedding模型，我们换个模型，我稍后会给你单独配置，你先把其他的都完成

### Details
Successful strategy from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, strategy
- Pattern-Key: strategy.1773461858550

---

## [LRN-20260314-8ZW] best_practice

**Logged**: 2026-03-14T04:17:38.550Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T14:42:42.888Z] 前程无忧没投递成功，你带着原因去问一下你的gpt老师，告诉他你的运行逻辑还有智联的测试通过数据，以及前程无忧为什么无法看到返回值和自动无法投递

### Details
Successful strategy from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, strategy
- Pattern-Key: strategy.1773461858550

---

## [LRN-20260314-5Y3] best_practice

**Logged**: 2026-03-14T04:17:38.550Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T15:19:00.913Z] 你目前只投递了一个岗位是：品牌策划经理、公司：深圳市冠旭电子股份有限公司、薪资：1.5-2.5万，你回顾一下这个步骤，为什么这个成功了，其余四个没投递上，或者说根本没投递

### Details
Successful strategy from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, strategy
- Pattern-Key: strategy.1773461858550

---

## [ERR-20260314-ZX0] reflection

**Logged**: 2026-03-14T04:17:38.550Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T08:32:33.670Z] 所有的投递测试都是一样的流程，都是打开chrome浏览器，我登陆了所以是不需要登陆的，搜索岗位——先排除行业、薪资、地址——点击进入岗位查看jd——匹配度≥80%——点击投递。我现在怀疑你反思系统还是

### Details
Mistake identified from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, error
- Pattern-Key: error.1773461858550

---

## [ERR-20260314-141] reflection

**Logged**: 2026-03-14T04:17:38.550Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T14:42:42.888Z] 前程无忧没投递成功，你带着原因去问一下你的gpt老师，告诉他你的运行逻辑还有智联的测试通过数据，以及前程无忧为什么无法看到返回值和自动无法投递

### Details
Mistake identified from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, error
- Pattern-Key: error.1773461858550

---

## [ERR-20260314-MM1] reflection

**Logged**: 2026-03-14T04:17:38.550Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T15:44:09.432Z] 你对于gpt提问这个步骤肯定是出错，你找到昨天晚上21：20，请教GPT：影刀RPA绕过反爬，这个请教内容，然后查看运行的逻辑是什么

### Details
Mistake identified from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, error
- Pattern-Key: error.1773461858550

---

## [ERR-20260314-8X2] reflection

**Logged**: 2026-03-14T04:17:38.550Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T16:51:31.835Z] 那你还是无法读取文本，并且无法输入问题

### Details
Mistake identified from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, error
- Pattern-Key: error.1773461858550

---

## [ERR-20260314-6BO] reflection

**Logged**: 2026-03-14T04:17:38.550Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T16:53:03.218Z] 你检查一下为什么无法输入文本为什么不能读取信息

### Details
Mistake identified from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, error
- Pattern-Key: error.1773461858550

---


---

## [LRN-20260314-DYN] ��̬��ҳ�Զ��������淶

**Logged**: 2026-03-14T17:42:00+08:00
**Priority**: critical
**Status**: resolved
**Area**: browser_automation

### Summary
��̬��ҳ��React/Vue���Զ�����������ȷ���̣��ȴ����� �� snapshot �� ���� act �� ��֤���

### Details
**����**��
- React/Vue Ӧ�ó���������Ⱦ
- snapshot ֻ����˲�� DOM
- �ȴ��� ref ʧЧ
- �þ� ref ������Ȼʧ��

**��ȷ����**��
1. browser.open(url)
2. await sleep(10)  # ��ҳ����ȫ����
3. snapshot = browser.snapshot()  # ��ȡ�� DOM
4. browser.act(ref=snapshot.ref)  # ����ʹ�ã����ȴ�
5. verify = browser.snapshot()  # ��֤���

**��������**�����⣩��
1. snapshot = browser.snapshot()
2. await sleep(5)  # ? �ȴ����� ref ʧЧ
3. browser.act(ref=snapshot.ref)  # ? �þ� ref
4. ����ɹ�  # ? ����֤

### Suggested Action
���� browser �Զ���������ѭ��
1. �ȴ�ҳ��������
2. snapshot ������ʹ��
3. ��������֤���
4. ʧ�������� snapshot ����

### Metadata
- Source: user_feedback
- Related Files: TOOLS.md, AGENTS.md
- Tags: browser_automation, react, best_practice
- Pattern-Key: automation.wait_for_stable_dom

---
## [LRN-20260314-4LR] best_practice

**Logged**: 2026-03-14T10:55:48.522Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T07:09:12.495Z] 智联测试完成后你是不是给了我反馈的信息，那信息里面是不是有相关公司数据？

### Details
通过反思系统自动生成

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, learning
- Pattern-Key: learning.1773485748522

---

## [LRN-20260314-IE6] best_practice

**Logged**: 2026-03-14T10:55:48.522Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T08:32:33.670Z] 所有的投递测试都是一样的流程，都是打开chrome浏览器，我登陆了所以是不需要登陆的，搜索岗位——先排除行业、薪资、地址——点击进入岗位查看jd——匹配度≥80%——点击投递。我现在怀疑你反思系统还是

### Details
通过反思系统自动生成

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, learning
- Pattern-Key: learning.1773485748522

---

## [LRN-20260314-TB3] best_practice

**Logged**: 2026-03-14T10:55:48.522Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T16:07:35.274Z] 为了防止你再次失忆先把所有对话内容都记忆，如果你聪明的话，你应该以及记忆了，而不是我提醒你

### Details
通过反思系统自动生成

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, learning
- Pattern-Key: learning.1773485748522

---

## [LRN-20260314-7UB] best_practice

**Logged**: 2026-03-14T10:55:48.522Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T07:09:12.495Z] 智联测试完成后你是不是给了我反馈的信息，那信息里面是不是有相关公司数据？

### Details
Successful strategy from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, strategy
- Pattern-Key: strategy.1773485748522

---

## [LRN-20260314-TNP] best_practice

**Logged**: 2026-03-14T10:55:48.522Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T07:41:47.760Z] ok，我们现在来继续我们的求职agent，智联已经能够真实投递了，你帮我写一句大概内容是：您好，我是王庆的个人求职Ai助手，通过分析匹配贵司的招聘详情，庆的个人经验匹配度挺高的.....这类型的话，总

### Details
Successful strategy from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, strategy
- Pattern-Key: strategy.1773485748522

---

## [LRN-20260314-QMN] best_practice

**Logged**: 2026-03-14T10:55:48.522Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T07:57:42.786Z] ok，我们来继续完善求职agent，我们做到那一步了

### Details
Successful strategy from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, strategy
- Pattern-Key: strategy.1773485748522

---

## [LRN-20260314-S5K] best_practice

**Logged**: 2026-03-14T10:55:48.522Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T11:02:54.729Z] https://github.com/liugedapiqiu-dev/vectorbrain，你用chrome浏览器打开这个网站，然后阅读它的使用文档，一步一步完成它

### Details
Successful strategy from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, strategy
- Pattern-Key: strategy.1773485748522

---

## [LRN-20260314-4LJ] best_practice

**Logged**: 2026-03-14T10:55:48.522Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T13:08:10.067Z] 你根据官方文档的步骤一步一步操作就行，对于embedding模型，我们换个模型，我稍后会给你单独配置，你先把其他的都完成

### Details
Successful strategy from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, strategy
- Pattern-Key: strategy.1773485748522

---

## [LRN-20260314-WVW] best_practice

**Logged**: 2026-03-14T10:55:48.522Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T14:42:42.888Z] 前程无忧没投递成功，你带着原因去问一下你的gpt老师，告诉他你的运行逻辑还有智联的测试通过数据，以及前程无忧为什么无法看到返回值和自动无法投递

### Details
Successful strategy from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, strategy
- Pattern-Key: strategy.1773485748522

---

## [LRN-20260314-WYO] best_practice

**Logged**: 2026-03-14T10:55:48.522Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T15:19:00.913Z] 你目前只投递了一个岗位是：品牌策划经理、公司：深圳市冠旭电子股份有限公司、薪资：1.5-2.5万，你回顾一下这个步骤，为什么这个成功了，其余四个没投递上，或者说根本没投递

### Details
Successful strategy from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, strategy
- Pattern-Key: strategy.1773485748522

---

## [ERR-20260314-45G] reflection

**Logged**: 2026-03-14T10:55:48.522Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T08:32:33.670Z] 所有的投递测试都是一样的流程，都是打开chrome浏览器，我登陆了所以是不需要登陆的，搜索岗位——先排除行业、薪资、地址——点击进入岗位查看jd——匹配度≥80%——点击投递。我现在怀疑你反思系统还是

### Details
Mistake identified from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, error
- Pattern-Key: error.1773485748522

---

## [ERR-20260314-AHQ] reflection

**Logged**: 2026-03-14T10:55:48.522Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T14:42:42.888Z] 前程无忧没投递成功，你带着原因去问一下你的gpt老师，告诉他你的运行逻辑还有智联的测试通过数据，以及前程无忧为什么无法看到返回值和自动无法投递

### Details
Mistake identified from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, error
- Pattern-Key: error.1773485748522

---

## [ERR-20260314-CIC] reflection

**Logged**: 2026-03-14T10:55:48.522Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T15:44:09.432Z] 你对于gpt提问这个步骤肯定是出错，你找到昨天晚上21：20，请教GPT：影刀RPA绕过反爬，这个请教内容，然后查看运行的逻辑是什么

### Details
Mistake identified from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, error
- Pattern-Key: error.1773485748522

---

## [ERR-20260314-GXA] reflection

**Logged**: 2026-03-14T10:55:48.522Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T16:51:31.835Z] 那你还是无法读取文本，并且无法输入问题

### Details
Mistake identified from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, error
- Pattern-Key: error.1773485748522

---

## [ERR-20260314-8VN] reflection

**Logged**: 2026-03-14T10:55:48.522Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T16:53:03.218Z] 你检查一下为什么无法输入文本为什么不能读取信息

### Details
Mistake identified from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, error
- Pattern-Key: error.1773485748522

---

## [LRN-20260314-OGJ] best_practice

**Logged**: 2026-03-14T22:55:16.916Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T07:09:12.495Z] 智联测试完成后你是不是给了我反馈的信息，那信息里面是不是有相关公司数据？

### Details
通过反思系统自动生成

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, learning
- Pattern-Key: learning.1773528916916

---

## [LRN-20260314-PMJ] best_practice

**Logged**: 2026-03-14T22:55:16.916Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T08:32:33.670Z] 所有的投递测试都是一样的流程，都是打开chrome浏览器，我登陆了所以是不需要登陆的，搜索岗位——先排除行业、薪资、地址——点击进入岗位查看jd——匹配度≥80%——点击投递。我现在怀疑你反思系统还是

### Details
通过反思系统自动生成

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, learning
- Pattern-Key: learning.1773528916916

---

## [LRN-20260314-2Q2] best_practice

**Logged**: 2026-03-14T22:55:16.916Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T16:07:35.274Z] 为了防止你再次失忆先把所有对话内容都记忆，如果你聪明的话，你应该以及记忆了，而不是我提醒你

### Details
通过反思系统自动生成

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, learning
- Pattern-Key: learning.1773528916916

---

## [LRN-20260314-4QU] best_practice

**Logged**: 2026-03-14T22:55:16.916Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T07:09:12.495Z] 智联测试完成后你是不是给了我反馈的信息，那信息里面是不是有相关公司数据？

### Details
Successful strategy from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, strategy
- Pattern-Key: strategy.1773528916916

---

## [LRN-20260314-F7L] best_practice

**Logged**: 2026-03-14T22:55:16.916Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T07:41:47.760Z] ok，我们现在来继续我们的求职agent，智联已经能够真实投递了，你帮我写一句大概内容是：您好，我是王庆的个人求职Ai助手，通过分析匹配贵司的招聘详情，庆的个人经验匹配度挺高的.....这类型的话，总

### Details
Successful strategy from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, strategy
- Pattern-Key: strategy.1773528916916

---

## [LRN-20260314-86J] best_practice

**Logged**: 2026-03-14T22:55:16.916Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T07:57:42.786Z] ok，我们来继续完善求职agent，我们做到那一步了

### Details
Successful strategy from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, strategy
- Pattern-Key: strategy.1773528916916

---

## [LRN-20260314-TOV] best_practice

**Logged**: 2026-03-14T22:55:16.916Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T11:02:54.729Z] https://github.com/liugedapiqiu-dev/vectorbrain，你用chrome浏览器打开这个网站，然后阅读它的使用文档，一步一步完成它

### Details
Successful strategy from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, strategy
- Pattern-Key: strategy.1773528916916

---

## [LRN-20260314-E43] best_practice

**Logged**: 2026-03-14T22:55:16.916Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T13:08:10.067Z] 你根据官方文档的步骤一步一步操作就行，对于embedding模型，我们换个模型，我稍后会给你单独配置，你先把其他的都完成

### Details
Successful strategy from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, strategy
- Pattern-Key: strategy.1773528916916

---

## [LRN-20260314-9UQ] best_practice

**Logged**: 2026-03-14T22:55:16.916Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T14:42:42.888Z] 前程无忧没投递成功，你带着原因去问一下你的gpt老师，告诉他你的运行逻辑还有智联的测试通过数据，以及前程无忧为什么无法看到返回值和自动无法投递

### Details
Successful strategy from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, strategy
- Pattern-Key: strategy.1773528916916

---

## [LRN-20260314-SAI] best_practice

**Logged**: 2026-03-14T22:55:16.916Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T15:19:00.913Z] 你目前只投递了一个岗位是：品牌策划经理、公司：深圳市冠旭电子股份有限公司、薪资：1.5-2.5万，你回顾一下这个步骤，为什么这个成功了，其余四个没投递上，或者说根本没投递

### Details
Successful strategy from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, strategy
- Pattern-Key: strategy.1773528916916

---

## [ERR-20260314-DQB] reflection

**Logged**: 2026-03-14T22:55:16.916Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T08:32:33.670Z] 所有的投递测试都是一样的流程，都是打开chrome浏览器，我登陆了所以是不需要登陆的，搜索岗位——先排除行业、薪资、地址——点击进入岗位查看jd——匹配度≥80%——点击投递。我现在怀疑你反思系统还是

### Details
Mistake identified from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, error
- Pattern-Key: error.1773528916916

---

## [ERR-20260314-IUM] reflection

**Logged**: 2026-03-14T22:55:16.916Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T14:42:42.888Z] 前程无忧没投递成功，你带着原因去问一下你的gpt老师，告诉他你的运行逻辑还有智联的测试通过数据，以及前程无忧为什么无法看到返回值和自动无法投递

### Details
Mistake identified from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, error
- Pattern-Key: error.1773528916916

---

## [ERR-20260314-EXV] reflection

**Logged**: 2026-03-14T22:55:16.916Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T15:44:09.432Z] 你对于gpt提问这个步骤肯定是出错，你找到昨天晚上21：20，请教GPT：影刀RPA绕过反爬，这个请教内容，然后查看运行的逻辑是什么

### Details
Mistake identified from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, error
- Pattern-Key: error.1773528916916

---

## [ERR-20260314-M65] reflection

**Logged**: 2026-03-14T22:55:16.916Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T16:51:31.835Z] 那你还是无法读取文本，并且无法输入问题

### Details
Mistake identified from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, error
- Pattern-Key: error.1773528916916

---

## [ERR-20260314-A47] reflection

**Logged**: 2026-03-14T22:55:16.916Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
[2026-03-13T16:53:03.218Z] 你检查一下为什么无法输入文本为什么不能读取信息

### Details
Mistake identified from reflection

### Suggested Action
review and promote if applicable

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, error
- Pattern-Key: error.1773528916916

---

