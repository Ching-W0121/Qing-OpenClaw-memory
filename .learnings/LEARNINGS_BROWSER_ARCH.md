## [LRN-20260315-002] 浏览器自动化工业级架构 🔴

**Logged**: 2026-03-15T02:05:00+08:00
**Priority**: critical
**Status**: pending
**Area**: browser_automation

### Summary
庆提供的工业级浏览器自动化架构：动态寻址 + 异常阻断与重启

### Details

**问题根源**：
1. 全局复用单一 page 对象 → Tab 关闭后继续使用旧引用
2. 不处理新标签页弹出 → 控制权留在旧页面
3. 重试机制错误 → 在错的页面上重复尝试

**解决方案**：

#### 1. 动态获取最新活跃 Tab
```python
def get_active_page(context):
    """永远返回浏览器中最新打开的那个标签页"""
    pages = context.pages
    if not pages:
        raise Exception("Browser has no open tabs!")
    return pages[-1]  # 获取列表中的最后一个，通常是最新弹出的
```

#### 2. 拥抱并拦截"新标签页"
```python
async def click_and_catch_new_tab(context, page, selector):
    # 告诉上下文：准备好迎接一个新页面的诞生
    async with context.expect_page() as new_page_info:
        await page.click(selector)  # 执行点击动作
    
    # 获取新弹出的页面实例
    new_page = await new_page_info.value
    await new_page.wait_for_load_state()
    
    return new_page  # 接下来所有的操作，都要基于这个 new_page
```

#### 3. 终极防御：自愈装饰器
```python
import functools
import logging

def auto_heal_browser_tool(max_retries=3):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(self, *args, **kwargs)
                except Exception as e:
                    error_msg = str(e).lower()
                    if "tab not found" in error_msg or "target closed" in error_msg:
                        logging.warning(f"检测到标签页丢失 (尝试 {attempt + 1}/{max_retries})，正在触发自愈机制...")
                        
                        # 【核心自愈动作】
                        # 1. 强制关闭当前损坏的上下文
                        # 2. 重新初始化一个干净的浏览器上下文
                        # 3. 重新导航到目标 URL
                        await self.reboot_browser_context()
                        
                        if attempt == max_retries - 1:
                            raise Exception("浏览器自愈失败，超出最大重试次数")
                    else:
                        raise e
        return wrapper
    return decorator
```

### Suggested Action
1. 重构 browser 工具函数
2. 添加 get_active_page() 动态获取
3. 添加 click_and_catch_new_tab() 处理新标签页
4. 添加 auto_heal_browser_tool() 装饰器
5. 所有 browser 操作使用自愈机制

### Metadata
- Source: user_feedback
- Related Files: browser.py, memory_guard.py
- Tags: browser_automation, architecture, critical
- Pattern-Key: automation.industrial_grade
- See Also: ERR-20260315-002
