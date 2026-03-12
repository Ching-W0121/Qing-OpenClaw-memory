/**
 * Memory Reflection Worker
 * 
 * 从经历中反思，提取经验教训和策略
 * 定时触发（每 6 小时或失败时）
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
 */
function loadRecentEpisodes(limit = 50) {
  const today = new Date().toISOString().slice(0, 10);
  const file = path.join(EPISODIC_DIR, `${today}.jsonl`);
  
  if (!fs.existsSync(file)) return [];
  
  const content = fs.readFileSync(file, 'utf8');
  const lines = content.trim().split('\n').filter(l => l.trim());
  return lines.slice(-limit).map(line => JSON.parse(line));
}

/**
 * 调用 LLM 进行反思
 * @param {Array} episodes - 对话记录
 * @returns {Promise<Object>} - 反思结果
 */
async function reflectWithLLM(episodes) {
  const prompt = `你是一个 AI 反思系统。回顾以下对话经历，提取经验教训。

对话日志：
${episodes.map(ep => `[${ep.type}] ${ep.timestamp}: ${ep.content}`).join('\n')}

请识别：
1. 重要模式（important patterns）
2. 错误/失败（mistakes）
3. 成功策略（successful strategies）
4. 未来行为的教训（lessons for future behavior）

返回 JSON：
{
  "lessons": [],      // 教训
  "strategies": [],   // 策略
  "mistakes": [],     // 错误
  "patterns": []      // 模式
}

聚焦于可操作的知识，帮助未来做出更好的决策。`;

  return new Promise((resolve, reject) => {
    const child = spawn('openclaw', ['spawn', '--mode', 'run', '--task', prompt], {
      stdio: ['pipe', 'pipe', 'pipe']
    });
    
    let output = '';
    child.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    child.stderr.on('data', (data) => {
      console.error('[Reflection] stderr:', data.toString());
    });
    
    child.on('close', (code) => {
      if (code === 0) {
        try {
          const jsonMatch = output.match(/\{[\s\S]*\}/);
          if (jsonMatch) {
            resolve(JSON.parse(jsonMatch[0]));
          } else {
            resolve({ lessons: [], strategies: [], mistakes: [], patterns: [] });
          }
        } catch (e) {
          resolve({ lessons: [], strategies: [], mistakes: [], patterns: [] });
        }
      } else {
        reject(new Error(`LLM call failed with code ${code}`));
      }
    });
    
    setTimeout(() => {
      child.kill();
      resolve({ lessons: [], strategies: [], mistakes: [], patterns: [] });
    }, 60000);
  });
}

/**
 * 更新策略记忆存储
 * @param {Object} reflection - 反思结果
 */
function updateStrategyMemory(reflection) {
  const lessonsFile = path.join(SEMANTIC_DIR, 'lessons.json');
  
  // 加载现有 lessons
  let lessons = {
    lessons: [],
    strategies: [],
    mistakes: [],
    patterns: [],
    updated_at: null
  };
  
  if (fs.existsSync(lessonsFile)) {
    try {
      lessons = JSON.parse(fs.readFileSync(lessonsFile, 'utf8'));
    } catch (e) {
      console.log('[Reflection] Creating new lessons file');
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
  
  lessons.lessons = mergeUnique(lessons.lessons, reflection.lessons || []);
  lessons.strategies = mergeUnique(lessons.strategies, reflection.strategies || []);
  lessons.mistakes = mergeUnique(lessons.mistakes, reflection.mistakes || []);
  lessons.patterns = mergeUnique(lessons.patterns, reflection.patterns || []);
  lessons.updated_at = new Date().toISOString();
  
  // 保存
  fs.writeFileSync(lessonsFile, JSON.stringify(lessons, null, 2), 'utf8');
  console.log('[Reflection] Updated strategy memory');
}

/**
 * 主反思函数
 */
async function reflectOnMemory() {
  console.log('[Reflection] Starting memory reflection...');
  
  // 加载最近的 episodic 记录
  const episodes = loadRecentEpisodes(50);
  if (episodes.length === 0) {
    console.log('[Reflection] No episodes to reflect on');
    return;
  }
  
  console.log(`[Reflection] Processing ${episodes.length} episodes...`);
  
  try {
    const reflection = await reflectWithLLM(episodes);
    updateStrategyMemory(reflection);
    console.log('[Reflection] Completed');
  } catch (e) {
    console.error('[Reflection] Error:', e.message);
  }
}

// CLI 模式
if (require.main === module) {
  reflectOnMemory().catch(console.error);
}

module.exports = {
  reflectOnMemory,
  loadRecentEpisodes,
  updateStrategyMemory
};
