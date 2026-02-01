/**
 * zhipu-mcp-tools 插件
 * 为Clawd提供智谱AI MCP服务器的各种AI能力
 */

const ZhipuMCPTools = require('./index.js');

class ZhipuMCPPlugin {
  constructor(clawd) {
    this.clawd = clawd;
    this.zhipuTools = new ZhipuMCPTools();
    this.name = 'zhipu-mcp-tools';
  }

  /**
   * 初始化插件
   */
  async initialize() {
    console.log('Initializing Zhipu MCP Tools plugin...');
    
    // 检查服务器是否可用
    try {
      const response = await fetch('http://localhost:8000/capabilities');
      const capabilities = await response.json();
      console.log(`✓ Connected to ${capabilities.name} v${capabilities.version}`);
    } catch (error) {
      console.warn('⚠ Warning: Could not connect to Zhipu MCP server:', error.message);
      console.log('Please ensure the server is running at http://localhost:8000');
    }
  }

  /**
   * 分析网页内容
   */
  async analyzeWebpage(url) {
    return await this.zhipuTools.analyzeWebpage(url);
  }

  /**
   * 分析图片内容
   */
  async analyzeImage(imagePath) {
    return await this.zhipuTools.analyzeImage(imagePath);
  }

  /**
   * 执行网络搜索
   */
  async webSearch(query, maxResults = 5) {
    return await this.zhipuTools.webSearch(query, maxResults);
  }

  /**
   * 分析代码仓库
   */
  async analyzeRepo(repoUrl) {
    return await this.zhipuTools.analyzeRepo(repoUrl);
  }

  /**
   * 生成文本
   */
  async generateText(prompt, model = 'glm-4') {
    return await this.zhipuTools.generateText(prompt, model);
  }

  /**
   * 获取插件信息
   */
  getInfo() {
    return {
      name: this.name,
      version: '1.0.0',
      description: '使用智谱AI MCP服务器提供的多种AI能力',
      features: [
        '网页分析',
        '视觉理解',
        '联网搜索',
        '仓库分析',
        '文本生成'
      ]
    };
  }
}

module.exports = ZhipuMCPPlugin;