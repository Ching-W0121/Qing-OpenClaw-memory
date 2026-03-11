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

## [ERR-20260311-002] 时间范围理解错误 + 记忆检索失败

**Logged**: 2026-03-11T14:30:00+08:00  
**Priority**: critical  
**Status**: open  
**Area**: agent-behavior, memory-system

### Summary
用户问"两点之后叫你做了什么"，Agent 错误理解为"当前新会话"而非"14:00 之后的时间段"，导致无法回答。

### Error
- 用户问：`我刚才两点之后叫你做了什么` (14:23)
- Agent 理解：以为问的是"新会话 (14:21 开始) 后做了什么"
- Agent 回答："这是新会话，我还没有执行任何任务"
- 实际情况：14:03 有自动记忆同步任务 (cron)，且上一个会话中可能有用户请求
- 用户纠正：指出我没回答上来，反应慢了

### Context
- 新会话于 14:21 启动
- 用户在 14:23 问"两点之后"的任务
- cron 任务在 14:03 执行了记忆同步（每小时一次）
- requests.json 中可能记录了 14:00 之后的用户请求
- 上一个会话 (14:00-14:21) 的历史未查看

### Root Cause
1. **时间范围理解错误** — "两点之后"是绝对时间 (14:00+)，不是"会话开始后"
2. **未主动检索** — 没有检查 requests.json 中 14:00 之后的请求
3. **未检查 cron 记录** — 忽略了定时任务的执行历史
4. **跨会话失忆** — 新会话没有主动查看上一个会话的历史
5. **违背 GPT 老师原则** — "记忆的第一原则是帮助 AI 回答用户的过去问题"

### Impact
- 用户需要指出错误才能得到正确答案
- 降低了记忆系统的可信度
- 违背了"快速检索过去请求"的核心能力

### Correct Behavior (Should Have Done)
当用户问"两点之后叫你做了什么"时，应该：
1. **理解时间范围** — "两点之后" = 14:00 至今，不是"会话开始后"
2. **检查 requests.json** — 筛选 timestamp >= "2026-03-11 14:00" 的请求
3. **检查 cron 执行历史** — 查看 14:00 之后的定时任务
4. **检查 Git 提交** — 查看 14:00 之后的自动同步记录
5. **综合回答** — 给出完整的任务清单

### Suggested Fix
1. **立即**: 更新 AGENTS.md 添加时间理解规则
2. **短期**: 修改 memory_search.py 支持时间范围查询
3. **长期**: 添加 cron 执行历史查询功能

### Prevention
- 在 AGENTS.md 中添加：
  - 当用户提到"刚才/今天/上周 + 具体时间"时，按绝对时间检索
  - 不要按会话边界理解时间
- 在 scripts/memory_search.py 中添加 `--since` 和 `--until` 参数
- 在 cron.list 或 cron.runs 中查看定时任务执行历史

### GPT 老师指导原则（3 月 11 日咨询）
> 记录"用户意图"，而不是"系统行为"  
> 记忆的第一原则是帮助 AI 回答用户的"过去问题"

**我违背了原则**：当用户问"过去我让你做了什么"时，我没有快速检索并回答

### Metadata
- Reproducible: yes (同类时间理解问题会重复发生)
- Related Files: AGENTS.md, requests.json, memory/, cron
- See Also: ERR-20260311-001 (同属主动追踪不足)

---
