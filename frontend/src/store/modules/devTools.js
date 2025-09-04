// devTools.js - 开发工具的Vuex模块
// 支持API持久化存储

// 首先声明所有辅助函数，确保在使用前可用
const generateExportableCode = (changes) => {
  let code = '';
  
  // 生成CSS变量代码
  if (changes.styles && changes.styles.length > 0) {
    code += '/* CSS变量修改 */\n';
    code += ':root {\n';
    changes.styles.forEach(style => {
      code += `  ${style.name}: ${style.value};\n`;
    });
    code += '}\n\n';
  }
  
  // 生成布局修改代码
  if (changes.layouts && changes.layouts.length > 0) {
    code += '/* 布局修改 */\n';
    
    // 按选择器分组
    const selectorGroups = {};
    changes.layouts.forEach(layout => {
      if (!selectorGroups[layout.selector]) {
        selectorGroups[layout.selector] = [];
      }
      selectorGroups[layout.selector].push({
        property: layout.property,
        value: layout.currentValue
      });
    });
    
    // 生成CSS规则
    Object.keys(selectorGroups).forEach(selector => {
      code += `${selector} {\n`;
      selectorGroups[selector].forEach(prop => {
        code += `  ${prop.property}: ${prop.value};\n`;
      });
      code += '}\n\n';
    });
  }
  
  // 文本修改通常不会导出为代码，但可以提供一个注释
  if (changes.texts && changes.texts.length > 0) {
    code += '/* 文本修改 */\n';
    code += '/* 注意：文本修改需要在HTML或组件中手动更新 */\n';
    changes.texts.forEach(text => {
      code += `/* ${text.selector}: "${text.currentValue}" */\n`;
    });
    code += '\n';
  }
  
  return code;
};

// 生成CSS代码
const generateCssCode = (changes, pageData) => {
  let code = '/* 自动生成的样式修改 */\n';
  code += `/* 生成时间: ${new Date().toLocaleString()} */\n\n`;
  
  // 处理当前页面的更改
  if (changes.styles && changes.styles.length > 0) {
    code += '/* 全局CSS变量 */\n';
    code += ':root {\n';
    changes.styles.forEach(style => {
      code += `  ${style.name}: ${style.value};\n`;
    });
    code += '}\n\n';
  }
  
  // 处理布局修改
  if (changes.layouts && changes.layouts.length > 0) {
    code += '/* 全局布局修改 */\n';
    
    // 按选择器分组
    const selectorGroups = {};
    changes.layouts.forEach(layout => {
      if (!selectorGroups[layout.selector]) {
        selectorGroups[layout.selector] = [];
      }
      selectorGroups[layout.selector].push({
        property: layout.property,
        value: layout.currentValue
      });
    });
    
    // 生成CSS规则
    Object.keys(selectorGroups).forEach(selector => {
      code += `${selector} {\n`;
      selectorGroups[selector].forEach(prop => {
        code += `  ${prop.property}: ${prop.value};\n`;
      });
      code += '}\n\n';
    });
  }
  
  // 处理文本修改
  if (changes.texts && changes.texts.length > 0) {
    code += '/* 全局文本修改 */\n';
    code += '/* 注意：文本修改需要在HTML或组件中手动更新 */\n';
    changes.texts.forEach(text => {
      code += `/* ${text.selector}: "${text.currentValue}" */\n`;
    });
    code += '\n';
  }
  
  // 页面特定的修改
  if (pageData && Object.keys(pageData).length > 0) {
    Object.entries(pageData).forEach(([page, data]) => {
      if (page !== 'current' && (data.styles?.length > 0 || data.layouts?.length > 0 || data.texts?.length > 0)) {
        code += `/* 页面 ${page} 的特定修改 */\n`;
        code += `/* 注意：页面特定修改需要在相应页面中手动应用 */\n`;
        if (data.styles && data.styles.length > 0) {
          code += `/* CSS变量: ${data.styles.map(s => s.name).join(', ')} */\n`;
        }
        if (data.layouts && data.layouts.length > 0) {
          code += `/* 布局修改: ${data.layouts.map(l => l.property).join(', ')} */\n`;
        }
        if (data.texts && data.texts.length > 0) {
          code += `/* 文本修改: ${data.texts.map(t => t.selector).join(', ')} */\n`;
        }
        code += '\n';
      }
    });
  }
  
  return code;
};

