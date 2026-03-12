#!/usr/bin/env node
/**
 * Episodic Memory Auto-Writer
 * 
 * 自动记录用户请求到 Episodic 记忆层
 * 用法：在 OpenClaw hook 中调用
 */

const fs = require('fs');
const path = require('path');

const MEMORY_ROOT = path.join(__dirname);
const EPISODIC_DIR = path.join(MEMORY_ROOT, 'episodic');

/**
 * 追加一条情景记忆到 JSONL 文件
 * @param {Object} episode - 记忆条目
 */
async function appendEpisode(episode) {
  // 确保目录存在
  if (!fs.existsSync(EPISODIC_DIR)) {
    fs.mkdirSync(EPISODIC_DIR, { recursive: true });
  }

  // 获取今日日期 (YYYY-MM-DD)
  const date = new Date().toISOString().slice(0, 10);
  const file = path.join(EPISODIC_DIR, `${date}.jsonl`);
  
  // 构建 JSONL 行
  const line = JSON.stringify(episode, null, 0) + '\n';
  
  // 异步追加写入
  await fs.promises.appendFile(file, line, 'utf8');
  
  console.log(`[Episodic] Recorded: ${episode.type} at ${episode.timestamp}`);
}

/**
 * 构建情景记忆条目
 * @param {Object} context - 上下文信息
 * @returns {Object} 记忆条目
 */
function buildEpisode(context) {
  return {
    timestamp: new Date().toISOString(),
    type: context.type || 'user_request',
    id: `REQ-${Date.now()}`,
    user: context.userMessage || '',
    task_type: context.taskType || 'unknown',
    result: context.result || '',
    tags: context.tags || [],
    session_id: context.sessionId || 'unknown',
    channel: context.channel || 'unknown'
  };
}

/**
 * 主函数 - 记录用户请求
 * @param {Object} context - 上下文
 */
async function recordRequest(context) {
  const episode = buildEpisode(context);
  await appendEpisode(episode);
  return episode;
}

// 导出供 Hook 调用
module.exports = {
  appendEpisode,
  buildEpisode,
  recordRequest
};

// CLI 模式：直接运行测试
if (require.main === module) {
  const testContext = {
    type: 'user_request',
    userMessage: '测试记忆记录',
    taskType: 'test',
    result: '测试成功',
    tags: ['test', 'cli'],
    sessionId: 'test-session',
    channel: 'cli'
  };
  
  recordRequest(testContext)
    .then(ep => console.log('Test passed:', ep.id))
    .catch(err => console.error('Test failed:', err));
}
