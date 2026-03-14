# 前程无忧投递修复测试报告

**修复日期**: 2026-03-14 12:30  
**问题**: 5 个职位仅成功 1 个，其余 4 个失败  
**原因**: DOM ref 失效（React SPA 页面重新渲染）  
**解决方案**: GPT 工程级分析 + 重新 snapshot 策略

---

## 🔍 问题分析（GPT 咨询）

### 核心原因
前程无忧 (51job) 是 **React SPA 单页应用**，点击职位后 DOM 会重新渲染：

```
初始 snapshot → ref(e190) → DOM index pointer
                      ↓
            点击职位后 DOM 重新渲染
                      ↓
            e190 → 指向不存在的节点 → 点击失败
```

### 为什么第 1 个成功？
- 初始 snapshot 后，DOM 还没变化
- 流程：`snapshot → click job → click apply` 还能用

### 为什么第 2-5 个失败？
- 点击第 1 个职位后，列表 DOM 重新渲染
- 原来的 `e190`、`e280` 已经失效
- 点击的是**错误的 DOM 节点**

---

## ✅ 修复方案

### 3 条关键规则

| 规则 | 说明 | 实现 |
|------|------|------|
| **规则 1** | 任何点击后都要重新 snapshot | 每次 `browser.act()` 后调用 `browser.snapshot()` |
| **规则 2** | 绝对不要复用旧 ref | 每次操作前重新获取 ref |
| **规则 3** | 列表页必须重新 snapshot | 返回职位列表后立即 snapshot |

### 优化措施

| 优化项 | 原实现 | 新实现 |
|--------|--------|--------|
| 等待时间 | 固定 2 秒 | 随机 3-5 秒 |
| ref 获取 | 只获取 1 次 | 每次操作前重新获取 |
| 按钮查找 | 无 | `_find_apply_button_ref()` 动态查找 |
| 状态判断 | 无 | 检查"投递成功"/"已投递"等状态 |
| 确认弹窗 | 无 | 自动处理确认弹窗 |
| 反爬规避 | 无 | 随机等待 + 状态检查 |
| 批量投递 | 无 | `batch_apply()` 每 3 个暂停 20 秒 |

---

## 📝 代码修改

### 修改文件
`qing-agent/services/application_service.py`

### 新增方法
| 方法 | 说明 |
|------|------|
| `_apply_51job()` | 前程无忧投递（GPT 优化版） |
| `_find_apply_button_ref()` | 从 snapshot 动态查找投递按钮 ref |
| `_extract_text()` | 从元素中提取文本 |
| `batch_apply()` | 批量投递（带反爬保护） |

### 关键改动

#### 1. 随机等待（反自动化）
```python
# 原代码
await asyncio.sleep(2)

# 新代码
wait_time = random.uniform(3, 5)
await asyncio.sleep(wait_time)
```

#### 2. 每次操作后重新 snapshot
```python
# 打开页面 → 等待 → snapshot
await browser.open(url)
await asyncio.sleep(random.uniform(3, 5))
snapshot = await browser.snapshot(refs="aria")

# 点击后 → 等待 → snapshot
await browser.act(kind="click", ref=apply_ref)
await asyncio.sleep(random.uniform(2, 3))
result_snapshot = await browser.snapshot(refs="aria")
```

#### 3. 动态查找投递按钮 ref
```python
def _find_apply_button_ref(self, snapshot) -> Optional[str]:
    """从 snapshot 中查找投递按钮的 ref"""
    # 递归查找 button/link 元素
    # 文本包含"投递"或"申请"
    # 返回 ref
```

#### 4. 状态判断
```python
# 检查成功状态
if any(s in snapshot_text for s in ['投递成功', '申请成功', '已投递']):
    return {'status': 'success', ...}

# 检查确认弹窗
if any(s in snapshot_text for s in ['确认', '确定', '提交简历']):
    # 自动点击确认

# 检查重复投递
if any(s in snapshot_text for s in ['已投递', '重复投递']):
    return {'status': 'success', 'message': '该职位已投递过', ...}
```

---

## 🧪 测试计划

### 测试环境
- 平台：前程无忧网页版
- 职位：品牌策划（深圳）
- 数量：5 个职位

### 测试步骤
1. 运行投递脚本
2. 记录每个职位的投递结果
3. 检查前程无忧后台投递记录
4. 统计成功率

### 预期结果
| 指标 | 修复前 | 修复后（预期） |
|------|--------|----------------|
| 成功率 | 20% (1/5) | ≥90% (≥4.5/5) |
| 平均耗时 | ~10s/职位 | ~15-20s/职位 |
| 反爬触发 | 未知 | 低（随机等待） |

---

## 📊 测试记录

### 测试 1（待执行）
**时间**: 2026-03-14 下午  
**职位数**: 5  
**成功数**: 待测试  
**失败数**: 待测试  
**问题**: 待记录

### 测试 2（待执行）
**时间**: 2026-03-14 下午  
**职位数**: 5  
**成功数**: 待测试  
**失败数**: 待测试  
**问题**: 待记录

---

## 🚀 下一步优化

### 短期（本周）
- [ ] 执行真实投递测试
- [ ] 根据测试结果微调等待时间
- [ ] 添加日志记录（便于调试）

### 中期（v1.5）
- [ ] 添加浏览器滚动（确保按钮可见）
- [ ] 每 3 个职位暂停 20 秒
- [ ] 添加投递失败重试机制

### 长期（v2.0）
- [ ] 使用 Playwright 替代 browser 工具（更稳定）
- [ ] 添加视觉验证（OCR 确认投递状态）
- [ ] 分布式投递（多浏览器实例）

---

## 💡 GPT 评价

> "你的 Agent 架构是正确的，只是 51job 的 DOM 更动态。"
> "遵循上述规则后成功率可达 90%+"
> "这套其实就是很多 AI 求职 Agent 的底层实现。"

---

**修复状态**: ✅ 代码完成，待测试  
**测试状态**: ⏳ 待执行  
**预计成功率**: ≥90%
