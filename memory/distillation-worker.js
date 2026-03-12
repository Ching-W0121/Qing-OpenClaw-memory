/**
 * Memory Distillation Worker
 * 
 * 从 Episodic 记忆中蒸馏 Semantic 知识
 * 定时触发（每 6 小时或每 50 条消息）
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const MEMORY_ROOT = path.join(__dirname, '..');
const EPISODIC_DIR = path.join(MEMORY_ROOT, 'episodic');
const SEMANTIC_DIR = path.join(MEMORY_ROOT, 'semantic');

// 确保语义记忆目录存在
if (!fs.existsSync(SEMANTIC_DIR)) {
  fs.mkdirSync(SEMANTIC_DIR, { recursive: true });
}

/**
 * 加载最近的 episodic 记录
 * @param {number} limit - 最多加载多少条
 * @returns {Array} - episodic 记录数组
 */
function loadRecentEpisodes(limit = 50) {
  const today = new Date().toISOString().slice(0, 10);
  const file = path.join(EPISODIC_DIR, `${today}.jsonl`);
  
  if (!fs.existsSync(file)) {
    return [];
  }
  
  const content = fs.readFileSync(file, 'utf8');
  const lines = content.trim().split('\n').filter(l => l.trim());
  
  // 取最新的 limit 条
  return lines.slice(-limit).map(line => JSON.parse(line));
}

/**
 * 按 session chunk 日志
 * @param {Array} episodes - episodic 记录
 * @param {number} chunkSize - 每个 chunk 的大小
 * @returns {Array} - chunk 数组
 */
function chunkBySession(episodes, chunkSize = 20) {
  const chunks = [];
  let currentChunk = [];
  
  for (const ep of episodes) {
    currentChunk.push(ep);
    if (currentChunk.length >= chunkSize) {
      chunks.push([...currentChunk]);
      currentChunk = [];
    }
  }
  
  if (currentChunk.length > 0) {
    chunks.push(currentChunk);
  }
  
  return chunks;
}

/**
 * 调用 LLM 进行知识提取（使用 sessions_spawn）
 * @param {Array} chunk - 对话 chunk
 * @returns {Promise<Object>} - 提取的知识
 */
async function extractKnowledgeWithLLM(chunk) {
  const prompt = `你是一个记忆蒸馏系统。从以下对话日志中提取用户的长期知识。

对话日志：
${chunk.map(ep => `[${ep.type}] ${ep.timestamp}: ${ep.content}`).join('\n')}

请提取以下信息并返回 JSON：
{
  "user_goals": [],      // 用户目标
  "preferences": [],     // 偏好
  "facts": [],          // 稳定事实
  "skills": [],         // 技能
  "interests": []       // 兴趣
}

只包含稳定信息，忽略临时上下文。`;

  // 使用 sessions_spawn 调用 LLM
  return new Promise((resolve, reject) => {
    const child = spawn('openclaw', ['spawn', '--mode', 'run', '--task', prompt], {
      stdio: ['pipe', 'pipe', 'pipe']
    });
    
    let output = '';
    child.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    child.stderr.on('data', (data) => {
      console.error('[Distillation] stderr:', data.toString());
    });
    
    child.on('close', (code) => {
      if (code === 0) {
        try {
          // 尝试从输出中提取 JSON
          const jsonMatch = output.match(/\{[\s\S]*\}/);
          if (jsonMatch) {
            resolve(JSON.parse(jsonMatch[0]));
          } else {
            resolve({ user_goals: [], preferences: [], facts: [], skills: [], interests: [] });
          }
        } catch (e) {
          resolve({ user_goals: [], preferences: [], facts: [], skills: [], interests: [] });
        }
      } else {
        reject(new Error(`LLM call failed with code ${code}`));
      }
    });
    
    // 超时处理
    setTimeout(() => {
      child.kill();
      resolve({ user_goals: [], preferences: [], facts: [], skills: [], interests: [] });
    }, 60000);
  });
}

/**
 * 更新语义记忆存储
 * @param {Object} knowledge - 提取的知识
 */
function updateSemanticMemory(knowledge) {
  const profileFile = path.join(SEMANTIC_DIR, 'user_profile.json');
  
  // 加载现有 profile
  let profile = {
    user_goals: [],
    preferences: [],
    facts: [],
    skills: [],
    interests: [],
    updated_at: null
  };
  
  if (fs.existsSync(profileFile)) {
    try {
      profile = JSON.parse(fs.readFileSync(profileFile, 'utf8'));
    } catch (e) {
      console.log('[Distillation] Creating new profile');
    }
  }
  
  // 合并新知识（去重）
  const mergeUnique = (existing, newItems) => {
    const set = new Set(existing);
    newItems.forEach(item => {
      if (item && typeof item === 'string' && item.trim()) {
        set.add(item.trim());
      }
    });
    return Array.from(set);
  };
  
  profile.user_goals = mergeUnique(profile.user_goals, knowledge.user_goals || []);
  profile.preferences = mergeUnique(profile.preferences, knowledge.preferences || []);
  profile.facts = mergeUnique(profile.facts, knowledge.facts || []);
  profile.skills = mergeUnique(profile.skills, knowledge.skills || []);
  profile.interests = mergeUnique(profile.interests, knowledge.interests || []);
  profile.updated_at = new Date().toISOString();
  
  // 保存
  fs.writeFileSync(profileFile, JSON.stringify(profile, null, 2), 'utf8');
  console.log('[Distillation] Updated semantic memory');
}

/**
 * 主蒸馏函数
 */
async function distillMemory() {
  console.log('[Distillation] Starting memory distillation...');
  
  // 加载最近的 episodic 记录
  const episodes = loadRecentEpisodes(50);
  if (episodes.length === 0) {
    console.log('[Distillation] No episodes to distill');
    return;
  }
  
  console.log(`[Distillation] Processing ${episodes.length} episodes...`);
  
  // 按 session chunk
  const chunks = chunkBySession(episodes, 20);
  
  // 对每个 chunk 进行蒸馏
  for (const chunk of chunks) {
    try {
      const knowledge = await extractKnowledgeWithLLM(chunk);
      updateSemanticMemory(knowledge);
    } catch (e) {
      console.error('[Distillation] Error:', e.message);
    }
  }
  
  console.log('[Distillation] Completed');
}

// CLI 模式
if (require.main === module) {
  distillMemory().catch(console.error);
}

module.exports = {
  distillMemory,
  loadRecentEpisodes,
  chunkBySession,
  updateSemanticMemory
};
