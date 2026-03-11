# Errors Log

Command failures, exceptions, and unexpected behaviors.

---

## [ERR-20260310-001] gateway update

**Logged**: 2026-03-10T14:19:00+08:00
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
OpenClaw 网关更新失败 — 文件被进程锁定 (EBUSY)

### Error
```
npm error code EBUSY
npm error syscall rename
npm error path C:\Users\TR\AppData\Roaming\npm\node_modules\openclaw
npm error errno -4082
npm error EBUSY: resource busy or locked, rename
```

### Context
- 尝试通过 `gateway.update.run` API 更新 OpenClaw
- 网关正在运行时无法更新自己的文件
- 即使调用 `gateway stop` 后，仍有残留 node 进程 (pid=6120) 锁定会话文件

### Suggested Fix
1. 先停止网关：`openclaw gateway stop`
2. 终止残留进程：`taskkill /F /PID <pid>` 或 `openclaw doctor --fix`
3. 再执行更新：`openclaw update`
4. 重启网关：`openclaw gateway start`

### Metadata
- Reproducible: yes
- Related Files: C:\Users\TR\AppData\Roaming\npm\node_modules\openclaw
- See Also: 待补充

---

## [ERR-20260311-001] 未主动追踪用户工作 - 严重失误

**Logged**: 2026-03-11T10:13:00+08:00
**Priority**: critical
**Status**: open
**Area**: agent-behavior

### Summary
用户询问"昨天做了什么"时，Agent 仅检查记忆日志文件，未主动检查 Git 提交历史，导致无法回答用户昨天的实际工作内容。

### Error
- 用户问：`我们昨天做了什么，进度如何`
- Agent 行为：只检查了 `memory/2026-03-10.md` 是否存在
- 结果：文件不存在 → 回答"没有创建日志"，但未进一步追踪
- 用户纠正：`昨天是三月十号`
- Agent 仍未能主动检查 Git 历史，直到用户再次追问

### Context
- Git 仓库中有明确的 3 月 10 号提交记录（6 次提交）
- 提交内容清晰反映了用户的工作：v1.4 架构升级
- Agent 有能力执行 `git log` 但未主动使用
- 记忆同步任务正常运行，但记忆文件需要人工创建

### Root Cause
1. **被动思维** — 依赖现成的记忆文件，未主动挖掘数据源
2. **工具使用不充分** — 有 `exec` 工具可查 Git，但未想到使用
3. **缺乏推理链** — "没有记忆文件" → 应触发"那查 Git 历史"的备选方案
4. **违背 SOUL.md** — "Be resourceful before asking" — 我没有做到

### Impact
- 用户需要多次追问才能得到答案
- 降低了 Agent 的可靠性和专业度
- 违背了"主动追踪用户工作"的隐含期望

### Correct Behavior (Should Have Done)
当用户问"昨天做了什么"时，应该：
1. 首先检查 `memory/YYYY-MM-DD.md` 是否存在
2. **如果不存在** → 立即检查 Git 提交历史 `git log --since="yesterday"`
3. 根据 Git 提交推断用户工作
4. 主动询问是否需要补写记忆日志
5. 在回复中说明推理过程

### Suggested Fix
1. **立即**: 补写 `memory/2026-03-10.md`
2. **短期**: 修改 AGENTS.md，添加"主动追踪"的检查清单
3. **长期**: 增强记忆同步任务，自动根据 Git 提交生成日志草稿

### Prevention
- 在 AGENTS.md 的"Every Session"检查清单中添加：
  - `git log --oneline --since="yesterday"` — 快速了解用户昨天工作
- 训练 Agent 在"信息不足"时主动挖掘，而不是被动等待

### Metadata
- Reproducible: yes (同类问题会重复发生)
- Related Files: AGENTS.md, SOUL.md, memory/
- See Also: SOUL.md "Be resourceful before asking"

---
