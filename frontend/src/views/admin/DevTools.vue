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

    <!-- 元素导航器 -->
    <ElementNavigator 
      :elements="{ styles: cssVariables, texts: textElements, layouts: layoutElements }"
      @select-item="handleSelectItem"
      @highlight-item="handleHighlightItem"
      @unhighlight-item="handleUnhighlightItem"
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
import ElementNavigator from '../../components/dev-tools/ElementNavigator.vue';
import { sanitizeHtml, safelyApplyContent } from '../../utils/htmlSanitizer.js';
import toast from '../../utils/toast';

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
// 原始值快照（用于重置时恢复真正的原始值）
const originalValuesSnapshot = ref({
  cssVariables: new Map(), // key: variable.name, value: originalValue
  textElements: new Map(), // key: element.id, value: originalValue
  layoutElements: new Map() // key: `${element.selector}-${element.property}`, value: originalValue
});

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
    // 保存原始值快照（仅在首次提取或页面切换时保存）
    elements.cssVariables.forEach(variable => {
      if (!originalValuesSnapshot.value.cssVariables.has(variable.name)) {
        originalValuesSnapshot.value.cssVariables.set(variable.name, variable.originalValue);
      }
    });
    console.log('更新CSS变量:', elements.cssVariables.length, '个');
  }
  
  if (elements.textElements) {
    textElements.value = elements.textElements;
    // 保存原始值快照
    elements.textElements.forEach(element => {
      if (!originalValuesSnapshot.value.textElements.has(element.id)) {
        originalValuesSnapshot.value.textElements.set(element.id, element.originalValue);
      }
    });
    console.log('更新文本元素:', elements.textElements.length, '个');
  }
  
  if (elements.layoutElements) {
    layoutElements.value = elements.layoutElements;
    // 保存原始值快照
    elements.layoutElements.forEach(element => {
      const key = `${element.selector}-${element.property}`;
      if (!originalValuesSnapshot.value.layoutElements.has(key)) {
        originalValuesSnapshot.value.layoutElements.set(key, element.originalValue);
      }
    });
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
  
  // 清空原始值快照（新页面需要重新保存）
  originalValuesSnapshot.value.cssVariables.clear();
  originalValuesSnapshot.value.textElements.clear();
  originalValuesSnapshot.value.layoutElements.clear();
  
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

// 更新文本内容 - 使用安全的HTML应用
const updateTextContent = ({ id, value }) => {
  const element = textElements.value.find(el => el.id === id);
  if (!element) return;
  
  try {
    // 净化HTML内容
    const safeValue = sanitizeHtml(value);
    
    // 如果是当前页面，直接更新DOM
    if (!currentPageUrl.value) {
      const domElement = document.querySelector(element.selector);
      if (domElement) {
        // 使用安全的内容应用方法
        safelyApplyContent(domElement, safeValue);
      }
    } else if (iframeRef.value && iframeRef.value.contentWindow) {
      try {
        // 尝试直接访问iframe内容
        const frameDocument = iframeRef.value.contentDocument || iframeRef.value.contentWindow.document;
        const domElement = frameDocument.querySelector(element.selector);
        if (domElement) {
          // 使用安全的内容应用方法
          safelyApplyContent(domElement, safeValue);
        }
      } catch (error) {
        // 如果跨域，使用postMessage（传递净化后的值）
        iframeRef.value.contentWindow.postMessage({
          action: 'update-text',
          payload: { selector: element.selector, value: safeValue }
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
  
  // 处理特殊值
  let finalValue;
  if (value === 'none' || value === 'auto') {
    // 直接使用特殊值
    finalValue = value;
  } else if (element.property === 'max-width' && element.originalValue === 'none' && value === 0) {
    finalValue = 'none';
  } else if (element.property === 'max-width' && value >= element.max) {
    // 如果值达到最大值，可以设置为 'none' 来移除限制
    finalValue = 'none';
  } else {
    // 正常情况：数值 + 单位
    finalValue = value + element.unit;
  }
  
  try {
    // 如果是当前页面，直接更新DOM
    if (!currentPageUrl.value) {
      document.querySelectorAll(element.selector).forEach(domElement => {
        domElement.style[element.property] = finalValue;
      });
    } else if (iframeRef.value && iframeRef.value.contentWindow) {
      try {
        // 尝试直接访问iframe内容
        const frameDocument = iframeRef.value.contentDocument || iframeRef.value.contentWindow.document;
        frameDocument.querySelectorAll(element.selector).forEach(domElement => {
          domElement.style[element.property] = finalValue;
        });
      } catch (error) {
        // 如果跨域，使用postMessage
        iframeRef.value.contentWindow.postMessage({
          action: 'update-layout',
          payload: { 
            selector: element.selector, 
            property: element.property, 
            value: finalValue 
          }
        }, '*');
      }
    }
    
    // 更新状态
    element.currentValue = finalValue;
    
    // 记录变更
    addToHistory({
      type: 'layout',
      id,
      selector: element.selector,
      property: element.property,
      oldValue: element.originalValue,
      newValue: finalValue,
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
      // 回退时直接恢复旧值，不需要净化（旧值来自历史记录）
      // 如果是当前页面，直接更新DOM
      if (!currentPageUrl.value) {
        const domElement = document.querySelector(change.selector);
        if (domElement) {
          // 直接设置 innerHTML 恢复旧值
          domElement.innerHTML = change.oldValue;
        }
      } else if (iframeRef.value && iframeRef.value.contentWindow) {
        try {
          // 尝试直接访问iframe内容
          const frameDocument = iframeRef.value.contentDocument || iframeRef.value.contentWindow.document;
          const domElement = frameDocument.querySelector(change.selector);
          if (domElement) {
            // 直接设置 innerHTML 恢复旧值
            domElement.innerHTML = change.oldValue;
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

// 重置单个CSS变量（返回Promise以便等待完成）
const resetCssVariable = (variable) => {
  return new Promise((resolve) => {
    // 从快照中获取真正的原始值
    const trueOriginalValue = originalValuesSnapshot.value.cssVariables.get(variable.name) || variable.originalValue;
    
    // 更新变量对象中的 originalValue（确保同步）
    variable.originalValue = trueOriginalValue;
    
      // 如果是当前页面，直接更新DOM
      if (!currentPageUrl.value) {
      try {
        if (trueOriginalValue === null || trueOriginalValue === undefined || trueOriginalValue === '') {
          document.documentElement.style.removeProperty(variable.name);
        } else {
          document.documentElement.style.setProperty(variable.name, trueOriginalValue);
        }
        variable.value = trueOriginalValue;
        resolve();
      } catch (error) {
        console.error(`重置CSS变量 ${variable.name} 失败:`, error);
        resolve(); // 继续执行，不阻塞其他重置操作
      }
      } else if (iframeRef.value && iframeRef.value.contentWindow) {
        try {
          // 尝试直接访问iframe内容
          const frameDocument = iframeRef.value.contentDocument || iframeRef.value.contentWindow.document;
        if (trueOriginalValue === null || trueOriginalValue === undefined || trueOriginalValue === '') {
          frameDocument.documentElement.style.removeProperty(variable.name);
        } else {
          frameDocument.documentElement.style.setProperty(variable.name, trueOriginalValue);
        }
        variable.value = trueOriginalValue;
        resolve();
        } catch (error) {
          // 如果跨域，使用postMessage
          iframeRef.value.contentWindow.postMessage({
            action: 'update-style',
          payload: { name: variable.name, value: trueOriginalValue }
          }, '*');
        variable.value = trueOriginalValue;
        // 跨域场景下，等待一小段时间确保消息被处理
        setTimeout(resolve, 50);
      }
    } else {
      variable.value = trueOriginalValue;
      resolve();
    }
  });
};

// 重置单个文本元素（返回Promise以便等待完成）
const resetTextElement = (element) => {
  return new Promise((resolve) => {
    // 从快照中获取真正的原始值
    const trueOriginalValue = originalValuesSnapshot.value.textElements.get(element.id) || element.originalValue;
    
    // 更新元素对象中的 originalValue
    element.originalValue = trueOriginalValue;
    
      // 如果是当前页面，直接更新DOM
      if (!currentPageUrl.value) {
      try {
        const domElement = document.querySelector(element.selector);
        if (domElement) {
          // 使用 safelyApplyContent 方法保持一致性
          safelyApplyContent(domElement, trueOriginalValue);
          element.currentValue = trueOriginalValue;
        }
        resolve();
      } catch (error) {
        console.error(`重置文本元素 ${element.selector} 失败:`, error);
        resolve();
        }
      } else if (iframeRef.value && iframeRef.value.contentWindow) {
        try {
          // 尝试直接访问iframe内容
          const frameDocument = iframeRef.value.contentDocument || iframeRef.value.contentWindow.document;
          const domElement = frameDocument.querySelector(element.selector);
          if (domElement) {
          safelyApplyContent(domElement, trueOriginalValue);
          element.currentValue = trueOriginalValue;
          }
        resolve();
        } catch (error) {
          // 如果跨域，使用postMessage
          iframeRef.value.contentWindow.postMessage({
            action: 'update-text',
          payload: { selector: element.selector, value: trueOriginalValue }
          }, '*');
        element.currentValue = trueOriginalValue;
        // 跨域场景下，等待一小段时间确保消息被处理
        setTimeout(resolve, 50);
      }
    } else {
      element.currentValue = trueOriginalValue;
      resolve();
    }
  });
};

// 重置单个布局元素（返回Promise以便等待完成）
const resetLayoutElement = (element) => {
  return new Promise((resolve) => {
    // 从快照中获取真正的原始值
    const key = `${element.selector}-${element.property}`;
    const trueOriginalValue = originalValuesSnapshot.value.layoutElements.get(key) || element.originalValue;
    
    // 验证原始值格式
    if (trueOriginalValue === null || trueOriginalValue === undefined) {
      element.currentValue = '';
      resolve();
      return;
    }
    
    // 更新元素对象中的 originalValue
    element.originalValue = trueOriginalValue;
    
      // 如果是当前页面，直接更新DOM
      if (!currentPageUrl.value) {
      try {
        document.querySelectorAll(element.selector).forEach(domElement => {
          if (trueOriginalValue === '') {
            domElement.style[element.property] = '';
          } else {
            domElement.style[element.property] = trueOriginalValue;
          }
        });
        element.currentValue = trueOriginalValue;
        resolve();
      } catch (error) {
        console.error(`重置布局元素 ${element.selector}.${element.property} 失败:`, error);
        resolve();
      }
      } else if (iframeRef.value && iframeRef.value.contentWindow) {
        try {
          // 尝试直接访问iframe内容
          const frameDocument = iframeRef.value.contentDocument || iframeRef.value.contentWindow.document;
          frameDocument.querySelectorAll(element.selector).forEach(domElement => {
          if (trueOriginalValue === '') {
            domElement.style[element.property] = '';
          } else {
            domElement.style[element.property] = trueOriginalValue;
          }
        });
        element.currentValue = trueOriginalValue;
        resolve();
        } catch (error) {
          // 如果跨域，使用postMessage
          iframeRef.value.contentWindow.postMessage({
            action: 'update-layout',
            payload: { 
              selector: element.selector, 
              property: element.property, 
            value: trueOriginalValue 
            }
          }, '*');
        element.currentValue = trueOriginalValue;
        // 跨域场景下，等待一小段时间确保消息被处理
        setTimeout(resolve, 50);
        }
    } else {
      element.currentValue = trueOriginalValue;
      resolve();
    }
  });
};

// 重置所有更改
const resetChanges = async () => {
  try {
    // 显示加载状态
    isLoading.value = true;
    
    // 收集所有重置操作的Promise
    const resetPromises = [];
    
    // 重置CSS变量
    cssVariables.value.forEach(variable => {
      resetPromises.push(resetCssVariable(variable));
    });
    
    // 重置文本内容
    textElements.value.forEach(element => {
      resetPromises.push(resetTextElement(element));
    });
    
    // 重置布局属性
    layoutElements.value.forEach(element => {
      resetPromises.push(resetLayoutElement(element));
    });
    
    // 等待所有重置操作完成
    await Promise.all(resetPromises);
    
    // 额外等待时间，确保跨域消息被处理（特别是iframe场景）
    if (iframeRef.value && currentPageUrl.value) {
      await new Promise(resolve => setTimeout(resolve, 200));
    } else {
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    // 清空历史记录
    changeHistory.value = [];
    localStorage.removeItem('dev-tools-history');
    
    // 清除所有开发工具相关的缓存
    localStorage.removeItem('devToolsStyles');
    localStorage.removeItem('devToolsPageData');
    
    // 清除 Vuex store 中保存的数据
    try {
      const currentPage = currentPageUrl.value || 'current';
      store.commit('devTools/clearPageData', currentPage);
    } catch (storeError) {
      console.warn('清除Vuex数据失败:', storeError);
    }
    
    // 显示成功提示
    toast.success('所有更改已重置', { duration: 2000 });
    
    // 重新提取页面元素（在重置完成后）
    console.log('重置完成，重新加载页面以获取原始元素...');
    
    // 如果有iframe，重新加载iframe
    if (iframeRef.value && currentPageUrl.value) {
      const currentSrc = iframeRef.value.src;
      iframeRef.value.src = '';
      setTimeout(() => {
        iframeRef.value.src = currentSrc;
        isLoading.value = false;
      }, 100);
    } else {
      // 如果是当前页面，重新扫描元素
      console.log('正在重新扫描页面元素...');
      setTimeout(() => {
        refreshElements();
        // 提示用户：如果元素识别有问题，建议刷新页面
        console.log('提示：如果元素识别有问题，请手动刷新页面（F5）');
      }, 300);
    }
    
  } catch (error) {
    console.error('重置更改失败:', error);
    toast.error('重置更改失败，请查看控制台了解详情', { duration: 3000 });
    isLoading.value = false;
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

// 处理从导航器选择元素
const handleSelectItem = (item) => {
  console.log('选中元素:', item);
  
  // 根据元素类型切换到相应的tab并聚焦到该元素
  if (item.type === 'style') {
    activeTab.value = 'styles';
  } else if (item.type === 'text') {
    activeTab.value = 'text';
  } else if (item.type === 'layout') {
    activeTab.value = 'layout';
  }
  
  // 等待tab切换完成后滚动到元素
  setTimeout(() => {
    const elementId = item.id;
    const element = document.getElementById(elementId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      element.classList.add('highlight-flash');
      setTimeout(() => {
        element.classList.remove('highlight-flash');
      }, 2000);
    }
  }, 100);
};

// 处理高亮元素
const handleHighlightItem = (item) => {
  // 通过postMessage通知iframe高亮元素
  if (iframeRef.value && iframeRef.value.contentWindow) {
    try {
      iframeRef.value.contentWindow.postMessage({
        action: 'highlight-element',
        payload: { 
          selector: item.data.selector,
          type: item.type
        }
      }, '*');
    } catch (error) {
      console.error('发送高亮消息失败:', error);
    }
  }
};

// 取消高亮
const handleUnhighlightItem = () => {
  if (iframeRef.value && iframeRef.value.contentWindow) {
    try {
      iframeRef.value.contentWindow.postMessage({
        action: 'unhighlight-element',
        payload: {}
      }, '*');
    } catch (error) {
      console.error('发送取消高亮消息失败:', error);
    }
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
/* 高亮闪烁动画 */
@keyframes highlight-flash {
  0%, 100% {
    background-color: transparent;
    box-shadow: none;
  }
  50% {
    background-color: rgba(76, 132, 255, 0.15);
    box-shadow: 0 0 0 4px rgba(76, 132, 255, 0.2);
  }
}

.highlight-flash {
  animation: highlight-flash 1s ease-in-out 2;
  border-radius: 4px;
}
</style>

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