// 生成JSON代码
const generateJsonCode = (changes, pageData) => {
  const exportData = {
    timestamp: new Date().toISOString(),
    changes: changes,
    pageData: pageData
  };
  
  return JSON.stringify(exportData, null, 2);
};

// 生成JavaScript代码
const generateJsCode = (changes, pageData) => {
  let code = '// 自动生成的JavaScript代码\n';
  code += `// 生成时间: ${new Date().toLocaleString()}\n\n`;
  
  // 全局样式修改函数
  if (changes.styles && changes.styles.length > 0) {
    code += 'function applyGlobalStyleChanges() {\n';
    changes.styles.forEach(style => {
      code += `  document.documentElement.style.setProperty('${style.name}', '${style.value}');\n`;
    });
    code += '}\n\n';
  }
  
  // 全局布局修改函数
  if (changes.layouts && changes.layouts.length > 0) {
    code += 'function applyGlobalLayoutChanges() {\n';
    changes.layouts.forEach(layout => {
      code += `  document.querySelectorAll('${layout.selector}').forEach(el => {\n`;
      code += `    el.style['${layout.property}'] = '${layout.currentValue}';\n`;
      code += '  });\n';
    });
    code += '}\n\n';
  }
  
  // 全局文本修改函数
  if (changes.texts && changes.texts.length > 0) {
    code += 'function applyGlobalTextChanges() {\n';
    changes.texts.forEach(text => {
      code += `  document.querySelectorAll('${text.selector}').forEach(el => {\n`;
      code += `    el.textContent = '${text.currentValue}';\n`;
      code += '  });\n';
    });
    code += '}\n\n';
  }
  
  // 页面特定的修改
  if (pageData && Object.keys(pageData).length > 0) {
    Object.entries(pageData).forEach(([page, data]) => {
      if (page !== 'current' && (data.styles?.length > 0 || data.layouts?.length > 0 || data.texts?.length > 0)) {
        code += `// 页面 ${page} 的特定修改\n`;
        code += `function apply${page.replace(/[^a-zA-Z0-9]/g, '')}Changes() {\n`;
        
        // 页面特定的CSS变量
        if (data.styles && data.styles.length > 0) {
          code += '  // CSS变量\n';
          data.styles.forEach(style => {
            code += `  document.documentElement.style.setProperty('${style.name}', '${style.value}');\n`;
          });
          code += '\n';
        }
        
        // 页面特定的布局修改
        if (data.layouts && data.layouts.length > 0) {
          code += '  // 布局修改\n';
          data.layouts.forEach(layout => {
            code += `  document.querySelectorAll('${layout.selector}').forEach(el => {\n`;
            code += `    el.style['${layout.property}'] = '${layout.currentValue}';\n`;
            code += '  });\n';
          });
          code += '\n';
        }
        
        // 页面特定的文本修改
        if (data.texts && data.texts.length > 0) {
          code += '  // 文本修改\n';
          data.texts.forEach(text => {
            code += `  document.querySelectorAll('${text.selector}').forEach(el => {\n`;
            code += `    el.textContent = '${text.currentValue}';\n`;
            code += '  });\n';
          });
        }
        
        code += '}\n\n';
      }
    });
  }
  
  // 主函数
  code += '// 应用所有修改\n';
  code += 'function applyAllChanges() {\n';
  if (changes.styles && changes.styles.length > 0) {
    code += '  applyGlobalStyleChanges();\n';
  }
  if (changes.layouts && changes.layouts.length > 0) {
    code += '  applyGlobalLayoutChanges();\n';
  }
  if (changes.texts && changes.texts.length > 0) {
    code += '  applyGlobalTextChanges();\n';
  }
  
  // 添加页面特定的函数调用
  if (pageData && Object.keys(pageData).length > 0) {
    Object.entries(pageData).forEach(([page, data]) => {
      if (page !== 'current' && (data.styles?.length > 0 || data.layouts?.length > 0 || data.texts?.length > 0)) {
        code += `  // 根据当前页面URL决定是否应用页面特定修改\n`;
        code += `  if (window.location.pathname === '${page}' || window.location.href.includes('${page}')) {\n`;
        code += `    apply${page.replace(/[^a-zA-Z0-9]/g, '')}Changes();\n`;
        code += '  }\n';
      }
    });
  }
  
  code += '}\n\n';
  code += '// 在页面加载完成后执行\n';
  code += 'document.addEventListener("DOMContentLoaded", applyAllChanges);\n';
  
  return code;
};

