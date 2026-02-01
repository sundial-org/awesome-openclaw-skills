const axios = require('axios');
const fs = require('fs');

class ZhipuMCPTools {
  constructor() {
    this.serverUrl = 'http://localhost:8000';
  }

  /**
   * 分析网页内容
   * @param {string} url - 要分析的网页URL
   * @returns {Promise<Object>} 分析结果
   */
  async analyzeWebpage(url) {
    try {
      const response = await axios.post(`${this.serverUrl}/execute`, {
        tool: 'web_reader',
        params: {
          url: url,
          summary: true
        }
      });
      
      if (response.data.success) {
        return {
          success: true,
          result: response.data.result,
          toolUsed: response.data.tool_used
        };
      } else {
        return {
          success: false,
          error: response.data.error
        };
      }
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * 分析图片内容
   * @param {string} imagePath - 图片路径或URL
   * @returns {Promise<Object>} 分析结果
   */
  async analyzeImage(imagePath) {
    try {
      // 如果是本地文件，则读取并转换为base64
      let imageData;
      if (imagePath.startsWith('http')) {
        // 如果是URL，则假定已由上游处理为base64
        imageData = imagePath;
      } else {
        // 如果是本地文件，则读取并转换为base64
        const imageBuffer = fs.readFileSync(imagePath);
        imageData = imageBuffer.toString('base64');
      }

      const response = await axios.post(`${this.serverUrl}/execute`, {
        tool: 'vision_analyzer',
        params: {
          image: imageData,
          prompt: '请详细描述这张图片的内容'
        }
      });

      if (response.data.success) {
        return {
          success: true,
          result: response.data.result,
          toolUsed: response.data.tool_used
        };
      } else {
        return {
          success: false,
          error: response.data.error
        };
      }
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * 联网搜索
   * @param {string} query - 搜索查询
   * @param {number} maxResults - 最大结果数
   * @returns {Promise<Object>} 搜索结果
   */
  async webSearch(query, maxResults = 5) {
    try {
      const response = await axios.post(`${this.serverUrl}/execute`, {
        tool: 'web_search',
        params: {
          query: query,
          max_results: maxResults
        }
      });

      if (response.data.success) {
        return {
          success: true,
          result: response.data.result,
          toolUsed: response.data.tool_used
        };
      } else {
        return {
          success: false,
          error: response.data.error
        };
      }
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * 分析代码仓库
   * @param {string} repoUrl - 仓库URL
   * @returns {Promise<Object>} 分析结果
   */
  async analyzeRepo(repoUrl) {
    try {
      const response = await axios.post(`${this.serverUrl}/execute`, {
        tool: 'repo_analyzer',
        params: {
          repo_url: repoUrl,
          analyze_readme: true,
          analyze_structure: true
        }
      });

      if (response.data.success) {
        return {
          success: true,
          result: response.data.result,
          toolUsed: response.data.tool_used
        };
      } else {
        return {
          success: false,
          error: response.data.error
        };
      }
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * 生成文本
   * @param {string} prompt - 生成提示
   * @param {string} model - 使用的模型
   * @returns {Promise<Object>} 生成结果
   */
  async generateText(prompt, model = 'glm-4') {
    try {
      const response = await axios.post(`${this.serverUrl}/execute`, {
        tool: 'text_generator',
        params: {
          prompt: prompt,
          model: model
        }
      });

      if (response.data.success) {
        return {
          success: true,
          result: response.data.result,
          toolUsed: response.data.tool_used
        };
      } else {
        return {
          success: false,
          error: response.data.error
        };
      }
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }
}

module.exports = ZhipuMCPTools;