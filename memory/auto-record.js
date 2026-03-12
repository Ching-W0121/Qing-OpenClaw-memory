#!/usr/bin/env node
/**
 * 自动记录当前会话到 Episodic 记忆
 * 由 cron 定时任务调用
 * 
 * 注意：此脚本需要配合 OpenClaw session 使用
 * 通过 sessions_history 获取数据后调用此脚本写入
 */

const fs = require('fs');
const path = require('path');

const MEMORY_ROOT = path.join(__dirname, '..', 'memory');
const EPISODIC_DIR = path.join(MEMORY_ROOT, 'episodic');

// 确保目录存在
if (!fs.existsSync(EPISODIC_DIR)) {
  fs.mkdirSync(EPISODIC_DIR, { recursive: true });
}

// 获取今日文件
const date = new Date().toISOString().slice(0, 10);
const file = path.join(EPISODIC_DIR, `${date}.jsonl`);

// 读取已存在的记录，避免重复
const existingIds = new Set();
if (fs.existsSync(file)) {
  const content = fs.readFileSync(file, 'utf8');
  content.split('\n').forEach(line => {
    if (line.trim()) {
      try {
        const entry = JSON.parse(line);
        if (entry.id) existingIds.add(entry.id);
      } catch (e) {}
    }
  });
}

// 从 stdin 或参数获取会话数据
let messages = [];
const input = process.argv[2] || '';
if (input.startsWith('{')) {
  try {
    messages = JSON.parse(input).messages || [];
  } catch (e) {
    console.error('[Episodic Auto] Failed to parse input JSON');
    process.exit(1);
  }
}

// 提取用户请求并记录
let recorded = 0;
messages.forEach((msg, idx) => {
  if (msg.role === 'user' && msg.content && typeof msg.content === 'string') {
    // 跳过系统事件和心跳
    if (msg.content.includes('System:') || msg.content.includes('HEARTBEAT')) return;
    
    const id = `REQ-${msg.timestamp || Date.now()}`;
    if (!existingIds.has(id)) {
      const episode = {
        timestamp: new Date(msg.timestamp || Date.now()).toISOString(),
        type: 'user_request',
        id: id,
        user: msg.content.substring(0, 500),
        task_type: 'auto_record',
        result: 'auto_captured',
        tags: ['auto', 'cron'],
        session_id: 'agent:main:main',
        channel: 'cron'
      };
      fs.appendFileSync(file, JSON.stringify(episode) + '\n', 'utf8');
      recorded++;
    }
  }
});

console.log(`[Episodic Auto] Recorded ${recorded} new entries at ${new Date().toISOString()}`);
process.exit(0);
