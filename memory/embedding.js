/**
 * Doubao Embedding API 客户端（多模态版本）
 * 
 * 调用火山方舟 Doubao-embedding-vision 多模态模型
 * API 端点：/api/v3/embeddings/multimodal
 */

const https = require('https');

const CONFIG = {
  baseUrl: 'https://ark.cn-beijing.volces.com/api/v3',
  apiKey: 'fddc1778-d04c-403e-8327-ab68ec1ec9dd',
  model: 'doubao-embedding-vision-251215',
  endpoint: '/embeddings/multimodal'  // 多模态专用端点
};

/**
 * 获取文本的向量表示（多模态 API）
 * @param {string|string[]} input - 单个文本或文本数组
 * @returns {Promise<number[][]>} - 向量数组
 */
async function getEmbeddings(input) {
  const inputs = Array.isArray(input) ? input : [input];
  
  // 多模态 API 需要特殊的 input 格式
  const multimodalInput = inputs.map(text => ({
    type: 'text',
    text: text
  }));
  
  const requestBody = {
    model: CONFIG.model,
    input: multimodalInput,
    encoding_format: 'float'
  };
  
  const data = JSON.stringify(requestBody);
  
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'ark.cn-beijing.volces.com',
      path: `/api/v3${CONFIG.endpoint}`,
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${CONFIG.apiKey}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data)
      }
    };
    
    const req = https.request(options, (res) => {
      let responseBody = '';
      
      res.on('data', (chunk) => {
        responseBody += chunk;
      });
      
      res.on('end', () => {
        try {
          const response = JSON.parse(responseBody);
          if (response.data && response.data.embedding) {
            // 多模态 API 返回格式不同
            const embeddings = [response.data.embedding];
            resolve(embeddings);
          } else if (response.data && Array.isArray(response.data)) {
            // 标准格式
            const embeddings = response.data
              .sort((a, b) => a.index - b.index)
              .map(item => item.embedding);
            resolve(embeddings);
          } else {
            reject(new Error(`API error: ${JSON.stringify(response)}`));
          }
        } catch (e) {
          reject(new Error(`Parse error: ${e.message}`));
        }
      });
    });
    
    req.on('error', (e) => {
      reject(new Error(`Request error: ${e.message}`));
    });
    
    req.write(data);
    req.end();
  });
}

/**
 * 计算两个向量的余弦相似度
 * @param {number[]} vec1 - 向量 1
 * @param {number[]} vec2 - 向量 2
 * @returns {number} - 相似度 (0-1)
 */
function cosineSimilarity(vec1, vec2) {
  if (vec1.length !== vec2.length) {
    throw new Error('Vector dimensions must match');
  }
  
  let dotProduct = 0;
  let norm1 = 0;
  let norm2 = 0;
  
  for (let i = 0; i < vec1.length; i++) {
    dotProduct += vec1[i] * vec2[i];
    norm1 += vec1[i] * vec1[i];
    norm2 += vec2[i] * vec2[i];
  }
  
  return dotProduct / (Math.sqrt(norm1) * Math.sqrt(norm2));
}

module.exports = {
  getEmbeddings,
  cosineSimilarity,
  CONFIG
};
