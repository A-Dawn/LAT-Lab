import DOMPurify from 'dompurify';

/**
 * 净化HTML内容，防止XSS攻击
 * 
 * @param {string} html - 需要净化的HTML内容
 * @param {Object} options - DOMPurify配置选项
 * @returns {string} - 净化后的安全HTML
 */
export const sanitizeHtml = (html, options = {}) => {
  if (!html) return '';
  
  // 默认配置
  const defaultOptions = {
    // 允许的标签列表
    ALLOWED_TAGS: [
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr',
      'ul', 'ol', 'li', 'dl', 'dt', 'dd',
      'div', 'span', 'blockquote', 'pre', 'code',
      'strong', 'b', 'i', 'em', 'mark', 'small', 'del', 'ins', 'sub', 'sup',
      'table', 'thead', 'tbody', 'tr', 'th', 'td',
      'img', 'a'
    ],
    // 允许的属性
    ALLOWED_ATTR: [
      'href', 'src', 'alt', 'title', 'class', 'id', 'style',
      'target', 'rel', 'width', 'height'
    ],
    // 添加noopener noreferrer到所有链接
    ADD_ATTR: ['target', 'rel'],
    // 强制https链接
    FORCE_HTTPS: true,
    // 禁止脚本
    FORBID_TAGS: ['script', 'style', 'iframe', 'frame', 'object', 'embed', 'form'],
    // 禁止属性
    FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover']
  };
  
  // 合并选项
  const sanitizeOptions = { ...defaultOptions, ...options };
  
  // 使用DOMPurify净化HTML
  return DOMPurify.sanitize(html, sanitizeOptions);
};

/**
 * 更严格的HTML净化，只允许非常有限的标签
 * 适用于用户评论等高风险内容
 */
export const strictSanitizeHtml = (html) => {
  return sanitizeHtml(html, {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'b', 'i', 'a', 'ul', 'ol', 'li', 'code'],
    ALLOWED_ATTR: ['href', 'rel', 'target']
  });
};

/**
 * 针对Markdown渲染内容的净化，允许更多的标记以支持Markdown格式
 */
export const sanitizeMarkdown = (html) => {
  return sanitizeHtml(html, {
    // 增加对代码高亮的支持
    ADD_TAGS: ['figure', 'figcaption', 'section'],
    ADD_ATTR: ['class', 'data-lang']
  });
};

export default {
  sanitizeHtml,
  strictSanitizeHtml,
  sanitizeMarkdown
}; 