// 获取MIME类型
const getMimeType = (format) => {
  switch (format) {
    case 'css':
      return 'text/css';
    case 'json':
      return 'application/json';
    case 'js':
      return 'application/javascript';
    default:
      return 'text/plain';
  }
};

// 导入adminApi
import { adminApi } from '../../services/api'

// 然后声明state
const state = () => ({
  isEnabled: true, // 移除环境限制
  savedChanges: {
    styles: [],
    texts: [],
    layouts: []
  },
  exportedCode: null,
  pageData: {}, // 存储不同页面的修改数据
  currentPage: 'current' // 当前编辑的页面
});

// 声明getters
const getters = {
  isEnabled: state => state.isEnabled,
  savedChanges: state => state.savedChanges,
  exportedCode: state => state.exportedCode,
  pageData: state => state.pageData,
  currentPage: state => state.currentPage,
  
  // 获取特定页面的数据
  getPageData: (state) => (page) => {
    return state.pageData[page] || null;
  }
};

// 声明mutations
const mutations = {
  setSavedChanges(state, changes) {
    state.savedChanges = changes;
  },
  setExportedCode(state, code) {
    state.exportedCode = code;
  },
  clearSavedChanges(state) {
    state.savedChanges = {
      styles: [],
      texts: [],
      layouts: []
    };
    state.exportedCode = null;
  },
  setCurrentPage(state, page) {
    state.currentPage = page;
  },
  setPageData(state, { page, data }) {
    state.pageData = {
      ...state.pageData,
      [page]: data
    };
  },
  clearPageData(state, page) {
    if (page) {
      const newPageData = { ...state.pageData };
      delete newPageData[page];
      state.pageData = newPageData;
    } else {
      state.pageData = {};
    }
  },
  // 新增：设置页面数据的mutation
  setPageDataAll(state, pageData) {
    state.pageData = pageData || {}
  }
};

