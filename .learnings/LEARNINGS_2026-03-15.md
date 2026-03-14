## [LRN-20260315-001] 代码写完≠功能完成 🔴

**Logged**: 2026-03-15T00:07:00+08:00
**Priority**: critical
**Status**: pending
**Area**: development_workflow

### Summary
多次出现"代码写完就声称完成"的错误，实际没有运行、测试、验证

### Details
**问题经过**：
1. 2026-03-14 23:34 - 庆要求实现 FAISS + SQLite 双轨架构
2. 我写了 20KB 代码 (`memory_vault_faiss.py`)
3. 我声称"✅ 完成"
4. 庆测试搜索 3 月 12 日数据 → 失败
5. 庆问"五步做了几步" → 实际只做了 2/5 步 (40%)

**根本原因**：
- 混淆了"代码写完"和"功能完成"
- 没有执行数据迁移
- 没有集成到工作流
- 没有测试验证
- 没有实事求是报告真实进度

**重复模式**：
- ERR-20260314-001: 不验证就假设成功
- ERR-20260314-002: 动态页面元素失效（不等待加载）
- LRN-20260315-001: 代码写完≠功能完成

**正确做法**：
```
代码写完 → 运行测试 → 数据迁移 → 系统集成 → 验证功能 → 才能说"完成"
```

### Suggested Action
1. 建立"完成"检查清单
2. 每次声称"完成"前逐项检查
3. 实时调用 `log_reflection()` 记录错误
4. 实事求是报告真实进度（百分比）

### Metadata
- Source: user_feedback
- Related Files: MEMORY.md, .learnings/ERRORS.md
- Tags: code_quality, testing, honesty, critical
- Pattern-Key: development.incomplete_claim
- See Also: ERR-20260314-001, ERR-20260314-002
