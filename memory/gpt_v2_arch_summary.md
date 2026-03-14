# GPT 老师咨询 - 青 Agent v2.0 架构设计（已记忆）

**咨询日期**: 2026-03-14 15:41  
**状态**: ✅ 已记忆并保存

## 📊 核心架构（7 个模块）

1. **Job Collector** - 多平台爬虫（智联 + 前程无忧 + 拉勾 + 猎聘）
2. **Job Normalizer** - 职位标准化（统一 schema）
3. **Dedup Engine** - 去重系统（hash + fuzzy match）
4. **Feature Extractor** - 特征提取（技能/薪资/城市/行业/经验/学历）
5. **Matching Engine** - AI 匹配系统（动态权重 + 用户反馈）
6. **Job Heat Score** - 职位热度系统（发布时间/竞争度）
7. **Application Tracker** - 投递追踪系统
8. **Notification Engine** - 推送系统（个性化时间 + 渠道）

## 🛠️ 技术选型

| 组件 | 推荐 | 说明 |
|------|------|------|
| Backend | FastAPI | 高性能异步 |
| Database | PostgreSQL | 全文搜索+json 字段 |
| Cache | Redis | 缓存推荐 + 任务队列 |
| 向量数据库 | Qdrant | 职位匹配 |
| 爬虫 | Playwright | 反爬能力强 |
| 任务调度 | Celery/APScheduler | 定时任务 |

## 📈 实施路线图

- **Phase 1（2 周）**: 多平台 + 稳定（爬虫 + 去重）
- **Phase 2（3 周）**: 智能推荐（embedding+ 动态评分 + 热度）
- **Phase 3（2 周）**: 闭环系统（投递追踪 + 行为学习 + 个性化推送）

## 📁 已保存文档

- `GPT 咨询_青 Agent v2.0 架构设计_2026-03-14.md`

---

**已记忆，现在打开正确的对话框"前程无忧自动化抓取问题"**
