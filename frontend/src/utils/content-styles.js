/**
 * 内容区域样式工具
 * 提供可以应用于内容区域的CSS类和工具函数
 */

// 内容容器基本样式类
export const contentContainerClass = 'text-left max-w-screen-md mx-auto p-4 content-container';

// 文章内容样式类
export const articleContentClass = 'text-left article-content';

// Markdown内容样式类
export const markdownBodyClass = 'text-left markdown-body';

/**
 * 将容器内的文本样式设置为左对齐
 * @param {HTMLElement} container - 要应用样式的容器元素
 */
export const applyLeftAlignToContainer = (container) => {
  if (!container) return;
  
  // 添加内容容器类
  container.classList.add('content-container');
  
  // 设置文本对齐
  container.style.textAlign = 'left';
  
  // 为容器内的所有文本元素设置左对齐
  const textElements = container.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, ol, ul');
  textElements.forEach(el => {
    el.style.textAlign = 'left';
  });
};

/**
 * Vue指令：v-left-align
 * 用法：<div v-left-align>内容</div>
 */
export const leftAlignDirective = {
  mounted(el) {
    applyLeftAlignToContainer(el);
  },
  updated(el) {
    applyLeftAlignToContainer(el);
  }
};

/**
 * 安装插件到Vue应用
 * @param {Vue} app - Vue应用实例
 */
export const installContentStyles = (app) => {
  // 注册指令
  app.directive('left-align', leftAlignDirective);
  
  // 提供全局属性
  app.config.globalProperties.$contentStyles = {
    containerClass: contentContainerClass,
    articleClass: articleContentClass,
    markdownClass: markdownBodyClass,
    applyLeftAlign: applyLeftAlignToContainer
  };
}; 