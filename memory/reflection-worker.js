/**
 * Memory Reflection Worker v2.0
 * 
 * 整合 self-improvement v3.0.1 技能
 * 从经历中反思，提取经验教训和策略
 * 定时触发（每 6 小时或失败时）
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const MEMORY_ROOT = __dirname;  // memory/ directory
const WORKSPACE_ROOT = path.join(MEMORY_ROOT, '..');
const EPISODIC_DIR = path.join(MEMORY_ROOT, 'episodic');
const SEMANTIC_DIR = path.join(MEMORY_ROOT, 'semantic');
const LEARNINGS_DIR = path.join(WORKSPACE_ROOT, '.learnings');

// 确保目录存在
if (!fs.existsSync(SEMANTIC_DIR)) {
  fs.mkdirSync(SEMANTIC_DIR, { recursive: true });
}
if (!fs.existsSync(LEARNINGS_DIR)) {
  fs.mkdirSync(LEARNINGS_DIR, { recursive: true });
}

/**
 * 加载最近的 episodic 记录（包括今天和昨天）
 */
function loadRecentEpisodes(limit = 50) {
  const today = new Date().toISOString().slice(0, 10);
  const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
  
  const episodes = [];
  
  // 加载今天的记录
  const todayFile = path.join(EPISODIC_DIR, `${today}.jsonl`);
  if (fs.existsSync(todayFile)) {
    const content = fs.readFileSync(todayFile, 'utf8');
    const lines = content.trim().split('\n').filter(l => l.trim());
    episodes.push(...lines.map(line => JSON.parse(line)));
  }
  
  // 加载昨天的记录
  const yesterdayFile = path.join(EPISODIC_DIR, `${yesterday}.jsonl`);
  if (fs.existsSync(yesterdayFile)) {
    const content = fs.readFileSync(yesterdayFile, 'utf8');
    const lines = content.trim().split('\n').filter(l => l.trim());
    episodes.push(...lines.map(line => JSON.parse(line)));
  }
  
  // 返回最近的 limit 条
  return episodes.slice(-limit);
}

/**
 * 调用 LLM 进行反思（使用简单规则而非 LLM，避免依赖）
 * @param {Array} episodes - 对话记录
 * @returns {Promise<Object>} - 反思结果
 */
async function reflectWithLLM(episodes) {
  // 简单规则提取模式
  const lessons = [];
  const strategies = [];
  const mistakes = [];
  const patterns = [];
  
  // 检测错误模式
  const errorKeywords = ['错误', '失败', '不行', '无法', '报错', '错', 'fail', 'error'];
  const successKeywords = ['成功', '完成', '好了', '搞定', 'ok', 'success'];
  const correctionKeywords = ['不对', '错了', '不是', '应该', '纠正', 'wrong', 'correct'];
  
  episodes.forEach(ep => {
    const content = ep.content.toLowerCase();
    
    // 检测错误
    if (errorKeywords.some(k => content.includes(k))) {
      mistakes.push(`[${ep.timestamp}] ${ep.content.substring(0, 100)}`);
    }
    
    // 检测成功
    if (successKeywords.some(k => content.includes(k))) {
      strategies.push(`[${ep.timestamp}] ${ep.content.substring(0, 100)}`);
    }
    
    // 检测纠正
    if (correctionKeywords.some(k => content.includes(k))) {
      lessons.push(`[${ep.timestamp}] ${ep.content.substring(0, 100)}`);
    }
  });
  
  // 提取通用模式
  if (mistakes.length > 0) {
    patterns.push('错误时需要立即记录并反思根本原因');
  }
  if (lessons.length > 0) {
    patterns.push('用户纠正时立即记录到 LEARNINGS.md');
  }
  if (strategies.length > 0) {
    patterns.push('成功策略应该被记录和复用');
  }
  
  return { lessons, strategies, mistakes, patterns };
}

/**
 * 生成学习条目 ID
 * @returns {string} - 格式：LRN-YYYYMMDD-XXX
 */
function generateLearningId() {
  const date = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const random = Math.random().toString(36).substring(2, 5).toUpperCase();
  return `LRN-${date}-${random}`;
}

/**
 * 生成错误条目 ID
 * @returns {string} - 格式：ERR-YYYYMMDD-XXX
 */
function generateErrorId() {
  const date = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const random = Math.random().toString(36).substring(2, 5).toUpperCase();
  return `ERR-${date}-${random}`;
}

/**
 * 格式化反思结果为学习条目（self-improvement v3.0.1 格式）
 * @param {string} type - 'learning' | 'error' | 'strategy'
 * @param {Object} item - 反思项目
 * @param {string} id - 条目 ID
 * @returns {string} - Markdown 格式的条目
 */
