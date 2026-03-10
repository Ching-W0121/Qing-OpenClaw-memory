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
