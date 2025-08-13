// devTools.js - 开发工具的Vuex模块
// 仅在开发环境下有效

const state = () => ({
  isEnabled: import.meta.env.DEV,
  savedChanges: {
    styles: [],
    texts: [],
    layouts: []
  },
  exportedCode: null,
  pageData: {}, // 存储不同页面的修改数据
  currentPage: 'current' // 当前编辑的页面
});

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
  }
};

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
      
      // 如果是在开发环境中，可以将更改保存到本地存储
      if (import.meta.env.DEV) {
        // 保存所有页面的数据
        localStorage.setItem('dev-tools-saved-changes', JSON.stringify(changes));
        localStorage.setItem('dev-tools-page-data', JSON.stringify(state.pageData));
      }
      
      return { success: true };
    } catch (error) {
      console.error('保存更改失败:', error);
      return { success: false, error };
    }
  },
  
  // 加载保存的更改
  loadSavedChanges({ commit }) {
    try {
      // 加载当前页面的更改
      const savedChanges = localStorage.getItem('dev-tools-saved-changes');
      if (savedChanges) {
        const changes = JSON.parse(savedChanges);
        commit('setSavedChanges', changes);
      }
      
      // 加载所有页面的数据
      const pageData = localStorage.getItem('dev-tools-page-data');
      if (pageData) {
        const pages = JSON.parse(pageData);
        Object.entries(pages).forEach(([page, data]) => {
          commit('setPageData', { page, data });
        });
      }
      
      return { success: true, changes: savedChanges ? JSON.parse(savedChanges) : null };
    } catch (error) {
      console.error('加载保存的更改失败:', error);
      return { success: false, error };
    }
  },
  
  // 清除保存的更改
  clearSavedChanges({ commit }, page) {
    commit('clearSavedChanges');
    
    if (page) {
      commit('clearPageData', page);
    } else {
      commit('clearPageData');
    }
    
    localStorage.removeItem('dev-tools-saved-changes');
    
    if (page) {
      // 如果指定了页面，只清除该页面的数据
      const pageData = localStorage.getItem('dev-tools-page-data');
      if (pageData) {
        const pages = JSON.parse(pageData);
        delete pages[page];
        localStorage.setItem('dev-tools-page-data', JSON.stringify(pages));
      }
    } else {
      // 否则清除所有页面数据
      localStorage.removeItem('dev-tools-page-data');
    }
    
    return { success: true };
  },
  
  // 设置当前页面
  setCurrentPage({ commit }, page) {
    commit('setCurrentPage', page);
    return { success: true };
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

// 生成可导出的代码（CSS变量、样式修改等）
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
  
  // 处理其他页面的样式修改
  if (pageData && Object.keys(pageData).length > 0) {
    Object.entries(pageData).forEach(([page, data]) => {
      if (page !== 'current' && data.styles && data.styles.length > 0) {
        code += `/* 页面特定样式: ${page} */\n`;
        code += `/* 注意: 可能需要添加特定的选择器来限制作用域 */\n`;
        
        // 生成特定页面的CSS变量
        if (data.styles && data.styles.length > 0) {
          code += `/* 页面 ${page} 的CSS变量 */\n`;
          code += ':root {\n';
          data.styles.forEach(style => {
            code += `  ${style.name}: ${style.value}; /* ${page} */\n`;
          });
          code += '}\n\n';
        }
        
        // 生成特定页面的布局修改
        if (data.layouts && data.layouts.length > 0) {
          code += `/* 页面 ${page} 的布局修改 */\n`;
          
          // 按选择器分组
          const selectorGroups = {};
          data.layouts.forEach(layout => {
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
      }
    });
  }
  
  // 文本修改（作为CSS注释）
  if (changes.texts && changes.texts.length > 0) {
    code += '/* 文本修改 */\n';
    changes.texts.forEach(text => {
      code += `/* ${text.selector}: "${text.currentValue}" */\n`;
    });
    code += '\n';
  }
  
  return code;
};

// 生成JSON代码
const generateJsonCode = (changes, pageData) => {
  const jsonData = {
    metadata: {
      generatedAt: new Date().toISOString(),
      format: 'LAT-Lab DevTools Export'
    },
    globalChanges: {
      styles: changes.styles.map(style => ({
        name: style.name,
        value: style.value,
        originalValue: style.originalValue
      })),
      texts: changes.texts.map(text => ({
        selector: text.selector,
        value: text.currentValue,
        originalValue: text.originalValue
      })),
      layouts: changes.layouts.map(layout => ({
        selector: layout.selector,
        property: layout.property,
        value: layout.currentValue,
        originalValue: layout.originalValue
      }))
    },
    pageSpecificChanges: {}
  };
  
  // 添加页面特定的修改
  if (pageData && Object.keys(pageData).length > 0) {
    Object.entries(pageData).forEach(([page, data]) => {
      if (page !== 'current') {
        jsonData.pageSpecificChanges[page] = {
          styles: data.styles?.map(style => ({
            name: style.name,
            value: style.value,
            originalValue: style.originalValue
          })) || [],
          texts: data.texts?.map(text => ({
            selector: text.selector,
            value: text.currentValue,
            originalValue: text.originalValue
          })) || [],
          layouts: data.layouts?.map(layout => ({
            selector: layout.selector,
            property: layout.property,
            value: layout.currentValue,
            originalValue: layout.originalValue
          })) || []
        };
      }
    });
  }
  
  return JSON.stringify(jsonData, null, 2);
};

// 生成JavaScript代码
const generateJsCode = (changes, pageData) => {
  let code = '// 自动生成的样式修改\n';
  code += `// 生成时间: ${new Date().toLocaleString()}\n\n`;
  
  // CSS变量修改
  if (changes.styles && changes.styles.length > 0) {
    code += '// 应用全局CSS变量修改\n';
    code += 'function applyGlobalStyleChanges() {\n';
    changes.styles.forEach(style => {
      code += `  document.documentElement.style.setProperty('${style.name}', '${style.value}');\n`;
    });
    code += '}\n\n';
  }
  
  // 布局修改
  if (changes.layouts && changes.layouts.length > 0) {
    code += '// 应用全局布局修改\n';
    code += 'function applyGlobalLayoutChanges() {\n';
    changes.layouts.forEach(layout => {
      code += `  document.querySelectorAll('${layout.selector}').forEach(el => {\n`;
      code += `    el.style['${layout.property}'] = '${layout.currentValue}';\n`;
      code += '  });\n';
    });
    code += '}\n\n';
  }
  
  // 文本修改
  if (changes.texts && changes.texts.length > 0) {
    code += '// 应用全局文本修改\n';
    code += 'function applyGlobalTextChanges() {\n';
    changes.texts.forEach(text => {
      code += `  document.querySelectorAll('${text.selector}').forEach(el => {\n`;
      code += `    el.textContent = '${text.currentValue.replace(/'/g, "\\'")}';\n`;
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
            code += `    el.textContent = '${text.currentValue.replace(/'/g, "\\'")}';\n`;
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

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}; 