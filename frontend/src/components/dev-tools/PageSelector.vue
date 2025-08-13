<template>
  <div class="page-selector">
    <div class="selector-header">
      <h3>选择页面</h3>
      <p class="selector-description">
        选择要编辑的页面，可以修改不同页面的样式、文本和布局。
      </p>
    </div>
    
    <div class="selector-content">
      <div class="selector-group">
        <label for="page-select">页面</label>
        <select 
          id="page-select" 
          v-model="selectedPageUrl" 
          @change="handlePageChange"
          class="page-dropdown"
        >
          <option value="">当前页面</option>
          <option 
            v-for="page in availablePages" 
            :key="page.url" 
            :value="page.url"
            :title="page.description"
          >
            {{ page.name }}
          </option>
        </select>
        <div v-if="selectedPageUrl" class="page-description">
          {{ getSelectedPageDescription() }}
        </div>
        
        <!-- 动态内容控制开关 -->
        <div class="dynamic-content-control">
          <label class="toggle-label">
            <input 
              type="checkbox" 
              v-model="includeDynamicContent"
              @change="handleDynamicContentToggle"
            />
            <span class="toggle-text">包含动态内容</span>
            <span class="toggle-description">
              开启后将包含从API获取的动态内容，关闭则只显示静态模板元素
            </span>
          </label>
        </div>
        
        <!-- 调试信息 -->
        <div class="debug-info" v-if="isDev">
          <small>
            页面总数: {{ availablePages.length }} | 
            当前选择: {{ selectedPageUrl || '当前页面' }}
          </small>
        </div>
      </div>
      
      <div v-if="selectedPageUrl" class="preview-container">
        <div class="preview-header">
          <h4>页面预览</h4>
          <div class="preview-controls">
            <button 
              class="preview-button" 
              @click="refreshPreview"
              title="刷新预览"
            >
              🔄
            </button>
            <button 
              class="preview-button" 
              @click="togglePreviewSize"
              title="切换预览大小"
            >
              {{ isFullPreview ? '🔍' : '📱' }}
            </button>
          </div>
        </div>
        
        <div 
          class="iframe-container"
          :class="{ 'full-size': isFullPreview }"
        >
          <iframe 
            ref="previewFrame" 
            :src="iframeUrl" 
            class="preview-frame"
            @load="onFrameLoad"
            allow="clipboard-write"
          ></iframe>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps({
  currentPage: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['page-change', 'elements-loaded', 'iframe-ready']);

const router = useRouter();
const previewFrame = ref(null);
const selectedPageUrl = ref('');
const isFullPreview = ref(false);
const frameLoaded = ref(false);

// 控制是否包含动态内容
const includeDynamicContent = ref(false);

// 开发环境判断
const isDev = computed(() => {
  return process.env.NODE_ENV === 'development';
});

// 计算iframe的URL，添加开发工具标记参数
const iframeUrl = computed(() => {
  if (!selectedPageUrl.value) return '';
  
  const url = new URL(selectedPageUrl.value, window.location.origin);
  // 添加参数以便目标页面识别是从开发工具中加载的
  url.searchParams.append('devtools', 'true');
  return url.toString();
});

// 可用页面列表 - 扩展了更多页面
const availablePages = [
  { name: '首页', url: '/', description: '博客首页，包含文章列表和导航' },
  { name: '文章详情页', url: '/article/1', description: '单篇文章的详细页面' },
  { name: '创建文章', url: '/article/new', description: '创建新文章的编辑器' },
  { name: '编辑文章', url: '/article/1/edit', description: '编辑已有文章的页面' },
  { name: '用户资料', url: '/profile', description: '用户个人资料页面' },
  { name: '登录页面', url: '/login', description: '用户登录界面' },
  { name: '注册页面', url: '/register', description: '用户注册界面' },
  { name: '管理员首页', url: '/admin', description: '管理员仪表板' },
  { name: '管理员 - 文章管理', url: '/admin/articles', description: '管理所有文章' },
  { name: '管理员 - 用户管理', url: '/admin/users', description: '管理系统用户' },
  { name: '管理员 - 分类管理', url: '/admin/categories', description: '管理文章分类' },
  { name: '管理员 - 标签管理', url: '/admin/tags', description: '管理文章标签' },
  { name: '管理员 - 评论管理', url: '/admin/comments', description: '管理用户评论' },
  { name: '管理员 - 插件管理', url: '/admin/plugins', description: '管理系统插件' },
  { name: '插件市场', url: '/admin/plugins/marketplace', description: '浏览和安装插件' },
];

// 切换预览大小
const togglePreviewSize = () => {
  isFullPreview.value = !isFullPreview.value;
};

// 刷新预览
const refreshPreview = () => {
  if (previewFrame.value) {
    previewFrame.value.src = iframeUrl.value;
  }
};

// 处理动态内容切换
const handleDynamicContentToggle = () => {
  console.log('动态内容设置已更改:', includeDynamicContent.value);
  
  // 重新提取元素
  if (!selectedPageUrl.value) {
    // 当前页面
    setTimeout(loadCurrentPageElements, 100);
  } else if (previewFrame.value && frameLoaded.value) {
    // iframe页面
    setTimeout(() => {
      if (previewFrame.value && previewFrame.value.contentWindow) {
        previewFrame.value.contentWindow.postMessage({
          action: 'refresh-elements',
          payload: { includeDynamicContent: includeDynamicContent.value }
        }, '*');
      }
    }, 100);
  }
};

// 获取选中页面的描述
const getSelectedPageDescription = () => {
  const selectedPage = availablePages.find(page => page.url === selectedPageUrl.value);
  return selectedPage ? selectedPage.description : '';
};

// 处理页面变更
const handlePageChange = () => {
  frameLoaded.value = false;
  emit('page-change', selectedPageUrl.value);
  
  // 如果选择了当前页面，则重新加载当前页面的元素
  if (!selectedPageUrl.value) {
    setTimeout(() => {
      loadCurrentPageElements();
    }, 100);
  } else {
    // 如果选择了其他页面，等待iframe加载完成
    // onFrameLoad 函数会自动处理元素提取
    console.log('等待iframe加载页面:', selectedPageUrl.value);
  }
};

// 预览框架加载完成
const onFrameLoad = async () => {
  frameLoaded.value = true;
  
  // 将iframe引用传递给父组件
  emit('iframe-ready', previewFrame.value);
  
  if (selectedPageUrl.value && previewFrame.value) {
    // 等待一小段时间确保iframe完全加载
    await nextTick();
    setTimeout(() => {
    try {
      // 获取iframe中的文档
      const frameDocument = previewFrame.value.contentDocument || previewFrame.value.contentWindow.document;
      
      // 注入通信脚本到iframe中
      injectCommunicationScript(frameDocument);
      
      // 提取可编辑元素
      const extractedElements = extractEditableElements(frameDocument);
        
        console.log('成功提取页面元素:', extractedElements);
      
      // 发送提取的元素到父组件
      emit('elements-loaded', extractedElements);
    } catch (error) {
      console.error('无法访问iframe内容，可能是由于跨域限制:', error);
      // 尝试使用postMessage进行跨域通信
      setupCrossDomainCommunication();
    }
    }, 200); // 增加延时确保内容完全加载
  }
};

// 注入通信脚本到iframe中
const injectCommunicationScript = (doc) => {
  try {
    const script = doc.createElement('script');
    script.textContent = `
      // 开发工具通信脚本
      console.log('开发工具通信脚本已注入');
      
      // 自动提取元素并发送给父窗口
      function autoExtractElements() {
        console.log('自动提取页面元素...');
        const elements = extractElementsForDevTools();
        console.log('提取到的元素:', elements);
        window.parent.postMessage({
          action: 'elements-extracted',
          payload: elements
        }, '*');
      }
      
      // 等待DOM完全加载后提取元素
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', autoExtractElements);
      } else {
        // DOM已经加载完成，立即提取
        setTimeout(autoExtractElements, 100);
      }
      
      window.addEventListener('message', function(event) {
        // 验证消息来源
        console.log('iframe收到消息:', event.data);
        
        const { action, payload } = event.data;
        
        if (action === 'extract-elements') {
          // 提取元素并回传
          console.log('收到提取元素请求');
          // 接收动态内容设置
          window.includeDynamicContent = payload?.includeDynamicContent || false;
          autoExtractElements();
        } else if (action === 'refresh-elements') {
          // 刷新元素
          console.log('收到刷新元素请求');
          // 接收动态内容设置
          window.includeDynamicContent = payload?.includeDynamicContent || false;
          setTimeout(autoExtractElements, 200);
        } else if (action === 'update-style') {
          // 更新CSS变量
          document.documentElement.style.setProperty(payload.name, payload.value);
        } else if (action === 'update-text') {
          // 更新文本内容
          const element = document.querySelector(payload.selector);
          if (element) element.textContent = payload.value;
        } else if (action === 'update-layout') {
          // 更新布局属性
          const elements = document.querySelectorAll(payload.selector);
          elements.forEach(el => {
            el.style[payload.property] = payload.value;
          });
        }
      });
      
      // 检查元素是否为动态内容
      function isDynamicElement(element) {
        // 检查元素或其父元素是否包含动态内容标识
        let current = element;
        
        // 向上遍历DOM树检查是否在动态内容区域
        while (current && current !== document.body) {
          // 检查Vue相关的动态绑定属性
          if (current.hasAttribute && (
            current.hasAttribute('v-for') ||
            current.hasAttribute('v-if') ||
            current.hasAttribute('v-show') ||
            current.hasAttribute(':key') ||
            current.hasAttribute('data-dynamic') ||
            current.className.includes('dynamic-content') ||
            current.className.includes('article-content') ||
            current.className.includes('user-content') ||
            current.className.includes('api-data') ||
            current.className.includes('generated-content')
          )) {
            return true;
          }
          
          // 检查常见的动态内容容器
          if (current.matches && current.matches(
            '.article-list, .post-list, .comment-list, ' +
            '.user-list, .tag-list, .category-list, ' +
            '.search-results, .feed-content, .dynamic-section, ' +
            '.api-content, .loaded-content, .fetched-data, ' +
            '[data-v-], .v-enter, .v-leave, .transition-group'
          )) {
            return true;
          }
          
          // 检查文本内容是否看起来像动态数据
          if (current.textContent) {
            const text = current.textContent.trim();
            // 排除看起来像时间戳、用户名、API数据的内容
            if (
              /^\d{4}-\d{2}-\d{2}/.test(text) || // 日期格式
              /^\d+\s*(分钟|小时|天|月|年)前$/.test(text) || // 相对时间
              /^@\w+$/.test(text) || // 用户名格式
              /^\d+\s*(阅读|点赞|评论|浏览)$/.test(text) || // 统计数据
              text.includes('加载中') || text.includes('loading') ||
              text.includes('暂无数据') || text.includes('no data')
            ) {
              return true;
            }
          }
          
          current = current.parentElement;
        }
        
        return false;
      }
      
      // 检查文本是否为静态模板内容
      function isStaticTemplateText(text) {
        if (!text || !text.trim()) return false;
        
        const trimmedText = text.trim();
        
        // 排除明显的动态内容
        const dynamicPatterns = [
          /^\d{4}-\d{2}-\d{2}/, // 日期
          /^\d+\s*(分钟|小时|天|月|年)前$/, // 相对时间
          /^@\w+$/, // 用户名
          /^\d+\s*(阅读|点赞|评论|浏览|播放)/, // 统计数据
          /^(加载中|loading|暂无数据|no data)/i,
          /\$\{.*\}/, // 模板变量
          /{{.*}}/, // Vue模板语法
          /\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}/, // 完整时间戳
        ];
        
        if (dynamicPatterns.some(pattern => pattern.test(trimmedText))) {
          return false;
        }
        
        // 静态模板文本的特征
        const staticPatterns = [
          /^(首页|关于我们?|联系我们?|登录|注册|设置|管理|博客|文章|分类|标签|档案)$/i,
          /^(导航|菜单|按钮|链接|标题|副标题|页面|网站)$/i,
          /^(提交|保存|取消|删除|编辑|修改|添加|创建|新建|发布)$/i,
          /^(用户名|密码|邮箱|电话|地址|姓名|昵称)$/i,
          /^(搜索|筛选|排序|分页|返回|下一页|上一页|更多|查看)$/i,
          /^(个人资料|用户中心|仪表板|控制面板|设置中心)$/i,
          /^(版权|隐私|条款|免责|声明|政策|协议)$/i,
          /^(主题|样式|布局|配色|字体|大小)$/i
        ];
        
        // 短文本更可能是静态的
        if (trimmedText.length <= 20) {
          return staticPatterns.some(pattern => pattern.test(trimmedText)) || 
                 /^[a-zA-Z\u4e00-\u9fa5\s]{1,20}$/.test(trimmedText);
        }
        
        // 长文本需要更严格的匹配
        return staticPatterns.some(pattern => pattern.test(trimmedText));
      }
      
      // 提取可编辑元素的函数
      function extractElementsForDevTools() {
        // CSS变量
        const rootStyles = getComputedStyle(document.documentElement);
        const cssVariables = [];
        
        // 主题颜色变量 - 扩展更多变量
        const themeVars = [
          '--primary-color', '--secondary-color', '--accent-color',
          '--bg-primary', '--bg-secondary', '--bg-elevated', '--bg-hover',
          '--text-primary', '--text-secondary', '--text-tertiary',
          '--border-color', '--card-bg', '--card-shadow',
          '--input-bg', '--input-border', '--input-text',
          '--success-color', '--warning-color', '--error-color', '--info-color',
          '--header-bg', '--footer-bg', '--sidebar-bg', '--modal-bg',
          '--button-primary', '--button-secondary', '--button-hover',
          '--link-color', '--link-hover', '--code-bg', '--code-text'
        ];
        
        themeVars.forEach(varName => {
          const value = rootStyles.getPropertyValue(varName).trim();
          if (value) {
            cssVariables.push({
              name: varName,
              value: value,
              originalValue: value,
              type: varName.includes('color') ? 'color' : 'text'
            });
          }
        });
        
        // 文本元素
        const textElements = [];
        
        // 查找标题元素
        document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach((el, index) => {
          const shouldInclude = window.includeDynamicContent || 
                               (!isDynamicElement(el) && 
                                (isStaticTemplateText(el.textContent) || el.textContent.length < 50));
          
          if (el.textContent.trim() && 
              !el.querySelector('input, textarea, select') && 
              shouldInclude) {
            textElements.push({
              id: \`heading-\${index}\`,
              selector: getUniqueSelector(el),
              description: \`标题: \${el.textContent.substring(0, 30)}\${el.textContent.length > 30 ? '...' : ''}\`,
              currentValue: el.textContent,
              originalValue: el.textContent
            });
          }
        });
        
        // 查找段落元素
        document.querySelectorAll('p').forEach((el, index) => {
          const shouldInclude = window.includeDynamicContent || 
                               (!isDynamicElement(el) && 
                                (isStaticTemplateText(el.textContent) || el.textContent.length < 100));
          
          if (el.textContent.trim() && 
              !el.querySelector('input, textarea, select') && 
              shouldInclude) {
            textElements.push({
              id: \`paragraph-\${index}\`,
              selector: getUniqueSelector(el),
              description: \`段落: \${el.textContent.substring(0, 30)}\${el.textContent.length > 30 ? '...' : ''}\`,
              currentValue: el.textContent,
              originalValue: el.textContent
            });
          }
        });
        
        // 查找按钮文本
        document.querySelectorAll('button, .btn, .button, .admin-btn').forEach((el, index) => {
          const shouldInclude = window.includeDynamicContent || 
                               (!isDynamicElement(el) && isStaticTemplateText(el.textContent));
          
          if (el.textContent.trim() && 
              !el.querySelector('input, textarea, select') && 
              shouldInclude) {
            textElements.push({
              id: \`button-\${index}\`,
              selector: getUniqueSelector(el),
              description: \`按钮: \${el.textContent.substring(0, 30)}\${el.textContent.length > 30 ? '...' : ''}\`,
              currentValue: el.textContent,
              originalValue: el.textContent
            });
          }
        });
        
        // 查找标签文本
        document.querySelectorAll('label').forEach((el, index) => {
          const shouldInclude = window.includeDynamicContent || 
                               (!isDynamicElement(el) && isStaticTemplateText(el.textContent));
          
          if (el.textContent.trim() && 
              !el.querySelector('input, textarea, select') && 
              shouldInclude) {
            textElements.push({
              id: \`label-\${index}\`,
              selector: getUniqueSelector(el),
              description: \`标签: \${el.textContent.substring(0, 30)}\${el.textContent.length > 30 ? '...' : ''}\`,
              currentValue: el.textContent,
              originalValue: el.textContent
            });
          }
        });
        
        // 查找导航链接
        document.querySelectorAll('nav a, .nav a, .navbar a').forEach((el, index) => {
          const shouldInclude = window.includeDynamicContent || 
                               (!isDynamicElement(el) && isStaticTemplateText(el.textContent));
          
          if (el.textContent.trim() && shouldInclude) {
            textElements.push({
              id: \`nav-link-\${index}\`,
              selector: getUniqueSelector(el),
              description: \`导航链接: \${el.textContent.substring(0, 30)}\${el.textContent.length > 30 ? '...' : ''}\`,
              currentValue: el.textContent,
              originalValue: el.textContent
            });
          }
        });
        
        // 查找标题类元素
        document.querySelectorAll('.title, .heading, .card-title, .section-title').forEach((el, index) => {
          const shouldInclude = window.includeDynamicContent || 
                               (!isDynamicElement(el) && 
                                (isStaticTemplateText(el.textContent) || el.textContent.length < 50));
          
          if (el.textContent.trim() && 
              !el.querySelector('input, textarea, select') && 
              shouldInclude) {
            textElements.push({
              id: \`title-\${index}\`,
              selector: getUniqueSelector(el),
              description: \`标题元素: \${el.textContent.substring(0, 30)}\${el.textContent.length > 30 ? '...' : ''}\`,
              currentValue: el.textContent,
              originalValue: el.textContent
            });
          }
        });
        
        // 查找表单相关文本
        document.querySelectorAll('legend, .form-label, .form-text, .help-text').forEach((el, index) => {
          const shouldInclude = window.includeDynamicContent || 
                               (!isDynamicElement(el) && isStaticTemplateText(el.textContent));
          
          if (el.textContent.trim() && shouldInclude) {
            textElements.push({
              id: \`form-text-\${index}\`,
              selector: getUniqueSelector(el),
              description: \`表单文本: \${el.textContent.substring(0, 30)}\${el.textContent.length > 30 ? '...' : ''}\`,
              currentValue: el.textContent,
              originalValue: el.textContent
            });
          }
        });
        
        // 布局元素
        const layoutElements = [];
        
        // 查找容器元素 - 扩展更多选择器，但排除动态内容区域
        document.querySelectorAll('.container, .card, .section, .panel, main, section, article, aside, .content, .wrapper, .box, .widget, .admin-card, .form-group, .input-group, header, footer, nav, .sidebar').forEach((el, index) => {
          // 跳过动态内容容器（除非用户选择包含动态内容）
          if (!window.includeDynamicContent && isDynamicElement(el)) {
            return;
          }
          
          const styles = getComputedStyle(el);
          
          // 宽度
          layoutElements.push({
            id: \`width-\${index}\`,
            selector: getUniqueSelector(el),
            property: 'width',
            description: \`宽度: \${getUniqueSelector(el).split(' ')[0]}\`,
            currentValue: styles.width,
            originalValue: styles.width,
            unit: 'px',
            min: 100,
            max: 2000
          });
          
          // 内边距
          layoutElements.push({
            id: \`padding-\${index}\`,
            selector: getUniqueSelector(el),
            property: 'padding',
            description: \`内边距: \${getUniqueSelector(el).split(' ')[0]}\`,
            currentValue: styles.padding,
            originalValue: styles.padding,
            unit: 'px',
            min: 0,
            max: 100
          });
          
          // 外边距
          layoutElements.push({
            id: \`margin-\${index}\`,
            selector: getUniqueSelector(el),
            property: 'margin',
            description: \`外边距: \${getUniqueSelector(el).split(' ')[0]}\`,
            currentValue: styles.margin,
            originalValue: styles.margin,
            unit: 'px',
            min: 0,
            max: 100
          });
          
          // 边框圆角
          layoutElements.push({
            id: \`border-radius-\${index}\`,
            selector: getUniqueSelector(el),
            property: 'border-radius',
            description: \`边框圆角: \${getUniqueSelector(el).split(' ')[0]}\`,
            currentValue: styles.borderRadius,
            originalValue: styles.borderRadius,
            unit: 'px',
            min: 0,
            max: 50
          });
        });
        
        return {
          cssVariables,
          textElements,
          layoutElements
        };
      }
      
      // 生成元素的唯一选择器
      function getUniqueSelector(el) {
        // 简单实现，实际项目中可能需要更复杂的算法
        if (el.id) {
          return \`#\${el.id}\`;
        }
        
        if (el.className) {
          const classes = el.className.split(' ')
            .filter(c => c && !c.startsWith('v-'))
            .join('.');
          if (classes) {
            return \`.\${classes}\`;
          }
        }
        
        // 如果没有ID或类，使用标签名和索引
        const siblings = Array.from(el.parentNode.children);
        const tagName = el.tagName.toLowerCase();
        const index = siblings.filter(sibling => sibling.tagName.toLowerCase() === tagName)
          .indexOf(el) + 1;
        
        return \`\${tagName}:nth-of-type(\${index})\`;
      }
      
      // 通知父窗口iframe已准备好
      window.parent.postMessage({
        action: 'iframe-ready',
        payload: { url: window.location.href }
      }, '*');
    `;
    doc.head.appendChild(script);
  } catch (error) {
    console.error('注入通信脚本失败:', error);
  }
};

// 设置跨域通信
const setupCrossDomainCommunication = () => {
  console.log('设置跨域通信...');
  
  // 监听来自iframe的消息
  window.addEventListener('message', handleIframeMessage);
  
  // 等待iframe完全加载后再发送消息
  setTimeout(() => {
  if (previewFrame.value && previewFrame.value.contentWindow) {
      console.log('请求iframe中的元素...');
    previewFrame.value.contentWindow.postMessage({
        action: 'extract-elements',
        payload: { includeDynamicContent: includeDynamicContent.value }
    }, '*');
  }
  }, 500);
};

// 处理来自iframe的消息
const handleIframeMessage = (event) => {
  // 验证消息来源
  if (!previewFrame.value || event.source !== previewFrame.value.contentWindow) return;
  
  const { action, payload } = event.data;
  
  console.log('收到iframe消息:', action, payload);
  
  if (action === 'elements-extracted') {
    // 收到iframe中提取的元素
    console.log('收到提取的元素:', payload);
    emit('elements-loaded', payload);
  } else if (action === 'iframe-ready') {
    console.log('Iframe已准备好:', payload.url);
  }
};

// 从当前页面提取可编辑元素
const loadCurrentPageElements = () => {
  // 设置动态内容标志
  window.includeDynamicContent = includeDynamicContent.value;
  
  const extractedElements = extractEditableElements(document);
  emit('elements-loaded', extractedElements);
};

// 提取可编辑元素
const extractEditableElements = (doc) => {
  // CSS变量
  const rootStyles = getComputedStyle(doc.documentElement);
  const cssVariables = [];
  
  // 主题颜色变量 - 扩展更多变量
  const themeVars = [
    '--primary-color', '--secondary-color', '--accent-color',
    '--bg-primary', '--bg-secondary', '--bg-elevated', '--bg-hover',
    '--text-primary', '--text-secondary', '--text-tertiary',
    '--border-color', '--card-bg', '--card-shadow',
    '--input-bg', '--input-border', '--input-text',
    '--success-color', '--warning-color', '--error-color', '--info-color',
    '--header-bg', '--footer-bg', '--sidebar-bg', '--modal-bg',
    '--button-primary', '--button-secondary', '--button-hover',
    '--link-color', '--link-hover', '--code-bg', '--code-text'
  ];
  
  themeVars.forEach(varName => {
    const value = rootStyles.getPropertyValue(varName).trim();
    if (value) {
      cssVariables.push({
        name: varName,
        value: value,
        originalValue: value,
        type: varName.includes('color') ? 'color' : 'text'
      });
    }
  });
  
  // 文本元素
  const textElements = [];
  
  // 查找标题元素
  doc.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach((el, index) => {
    if (el.textContent.trim() && !el.querySelector('input, textarea, select')) {
      textElements.push({
        id: `heading-${index}`,
        selector: getUniqueSelector(el),
        description: `标题: ${el.textContent.substring(0, 30)}${el.textContent.length > 30 ? '...' : ''}`,
        currentValue: el.textContent,
        originalValue: el.textContent
      });
    }
  });
  
  // 查找段落元素
  doc.querySelectorAll('p').forEach((el, index) => {
    if (el.textContent.trim() && !el.querySelector('input, textarea, select')) {
      textElements.push({
        id: `paragraph-${index}`,
        selector: getUniqueSelector(el),
        description: `段落: ${el.textContent.substring(0, 30)}${el.textContent.length > 30 ? '...' : ''}`,
        currentValue: el.textContent,
        originalValue: el.textContent
      });
    }
  });
  
  // 查找按钮文本
  doc.querySelectorAll('button, .btn, .button, .admin-btn').forEach((el, index) => {
    if (el.textContent.trim() && !el.querySelector('input, textarea, select')) {
      textElements.push({
        id: `button-${index}`,
        selector: getUniqueSelector(el),
        description: `按钮: ${el.textContent.substring(0, 30)}${el.textContent.length > 30 ? '...' : ''}`,
        currentValue: el.textContent,
        originalValue: el.textContent
      });
    }
  });
  
  // 查找标签文本
  doc.querySelectorAll('label').forEach((el, index) => {
    if (el.textContent.trim() && !el.querySelector('input, textarea, select')) {
      textElements.push({
        id: `label-${index}`,
        selector: getUniqueSelector(el),
        description: `标签: ${el.textContent.substring(0, 30)}${el.textContent.length > 30 ? '...' : ''}`,
        currentValue: el.textContent,
        originalValue: el.textContent
      });
    }
  });
  
  // 查找导航链接
  doc.querySelectorAll('nav a, .nav a, .navbar a').forEach((el, index) => {
    if (el.textContent.trim()) {
      textElements.push({
        id: `nav-link-${index}`,
        selector: getUniqueSelector(el),
        description: `导航链接: ${el.textContent.substring(0, 30)}${el.textContent.length > 30 ? '...' : ''}`,
        currentValue: el.textContent,
        originalValue: el.textContent
      });
    }
  });
  
  // 查找标题类元素
  doc.querySelectorAll('.title, .heading, .card-title, .section-title').forEach((el, index) => {
    if (el.textContent.trim() && !el.querySelector('input, textarea, select')) {
      textElements.push({
        id: `title-${index}`,
        selector: getUniqueSelector(el),
        description: `标题元素: ${el.textContent.substring(0, 30)}${el.textContent.length > 30 ? '...' : ''}`,
        currentValue: el.textContent,
        originalValue: el.textContent
      });
    }
  });
  
  // 查找表单相关文本
  doc.querySelectorAll('legend, .form-label, .form-text, .help-text').forEach((el, index) => {
    if (el.textContent.trim()) {
      textElements.push({
        id: `form-text-${index}`,
        selector: getUniqueSelector(el),
        description: `表单文本: ${el.textContent.substring(0, 30)}${el.textContent.length > 30 ? '...' : ''}`,
        currentValue: el.textContent,
        originalValue: el.textContent
      });
    }
  });
  
  // 布局元素
  const layoutElements = [];
  
  // 查找容器元素 - 扩展更多选择器
  doc.querySelectorAll('.container, .card, .section, .panel, main, section, article, aside, .content, .wrapper, .box, .widget, .admin-card, .form-group, .input-group, header, footer, nav, .sidebar').forEach((el, index) => {
    const styles = getComputedStyle(el);
    
    // 宽度
    layoutElements.push({
      id: `width-${index}`,
      selector: getUniqueSelector(el),
      property: 'width',
      description: `宽度: ${getUniqueSelector(el).split(' ')[0]}`,
      currentValue: styles.width,
      originalValue: styles.width,
      unit: 'px',
      min: 100,
      max: 2000
    });
    
    // 内边距
    layoutElements.push({
      id: `padding-${index}`,
      selector: getUniqueSelector(el),
      property: 'padding',
      description: `内边距: ${getUniqueSelector(el).split(' ')[0]}`,
      currentValue: styles.padding,
      originalValue: styles.padding,
      unit: 'px',
      min: 0,
      max: 100
    });
    
    // 外边距
    layoutElements.push({
      id: `margin-${index}`,
      selector: getUniqueSelector(el),
      property: 'margin',
      description: `外边距: ${getUniqueSelector(el).split(' ')[0]}`,
      currentValue: styles.margin,
      originalValue: styles.margin,
      unit: 'px',
      min: 0,
      max: 100
    });
    
    // 边框圆角
    layoutElements.push({
      id: `border-radius-${index}`,
      selector: getUniqueSelector(el),
      property: 'border-radius',
      description: `边框圆角: ${getUniqueSelector(el).split(' ')[0]}`,
      currentValue: styles.borderRadius,
      originalValue: styles.borderRadius,
      unit: 'px',
      min: 0,
      max: 50
    });
  });
  
  return {
    cssVariables,
    textElements,
    layoutElements
  };
};

// 生成元素的唯一选择器
const getUniqueSelector = (el) => {
  // 简单实现，实际项目中可能需要更复杂的算法
  if (el.id) {
    return `#${el.id}`;
  }
  
  if (el.className) {
    const classes = el.className.split(' ')
      .filter(c => c && !c.startsWith('v-'))
      .join('.');
    if (classes) {
      return `.${classes}`;
    }
  }
  
  // 如果没有ID或类，使用标签名和索引
  const siblings = Array.from(el.parentNode.children);
  const tagName = el.tagName.toLowerCase();
  const index = siblings.filter(sibling => sibling.tagName.toLowerCase() === tagName)
    .indexOf(el) + 1;
  
  return `${tagName}:nth-of-type(${index})`;
};

// 清理函数
const cleanup = () => {
  // 移除消息监听器
  window.removeEventListener('message', handleIframeMessage);
};

// 初始化
onMounted(() => {
  console.log('PageSelector mounted, 可用页面数量:', availablePages.length);
  console.log('可用页面列表:', availablePages.map(p => ({ name: p.name, url: p.url })));
  
  // 默认加载当前页面的元素
  loadCurrentPageElements();
  
  // 添加消息监听器
  window.addEventListener('message', handleIframeMessage);
});

// 组件卸载时清理
onUnmounted(() => {
  cleanup();
});

// 暴露iframe引用给父组件
defineExpose({
  previewFrame
});
</script>

<style scoped>
.page-selector {
  margin-bottom: 20px;
}

.selector-header {
  margin-bottom: 15px;
}

.selector-header h3 {
  margin: 0 0 10px 0;
  color: var(--text-primary);
}

.selector-description {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin: 0;
}

.selector-group {
  margin-bottom: 15px;
}

.selector-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: var(--text-secondary);
}

