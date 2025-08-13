import DOMPurify from 'dompurify';

export const sanitizeHtml = (html, options = {}) => {
  if (!html) return '';
  
  const defaultOptions = {
    ALLOWED_TAGS: [
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr',
      'ul', 'ol', 'li', 'dl', 'dt', 'dd',
      'div', 'span', 'blockquote', 'pre', 'code',
      'strong', 'b', 'i', 'em', 'mark', 'small', 'del', 'ins', 'sub', 'sup',
      'table', 'thead', 'tbody', 'tr', 'th', 'td',
      'img', 'a'
    ],
    ALLOWED_ATTR: [
      'href', 'src', 'alt', 'title', 'class', 'id', 'style',
      'target', 'rel', 'width', 'height'
    ],
    ADD_ATTR: ['target', 'rel'],
    FORCE_HTTPS: true,
    FORBID_TAGS: ['script', 'style', 'iframe', 'frame', 'object', 'embed', 'form'],
    FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover']
  };
  
  const sanitizeOptions = { ...defaultOptions, ...options };
  return DOMPurify.sanitize(html, sanitizeOptions);
};
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