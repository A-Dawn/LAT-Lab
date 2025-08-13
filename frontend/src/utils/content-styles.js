export const contentContainerClass = 'text-left max-w-screen-md mx-auto p-4 content-container';
export const articleContentClass = 'text-left article-content';
export const markdownBodyClass = 'text-left markdown-body';

export const applyLeftAlignToContainer = (container) => {
  if (!container) return;
  
  container.classList.add('content-container');
  container.style.textAlign = 'left';
  
  const textElements = container.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, ol, ul');
  textElements.forEach(el => {
    el.style.textAlign = 'left';
  });
};

export const leftAlignDirective = {
  mounted(el) {
    applyLeftAlignToContainer(el);
  },
  updated(el) {
    applyLeftAlignToContainer(el);
  }
};

export const installContentStyles = (app) => {
  app.directive('left-align', leftAlignDirective);
  
  app.config.globalProperties.$contentStyles = {
    containerClass: contentContainerClass,
    articleClass: articleContentClass,
    markdownClass: markdownBodyClass,
    applyLeftAlign: applyLeftAlignToContainer
  };
}; 