.page-dropdown {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--input-bg);
  color: var(--text-primary);
  font-size: 1rem;
}

.page-dropdown:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(76, 132, 255, 0.2);
}

.page-description {
  margin-top: 8px;
  padding: 8px 12px;
  background-color: var(--bg-hover);
  border-radius: 4px;
  font-size: 0.85rem;
  color: var(--text-secondary);
  border-left: 3px solid var(--primary-color);
}

.debug-info {
  margin-top: 8px;
  padding: 4px 8px;
  background-color: #f0f0f0;
  border-radius: 3px;
  font-size: 0.75rem;
  color: #666;
  border: 1px dashed #ccc;
}

.dynamic-content-control {
  margin-top: 15px;
  padding: 12px;
  background-color: var(--bg-elevated);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.toggle-label {
  display: flex;
  flex-direction: column;
  gap: 8px;
  cursor: pointer;
}

.toggle-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  margin-right: 8px;
  accent-color: var(--primary-color);
}

.toggle-text {
  font-weight: 500;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  font-size: 0.9rem;
}

.toggle-description {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-left: 24px;
  line-height: 1.4;
}

.preview-container {
  margin-top: 20px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  overflow: hidden;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.preview-header h4 {
  margin: 0;
  font-size: 1rem;
  color: var(--text-primary);
}

.preview-controls {
  display: flex;
  gap: 10px;
}

.preview-button {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
  transition: all 0.2s;
}

.preview-button:hover {
  background-color: var(--bg-hover);
}

.iframe-container {
  height: 300px;
  transition: height 0.3s ease;
}

.iframe-container.full-size {
  height: 600px;
}

.preview-frame {
  width: 100%;
  height: 100%;
  border: none;
  background-color: white;
}

@media (max-width: 768px) {
  .iframe-container.full-size {
    height: 400px;
  }
}
</style> 