function formatLearningEntry(type, item, id) {
  const timestamp = new Date().toISOString();
  const category = type === 'error' ? 'reflection' : 'best_practice';
  
  return `## [${id}] ${category}

**Logged**: ${timestamp}
**Priority**: medium
**Status**: pending
**Area**: backend

### Summary
${item.summary || item}

### Details
${item.details || item.description || '通过反思系统自动生成'}

### Suggested Action
${item.action || item.suggestedAction || 'review and promote if applicable'}

### Metadata
- Source: reflection-worker
- Related Files: memory/semantic/lessons.json
- Tags: reflection, ${type}
- Pattern-Key: ${type}.${Date.now()}

---

`;
}

/**
 * 更新策略记忆存储 AND log to .learnings/ (self-improvement v3.0.1 integration)
 * @param {Object} reflection - 反思结果
 */
function updateStrategyMemory(reflection) {
  const lessonsFile = path.join(SEMANTIC_DIR, 'lessons.json');
  const learningsFile = path.join(LEARNINGS_DIR, 'LEARNINGS.md');
  const errorsFile = path.join(LEARNINGS_DIR, 'ERRORS.md');
  
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
  
  // 保存 lessons.json
  fs.writeFileSync(lessonsFile, JSON.stringify(lessons, null, 2), 'utf8');
  console.log('[Reflection] Updated strategy memory (lessons.json)');
  
  // Log to .learnings/LEARNINGS.md (self-improvement v3.0.1 format)
  let learningsContent = '';
  if (fs.existsSync(learningsFile)) {
    learningsContent = fs.readFileSync(learningsFile, 'utf8');
  }
  
  // Add new learnings
  if (reflection.lessons && reflection.lessons.length > 0) {
    reflection.lessons.forEach(item => {
      const id = generateLearningId();
      const entry = formatLearningEntry('learning', item, id);
      learningsContent += entry;
      console.log(`[Reflection] Logged learning: ${id}`);
    });
  }
  
  if (reflection.strategies && reflection.strategies.length > 0) {
    reflection.strategies.forEach(item => {
      const id = generateLearningId();
      const entry = formatLearningEntry('strategy', { summary: item, description: 'Successful strategy from reflection' }, id);
      learningsContent += entry;
      console.log(`[Reflection] Logged strategy: ${id}`);
    });
  }
  
  if (reflection.mistakes && reflection.mistakes.length > 0) {
    reflection.mistakes.forEach(item => {
      const id = generateErrorId();
      const entry = formatLearningEntry('error', { summary: item, description: 'Mistake identified from reflection' }, id);
      learningsContent += entry;
      console.log(`[Reflection] Logged mistake: ${id}`);
    });
  }
  
  // Save learnings file
  if (learningsContent) {
    fs.writeFileSync(learningsFile, learningsContent, 'utf8');
    console.log('[Reflection] Updated LEARNINGS.md (self-improvement v3.0.1 format)');
  }
  
  // Auto-promote recurring patterns to workspace files
  autoPromotePatterns(lessons);
}

/**
 * Auto-promote patterns to workspace files (SOUL.md, AGENTS.md, TOOLS.md)
 * Based on self-improvement v3.0.1 promotion rules
 */
function autoPromotePatterns(lessons) {
  const patternsToPromote = lessons.patterns.filter(p => {
    // Simple heuristic: patterns mentioned multiple times
    return lessons.patterns.filter(x => x === p).length >= 2;
  });
  
  if (patternsToPromote.length === 0) return;
  
  console.log(`[Reflection] Found ${patternsToPromote.length} patterns to promote`);
  
  // Promote to TOOLS.md (tool gotchas)
  const toolsFile = path.join(WORKSPACE_ROOT, 'TOOLS.md');
  if (fs.existsSync(toolsFile)) {
    let toolsContent = fs.readFileSync(toolsFile, 'utf8');
    
    // Check if reflection section exists
    if (!toolsContent.includes('## 🧠 Reflection System')) {
      const section = `
---

## 🧠 Reflection System (self-improvement v3.0.1)

- **Automatic logging**: Lessons logged to \`.learnings/LEARNINGS.md\`
- **Reflection schedule**: Every 6 hours via reflection-worker.js
- **Promotion targets**:
  - Behavioral patterns → \`SOUL.md\`
  - Workflow improvements → \`AGENTS.md\`
  - Tool gotchas → \`TOOLS.md\`
- **Format**: Follows self-improvement v3.0.1 spec
`;
      toolsContent += section;
      fs.writeFileSync(toolsFile, toolsContent, 'utf8');
      console.log('[Reflection] Updated TOOLS.md with reflection section');
    }
  }
}

/**
 * 主反思函数
 */
async function reflectOnMemory() {
  console.log('[Reflection] Starting memory reflection...');
  console.log('[Reflection] EPISODIC_DIR:', EPISODIC_DIR);
  
  // 加载最近的 episodic 记录
  const episodes = loadRecentEpisodes(50);
  console.log('[Reflection] Loaded episodes:', episodes.length);
  
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
