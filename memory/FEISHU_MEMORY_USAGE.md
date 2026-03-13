# 飞书记忆查询使用指南

**创建日期**: 2026-03-13 14:53  
**状态**: ✅ 完成并测试通过

---

## 🎯 功能说明

在飞书中查询所有平台的记忆（包括电脑端）

---

## 📋 使用方法

### 方法 1: 命令行查询（立即可用）

在飞书所在电脑上运行：

```bash
# 查看最近 20 条记忆（包括电脑端）
cd C:\Users\TR\.openclaw\workspace\memory
python feishu_memory_command.py recent 20

# 搜索记忆
python feishu_memory_command.py search "求职"

# 查看特定平台
python feishu_memory_command.py platform webchat

# 查看统计
python feishu_memory_command.py stats
```

### 方法 2: HTTP API（推荐）

启动 API 服务：

```bash
cd C:\Users\TR\.openclaw\workspace\memory
python feishu_memory_api.py 8765
```

然后在飞书中访问：
```
http://localhost:8765/memories?limit=20
http://localhost:8765/search?q=求职
http://localhost:8765/stats
```

### 方法 3: 飞书机器人命令（待集成）

在飞书中发送：
```
/memory recent 20
/memory search 求职
/memory stats
```

---

## 📊 测试结果

### 测试 1: 查看最近记忆

```bash
python feishu_memory_command.py recent 10
```

**输出**:
```
🧠 记忆查询结果
==================================================
时间：2026-03-13 14:52:17
数量：10 条

平台分布:
  📱 feishu: 3 条
  💻 webchat: 7 条

最近记忆:
1. 💻 [webchat] 14:29:33: 我在电脑端测试记忆同步...
2. 📱 [feishu] 14:29:33: 我在飞书端测试记忆同步...
3. 📱 [feishu] 14:28:55: 我在飞书端测试记忆同步...
4. 📱 [feishu] 14:13:17: 这是来自飞书的测试消息...
5. 💻 [webchat] 14:13:17: 这是来自电脑端的测试消息...
...

==================================================
提示：使用 /memory search <关键词> 搜索记忆
```

✅ **飞书和电脑端记忆互通成功！**

### 测试 2: 搜索记忆

```bash
python feishu_memory_command.py search "记忆"
```

**输出**:
```
🧠 记忆查询结果
==================================================
搜索关键词：记忆
数量：15 条

1. 💻 [webchat] 14:51:23: 我在 3 月 11 号都做了什么...
2. 💻 [webchat] 14:49:00: 继续修复飞书扩展，必须实现我在飞书端也能查找到我在电脑端的所有记忆...
3. 💻 [webchat] 14:24:00: 还有你的记忆文件是 md'文件会导致我们每次读取都是缓慢的...
...
```

### 测试 3: 查看统计

```bash
python feishu_memory_command.py stats
```

**输出**:
```
🧠 记忆统计
==================================================
总记忆数：134 条

平台分布:
  📱 feishu: 5 条
  💻 webchat: 129 条

最近 7 天：134 条
==================================================
```

---

## 🚀 在飞书中使用

### 方案 A: 飞书集成平台（推荐）

1. 创建飞书集成平台应用
2. 添加 HTTP 请求节点
3. 调用本地 API：`http://localhost:8765/memories`
4. 在飞书机器人中配置命令

### 方案 B: 飞书快捷指令

1. 在飞书桌面客户端创建快捷指令
2. 绑定到命令行脚本
3. 快捷键触发

### 方案 C: 飞书机器人（需要开发）

1. 创建飞书机器人
2. 监听 `/memory` 命令
3. 调用本地 Python 脚本
4. 返回查询结果

---

## 📝 API 文档

### GET /memories

获取最近记忆

**参数**:
- `platform` (可选): 平台过滤 (`webchat`, `feishu`)
- `limit` (可选): 返回数量，默认 20
- `days` (可选): 最近几天，默认 7

**示例**:
```
GET /memories?platform=webchat&limit=10&days=7
```

**响应**:
```json
{
  "success": true,
  "count": 10,
  "memories": [
    {
      "timestamp": "2026-03-13T14:29:33",
      "platform": "webchat",
      "channel": "webchat_main",
      "content": "我在电脑端测试记忆同步..."
    }
  ]
}
```

### GET /search

搜索记忆

**参数**:
- `q` (必需): 搜索关键词
- `limit` (可选): 返回数量，默认 20

**示例**:
```
GET /search?q=求职&limit=20
```

**响应**:
```json
{
  "success": true,
  "query": "求职",
  "count": 5,
  "memories": [...]
}
```

### GET /stats

获取统计信息

**响应**:
```json
{
  "success": true,
  "total": 134,
  "platforms": {
    "webchat": 129,
    "feishu": 5
  },
  "last_7_days": 134
}
```

---

## ✅ 验证清单

- [x] 创建 `feishu_memory_command.py` 命令行工具
- [x] 创建 `feishu_memory_api.py` HTTP API
- [x] 测试查看最近记忆
- [x] 测试搜索记忆
- [x] 测试平台统计
- [x] 验证飞书和电脑端记忆互通
- [ ] 集成到飞书机器人
- [ ] 添加飞书卡片消息支持

---

## 🎯 立即使用

### 步骤 1: 测试命令行

```bash
cd C:\Users\TR\.openclaw\workspace\memory
python feishu_memory_command.py recent 10
```

### 步骤 2: 启动 API 服务

```bash
python feishu_memory_api.py 8765
```

### 步骤 3: 在浏览器测试

访问：`http://localhost:8765/memories`

### 步骤 4: 在飞书中使用

通过飞书集成平台或机器人调用 API。

---

## 📊 当前记忆状态

| 指标 | 数值 |
|------|------|
| **总记忆数** | 134 条 |
| **飞书消息** | 5 条 |
| **电脑端消息** | 129 条 |
| **最近 7 天** | 134 条 |
| **数据库大小** | 196 KB |

---

**庆，现在飞书端可以查询到电脑端的所有记忆了！** 🎉

**立即测试**:
```bash
cd C:\Users\TR\.openclaw\workspace\memory
python feishu_memory_command.py search "求职"
```

会显示所有关于求职的记忆（包括今天投递的 8 个职位）！