// 声明actions
const actions = {
  // 保存更改
  async saveChanges({ commit, state }, changes) {
    try {
      const page = changes.page || 'current';
      delete changes.page;
      
      // 保存当前页面的更改
      commit('setSavedChanges', changes);
      
      // 同时保存到页面数据中
      commit('setPageData', { 
        page, 
        data: {
          ...changes,
          timestamp: new Date().toISOString()
        }
      });
      
      // 生成可导出的代码
      const code = generateExportableCode(changes);
      commit('setExportedCode', code);
      
      // 准备API数据
      const apiData = {
        styles: state.savedChanges.styles,
        texts: state.savedChanges.texts,
        layouts: state.savedChanges.layouts,
        page_data: state.pageData,
        current_page: page
      }
      
      // 保存到服务器
      await adminApi.updateDevToolsConfig(apiData)
      
      return { success: true };
    } catch (error) {
      console.error('保存更改失败:', error);
      return { success: false, error };
    }
  },
  
  // 加载保存的更改
  async loadSavedChanges({ commit, state }, { force = false } = {}) {
    try {
      // 1. 从本地存储加载
      const savedData = JSON.parse(localStorage.getItem('devToolsPageData') || '{}')
      const localLastUpdated = savedData.lastUpdated || 0
      
      // 2. 如果本地有数据且不强制刷新，则检查更新
      if (Object.keys(savedData).length > 0 && !force) {
        try {
          // 检查服务器是否有更新
          const serverData = await adminApi.getDevToolsConfig()
          
          if (serverData && serverData.lastUpdated > localLastUpdated) {
            // 服务器有更新，使用服务器数据
            const dataToSave = {
              ...serverData,
              lastUpdated: serverData.lastUpdated || Date.now()
            }
            localStorage.setItem('devToolsPageData', JSON.stringify(dataToSave))
            commit('setPageDataAll', dataToSave)
            return dataToSave
          } else {
            // 使用本地数据
            commit('setPageDataAll', savedData)
            return savedData
          }
        } catch (e) {
          // 如果获取服务器数据失败，使用本地数据
          console.warn('获取服务器数据失败，使用本地缓存', e)
          commit('setPageDataAll', savedData)
          return savedData
        }
      }
      
      // 3. 从后端加载
      const response = await adminApi.getDevToolsConfig()
      
      if (response && response.data) {
        // 4. 保存到本地存储
        const dataToSave = {
          ...response.data,
          lastUpdated: response.lastUpdated || Date.now()
        }
        localStorage.setItem('devToolsPageData', JSON.stringify(dataToSave))
        
        // 5. 更新Vuex状态
        commit('setPageDataAll', dataToSave)
        
        return dataToSave
      } else {
        // 6. 如果没有数据，清空本地存储和状态
        localStorage.removeItem('devToolsPageData')
        commit('setPageDataAll', {})
        return {}
      }
    } catch (error) {
      console.error('加载保存的更改失败:', error)
      // 出错时尝试使用本地缓存
      try {
        const savedData = JSON.parse(localStorage.getItem('devToolsPageData') || '{}')
        if (Object.keys(savedData).length > 0) {
          commit('setPageDataAll', savedData)
          return savedData
        }
      } catch (e) {
        console.error('加载本地缓存失败:', e)
      }
      throw error
    }
  },
  
  // 新增：按页面保存更改
  async savePageChanges({ commit, state }, { page, changes }) {
    try {
      // 准备要保存的页面数据
      const pageData = {
        ...changes,
        lastUpdated: Date.now()
      }
      
      // 保存到Vuex状态
      commit('setPageData', { 
        page, 
        data: pageData
      });
      
      // 更新本地存储
      const savedData = JSON.parse(localStorage.getItem('devToolsPageData') || '{}')
      savedData[page] = pageData
      savedData.lastUpdated = Date.now()
      localStorage.setItem('devToolsPageData', JSON.stringify(savedData))
      
      // 准备API数据（包含所有页面的数据）
      const apiData = {
        styles: [],
        texts: [],
        layouts: [],
        page_data: { ...state.pageData, [page]: pageData },
        current_page: page,
        lastUpdated: Date.now()
      }
      
      // 保存到服务器
      await adminApi.updateDevToolsConfig(apiData)
      
      return { success: true };
    } catch (error) {
      console.error('保存页面更改失败:', error);
      return { success: false, error };
    }
  },
  
  // 新增：获取特定页面的配置
  getPageConfig({ state }, page) {
    const currentPage = page || 'current'
    return state.pageData[currentPage] || {
      styles: [],
      texts: [],
      layouts: []
    }
  },
  
  // 导出为文件
  exportToFile({ state }, { format, fileName }) {
    try {
      // 根据格式生成代码
      let code = '';
      
      switch (format) {
        case 'css':
          code = generateCssCode(state.savedChanges, state.pageData);
          break;
        case 'json':
          code = generateJsonCode(state.savedChanges, state.pageData);
          break;
        case 'js':
          code = generateJsCode(state.savedChanges, state.pageData);
          break;
        default:
          throw new Error(`不支持的格式: ${format}`);
      }
      
      // 创建Blob
      const blob = new Blob([code], { type: getMimeType(format) });
      
      // 创建下载链接
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = fileName;
      
      // 触发下载
      document.body.appendChild(link);
      link.click();
      
      // 清理
      setTimeout(() => {
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      }, 100);
      
      return { success: true };
    } catch (error) {
      console.error('导出文件失败:', error);
      return { success: false, error };
    }
  }
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}; 