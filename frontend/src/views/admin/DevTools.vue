<template>
  <!-- 开发工具界面在所有环境下都可用 -->
  <div class="dev-tools-container">
    <div class="dev-tools-header">
      <h2>前端开发工具</h2>
      <div class="dev-env-badge">{{ isDevelopment ? '开发环境' : '生产环境' }}</div>
    </div>

    <!-- 页面选择器 -->
    <PageSelector 
      @elements-loaded="updateElements"
      @page-change="handlePageChange"
      @iframe-ready="handleIframeReady"
      ref="pageSelector"
    />

    <!-- 状态指示器 -->
    <StatusIndicator 
      :current-page="currentPageUrl || '当前页面'"
      :css-variables-count="cssVariables.length"
      :text-elements-count="textElements.length"
      :layout-elements-count="layoutElements.length"
      :is-loading="isLoading"
    />

    <div class="dev-tools-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        :class="['tab-button', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        {{ tab.name }}
      </button>
    </div>

    <div class="dev-tools-content">
      <div v-if="activeTab === 'styles'" class="tab-content">
        <StyleEditor 
          :cssVariables="cssVariables" 
          @update-variable="updateCssVariable"
          @refresh="refreshElements"
        />
      </div>
      
      <div v-else-if="activeTab === 'text'" class="tab-content">
        <TextEditor 
          :textElements="textElements"
          @update-text="updateTextContent"
          @refresh="refreshElements"
        />
      </div>
      
      <div v-else-if="activeTab === 'layout'" class="tab-content">
        <LayoutEditor 
          :layoutElements="layoutElements"
          @update-layout="updateLayoutProperty"
          @refresh="refreshElements"
        />
      </div>
      
      <div v-else-if="activeTab === 'history'" class="tab-content">
        <ChangeHistory 
          :changes="changeHistory"
          @revert="revertChange"
        />
      </div>
      
      <div v-else-if="activeTab === 'export'" class="tab-content">
        <FileExporter />
      </div>
    </div>

    <div class="dev-tools-actions">
      <button class="admin-btn admin-btn-secondary" @click="resetChanges">重置所有更改</button>
      <button class="admin-btn admin-btn-primary" @click="saveChanges">保存更改</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue';
import { useStore } from 'vuex';
import StyleEditor from '../../components/dev-tools/StyleEditor.vue';
import TextEditor from '../../components/dev-tools/TextEditor.vue';
import LayoutEditor from '../../components/dev-tools/LayoutEditor.vue';
import ChangeHistory from '../../components/dev-tools/ChangeHistory.vue';
import PageSelector from '../../components/dev-tools/PageSelector.vue';
import FileExporter from '../../components/dev-tools/FileExporter.vue';
import StatusIndicator from '../../components/dev-tools/StatusIndicator.vue';

const store = useStore();

// 检查环境变量
const isDev = computed(() => import.meta.env.DEV);
const isProduction = computed(() => import.meta.env.PROD);
const isDevelopment = computed(() => !isProduction.value);

// 标签页配置
const tabs = [
  { id: 'styles', name: '样式编辑' },
  { id: 'text', name: '文本编辑' },
  { id: 'layout', name: '布局调整' },
  { id: 'history', name: '修改历史' },
  { id: 'export', name: '导出文件' }
];

const activeTab = ref('styles');

// CSS变量列表
const cssVariables = ref([]);
// 文本元素列表
const textElements = ref([]);
// 布局元素列表
const layoutElements = ref([]);
// 变更历史
const changeHistory = ref([]);
// 当前编辑的页面URL
const currentPageUrl = ref('');
// iframe引用
const iframeRef = ref(null);
// 加载状态
const isLoading = ref(false);

// 初始化数据
onMounted(async () => {
  // 从本地存储加载历史更改
  loadChangeHistory();
  
  // 从 store 加载保存的数据
  try {
    const result = await store.dispatch('devTools/loadSavedChanges');
    if (result.success && result.changes) {
      console.log('已加载保存的更改:', result.changes);
    }
  } catch (error) {
    console.error('加载保存的数据失败:', error);
  }
  
  // 添加消息监听器
  window.addEventListener('message', handleWindowMessage);
});

// 组件卸载时清理
onUnmounted(() => {
  // 移除消息监听器
  window.removeEventListener('message', handleWindowMessage);
});

// 处理来自iframe的消息
const handleWindowMessage = (event) => {
  // 验证消息来源是否来自iframe
  if (iframeRef.value && event.source === iframeRef.value.contentWindow) {
    const { action, payload } = event.data;
    
    if (action === 'elements-extracted') {
      // 收到iframe中提取的元素
      updateElements(payload);
    } else if (action === 'iframe-ready') {
      console.log('Iframe已准备好:', payload.url);
    }
  }
};

// 处理iframe准备就绪
const handleIframeReady = (iframe) => {
  iframeRef.value = iframe;
  console.log('iframe已准备就绪');
};

// 更新元素列表
const updateElements = (elements) => {
  console.log('DevTools 收到元素更新:', elements);
  
  // 清除加载状态
  isLoading.value = false;
  
  if (elements.cssVariables) {
    cssVariables.value = elements.cssVariables;
    console.log('更新CSS变量:', elements.cssVariables.length, '个');
  }
  
  if (elements.textElements) {
    textElements.value = elements.textElements;
    console.log('更新文本元素:', elements.textElements.length, '个');
  }
  
  if (elements.layoutElements) {
    layoutElements.value = elements.layoutElements;
    console.log('更新布局元素:', elements.layoutElements.length, '个');
  }
};

// 处理页面变更
const handlePageChange = (pageUrl) => {
  currentPageUrl.value = pageUrl;
  
  // 设置加载状态
  isLoading.value = true;
  
  // 清空当前元素列表，显示加载中状态
  cssVariables.value = [];
  textElements.value = [];
  layoutElements.value = [];
  
  console.log('页面切换到:', pageUrl || '当前页面');
};

// 从本地存储加载变更历史
const loadChangeHistory = () => {
  try {
    const savedHistory = localStorage.getItem('dev-tools-history');
    if (savedHistory) {
      changeHistory.value = JSON.parse(savedHistory);
    }
  } catch (error) {
    console.error('加载变更历史失败:', error);
  }
};

// 更新CSS变量
const updateCssVariable = ({ name, value }) => {
  // 如果是当前页面，直接更新DOM
  if (!currentPageUrl.value) {
    document.documentElement.style.setProperty(name, value);
  } else if (iframeRef.value && iframeRef.value.contentWindow) {
    try {
      // 尝试直接访问iframe内容
      const frameDocument = iframeRef.value.contentDocument || iframeRef.value.contentWindow.document;
      frameDocument.documentElement.style.setProperty(name, value);
    } catch (error) {
      // 如果跨域，使用postMessage
      iframeRef.value.contentWindow.postMessage({
        action: 'update-style',
        payload: { name, value }
      }, '*');
    }
  }
  
  // 更新变量列表中的值
  const varIndex = cssVariables.value.findIndex(v => v.name === name);
  if (varIndex !== -1) {
    cssVariables.value[varIndex].value = value;
  }
  
  // 记录变更
  addToHistory({
    type: 'style',
    name,
    oldValue: cssVariables.value[varIndex].originalValue,
    newValue: value,
    timestamp: new Date().toISOString(),
    page: currentPageUrl.value || 'current'
  });
};

// 更新文本内容
const updateTextContent = ({ id, value }) => {
  const element = textElements.value.find(el => el.id === id);
  if (!element) return;
  
  try {
    // 如果是当前页面，直接更新DOM
    if (!currentPageUrl.value) {
      const domElement = document.querySelector(element.selector);
      if (domElement) {
        domElement.textContent = value;
      }
    } else if (iframeRef.value && iframeRef.value.contentWindow) {
      try {
        // 尝试直接访问iframe内容
        const frameDocument = iframeRef.value.contentDocument || iframeRef.value.contentWindow.document;
        const domElement = frameDocument.querySelector(element.selector);
        if (domElement) {
          domElement.textContent = value;
        }
      } catch (error) {
        // 如果跨域，使用postMessage
        iframeRef.value.contentWindow.postMessage({
          action: 'update-text',
          payload: { selector: element.selector, value }
        }, '*');
      }
    }
    
    // 更新状态
    element.currentValue = value;
    
    // 记录变更
    addToHistory({
      type: 'text',
      id,
      selector: element.selector,
      oldValue: element.originalValue,
      newValue: value,
      timestamp: new Date().toISOString(),
      page: currentPageUrl.value || 'current'
    });
  } catch (error) {
    console.error('更新文本内容失败:', error);
  }
};

// 更新布局属性
const updateLayoutProperty = ({ id, value }) => {
  const element = layoutElements.value.find(el => el.id === id);
  if (!element) return;
  
  const valueWithUnit = value + element.unit;
  
  try {
    // 如果是当前页面，直接更新DOM
    if (!currentPageUrl.value) {
      document.querySelectorAll(element.selector).forEach(domElement => {
        domElement.style[element.property] = valueWithUnit;
      });
    } else if (iframeRef.value && iframeRef.value.contentWindow) {
      try {
        // 尝试直接访问iframe内容
        const frameDocument = iframeRef.value.contentDocument || iframeRef.value.contentWindow.document;
        frameDocument.querySelectorAll(element.selector).forEach(domElement => {
          domElement.style[element.property] = valueWithUnit;
        });
      } catch (error) {
        // 如果跨域，使用postMessage
        iframeRef.value.contentWindow.postMessage({
          action: 'update-layout',
          payload: { 
            selector: element.selector, 
            property: element.property, 
            value: valueWithUnit 
          }
        }, '*');
      }
    }
    
    // 更新状态
    element.currentValue = valueWithUnit;
    
    // 记录变更
    addToHistory({
      type: 'layout',
      id,
      selector: element.selector,
      property: element.property,
      oldValue: element.originalValue,
      newValue: valueWithUnit,
      timestamp: new Date().toISOString(),
      page: currentPageUrl.value || 'current'
    });
  } catch (error) {
    console.error('更新布局属性失败:', error);
  }
};

// 添加到变更历史
const addToHistory = (change) => {
  changeHistory.value.unshift(change);
  
  // 限制历史记录长度
  if (changeHistory.value.length > 50) {
    changeHistory.value.pop();
  }
  
  // 保存到本地存储
  localStorage.setItem('dev-tools-history', JSON.stringify(changeHistory.value));
};

// 撤销变更
const revertChange = (change) => {
  try {
    if (change.type === 'style') {
      // 如果是当前页面，直接更新DOM
      if (!currentPageUrl.value) {
        document.documentElement.style.setProperty(change.name, change.oldValue);
      } else if (iframeRef.value && iframeRef.value.contentWindow) {
        try {
          // 尝试直接访问iframe内容
          const frameDocument = iframeRef.value.contentDocument || iframeRef.value.contentWindow.document;
          frameDocument.documentElement.style.setProperty(change.name, change.oldValue);
        } catch (error) {
          // 如果跨域，使用postMessage
          iframeRef.value.contentWindow.postMessage({
            action: 'update-style',
            payload: { name: change.name, value: change.oldValue }
          }, '*');
        }
      }
      
      const varIndex = cssVariables.value.findIndex(v => v.name === change.name);
      if (varIndex !== -1) {
        cssVariables.value[varIndex].value = change.oldValue;
      }
    } else if (change.type === 'text') {
      // 如果是当前页面，直接更新DOM
      if (!currentPageUrl.value) {
        const domElement = document.querySelector(change.selector);
        if (domElement) {
          domElement.textContent = change.oldValue;
        }
      } else if (iframeRef.value && iframeRef.value.contentWindow) {
        try {
          // 尝试直接访问iframe内容
          const frameDocument = iframeRef.value.contentDocument || iframeRef.value.contentWindow.document;
          const domElement = frameDocument.querySelector(change.selector);
          if (domElement) {
            domElement.textContent = change.oldValue;
          }
        } catch (error) {
          // 如果跨域，使用postMessage
          iframeRef.value.contentWindow.postMessage({
            action: 'update-text',
            payload: { selector: change.selector, value: change.oldValue }
          }, '*');
        }
      }
      
      const textIndex = textElements.value.findIndex(el => el.id === change.id);
      if (textIndex !== -1) {
        textElements.value[textIndex].currentValue = change.oldValue;
      }
    } else if (change.type === 'layout') {
      // 如果是当前页面，直接更新DOM
      if (!currentPageUrl.value) {
        document.querySelectorAll(change.selector).forEach(domElement => {
          domElement.style[change.property] = change.oldValue;
        });
      } else if (iframeRef.value && iframeRef.value.contentWindow) {
        try {
          // 尝试直接访问iframe内容
          const frameDocument = iframeRef.value.contentDocument || iframeRef.value.contentWindow.document;
          frameDocument.querySelectorAll(change.selector).forEach(domElement => {
            domElement.style[change.property] = change.oldValue;
          });
        } catch (error) {
          // 如果跨域，使用postMessage
          iframeRef.value.contentWindow.postMessage({
            action: 'update-layout',
            payload: { 
              selector: change.selector, 
              property: change.property, 
              value: change.oldValue 
            }
          }, '*');
        }
      }
      
      const layoutIndex = layoutElements.value.findIndex(el => el.id === change.id);
      if (layoutIndex !== -1) {
        layoutElements.value[layoutIndex].currentValue = change.oldValue;
      }
    }
    
    // 从历史记录中移除
    const index = changeHistory.value.findIndex(c => 
      c.timestamp === change.timestamp && 
      c.type === change.type && 
      (c.id === change.id || c.name === change.name)
    );
    
    if (index !== -1) {
      changeHistory.value.splice(index, 1);
      localStorage.setItem('dev-tools-history', JSON.stringify(changeHistory.value));
    }
  } catch (error) {
    console.error('撤销变更失败:', error);
  }
};

// 重置所有更改
const resetChanges = () => {
  try {
    // 重置CSS变量
    cssVariables.value.forEach(variable => {
      // 如果是当前页面，直接更新DOM
      if (!currentPageUrl.value) {
        document.documentElement.style.setProperty(variable.name, variable.originalValue);
      } else if (iframeRef.value && iframeRef.value.contentWindow) {
        try {
          // 尝试直接访问iframe内容
          const frameDocument = iframeRef.value.contentDocument || iframeRef.value.contentWindow.document;
          frameDocument.documentElement.style.setProperty(variable.name, variable.originalValue);
        } catch (error) {
          // 如果跨域，使用postMessage
          iframeRef.value.contentWindow.postMessage({
            action: 'update-style',
            payload: { name: variable.name, value: variable.originalValue }
          }, '*');
        }
      }
      
      variable.value = variable.originalValue;
    });
    
    // 重置文本内容
    textElements.value.forEach(element => {
      // 如果是当前页面，直接更新DOM
      if (!currentPageUrl.value) {
        const domElement = document.querySelector(element.selector);
        if (domElement) {
          domElement.textContent = element.originalValue;
        }
      } else if (iframeRef.value && iframeRef.value.contentWindow) {
        try {
          // 尝试直接访问iframe内容
          const frameDocument = iframeRef.value.contentDocument || iframeRef.value.contentWindow.document;
          const domElement = frameDocument.querySelector(element.selector);
          if (domElement) {
            domElement.textContent = element.originalValue;
          }
        } catch (error) {
          // 如果跨域，使用postMessage
          iframeRef.value.contentWindow.postMessage({
            action: 'update-text',
            payload: { selector: element.selector, value: element.originalValue }
          }, '*');
        }
      }
      
      element.currentValue = element.originalValue;
    });
    
    // 重置布局属性
    layoutElements.value.forEach(element => {
      // 如果是当前页面，直接更新DOM
      if (!currentPageUrl.value) {
        document.querySelectorAll(element.selector).forEach(domElement => {
          domElement.style[element.property] = element.originalValue;
        });
      } else if (iframeRef.value && iframeRef.value.contentWindow) {
        try {
          // 尝试直接访问iframe内容
          const frameDocument = iframeRef.value.contentDocument || iframeRef.value.contentWindow.document;
          frameDocument.querySelectorAll(element.selector).forEach(domElement => {
            domElement.style[element.property] = element.originalValue;
          });
        } catch (error) {
          // 如果跨域，使用postMessage
          iframeRef.value.contentWindow.postMessage({
            action: 'update-layout',
            payload: { 
              selector: element.selector, 
              property: element.property, 
              value: element.originalValue 
            }
          }, '*');
        }
      }
      
      element.currentValue = element.originalValue;
    });
    
    // 清空历史记录
    changeHistory.value = [];
    localStorage.removeItem('dev-tools-history');
  } catch (error) {
    console.error('重置更改失败:', error);
  }
};

// 保存更改
const saveChanges = async () => {
  try {
    // 将当前更改保存到Vuex store
    await store.dispatch('devTools/saveChanges', {
      styles: cssVariables.value.filter(v => v.value !== v.originalValue),
      texts: textElements.value.filter(t => t.currentValue !== t.originalValue),
      layouts: layoutElements.value.filter(l => l.currentValue !== l.originalValue),
      page: currentPageUrl.value || 'current'
    });
    
    toast.success('更改已保存！可以在"导出文件"标签页中导出这些更改。');
  } catch (error) {
    console.error('保存更改失败:', error);
    toast.error('保存更改失败，请查看控制台了解详情。');
  }
};

// 刷新页面元素
const refreshElements = () => {
  console.log('刷新页面元素...');
  
  // 设置加载状态
  isLoading.value = true;
  
  // 清空当前元素列表
  cssVariables.value = [];
  textElements.value = [];
  layoutElements.value = [];
  
  // 如果有iframe，向其发送刷新消息
  if (iframeRef.value && iframeRef.value.contentWindow) {
    try {
      iframeRef.value.contentWindow.postMessage({
        action: 'refresh-elements'
      }, '*');
    } catch (error) {
      console.error('发送刷新消息失败:', error);
      // 如果发送消息失败，重新加载iframe
      const currentSrc = iframeRef.value.src;
      iframeRef.value.src = '';
      setTimeout(() => {
        iframeRef.value.src = currentSrc;
      }, 100);
    }
  } else {
    // 如果没有iframe，直接在当前页面重新扫描
    setTimeout(() => {
      // 模拟扫描当前页面的元素
      scanCurrentPageElements();
    }, 500);
  }
};

// 扫描当前页面元素（当没有iframe时使用）
const scanCurrentPageElements = () => {
  try {
    // 扫描CSS变量
    const computedStyle = getComputedStyle(document.documentElement);
    const cssVars = [];
    
    // 获取所有CSS变量
    const allRules = Array.from(document.styleSheets)
      .flatMap(sheet => {
        try {
          return Array.from(sheet.cssRules || sheet.rules || []);
        } catch (e) {
          return [];
        }
      });
    
    allRules.forEach(rule => {
      if (rule.style) {
        for (let i = 0; i < rule.style.length; i++) {
          const property = rule.style[i];
          if (property.startsWith('--')) {
            const value = computedStyle.getPropertyValue(property).trim();
            if (value && !cssVars.find(v => v.name === property)) {
              cssVars.push({
                name: property,
                value: value,
                originalValue: value,
                description: `CSS变量 ${property}`
              });
            }
          }
        }
      }
    });
    
    // 扫描文本元素
    const textElems = [];
    document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, span, div, a').forEach((elem, index) => {
      if (elem.textContent.trim() && elem.children.length === 0) {
        textElems.push({
          id: `text-${index}`,
          selector: elem.tagName.toLowerCase() + (elem.className ? `.${elem.className.split(' ').join('.')}` : ''),
          description: `${elem.tagName} 文本`,
          currentValue: elem.textContent.trim(),
          originalValue: elem.textContent.trim()
        });
      }
    });
    
    // 更新元素列表
    updateElements({
      cssVariables: cssVars,
      textElements: textElems.slice(0, 20), // 限制数量
      layoutElements: [] // 当前页面布局元素扫描较复杂，暂时留空
    });
    
  } catch (error) {
    console.error('扫描当前页面元素失败:', error);
    isLoading.value = false;
  }
};
</script>

<style scoped>
.dev-tools-container {
  background-color: var(--card-bg);
  border-radius: 8px;
  box-shadow: var(--card-shadow);
  padding: 20px;
  border: 1px solid var(--border-color);
}

.dev-tools-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--border-color);
}

.dev-tools-header h2 {
  margin: 0;
  color: var(--text-primary);
}

.dev-env-badge {
  background-color: var(--success-color);
  color: white;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.dev-tools-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  overflow-x: auto;
  padding-bottom: 5px;
}

.tab-button {
  padding: 8px 16px;
  border: none;
  background-color: var(--bg-elevated);
  color: var(--text-secondary);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-button.active {
  background-color: var(--primary-color);
  color: white;
}

.tab-button:hover:not(.active) {
  background-color: var(--bg-hover);
}

.dev-tools-content {
  margin-bottom: 20px;
  min-height: 400px;
}

.tab-content {
  padding: 15px;
  background-color: var(--bg-elevated);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.dev-tools-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 15px;
  border-top: 1px solid var(--border-color);
}

@media (max-width: 768px) {
  .dev-tools-tabs {
    flex-wrap: wrap;
  }
  
  .tab-button {
    flex-grow: 1;
    text-align: center;
  }
}
</style> 