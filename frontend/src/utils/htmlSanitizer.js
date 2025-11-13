/**
 * HTML内容安全净化工具
 * 使用 DOMPurify 库确保用户输入的HTML内容不包含恶意脚本
 */
import DOMPurify from 'dompurify'

/**
 * 安全的HTML净化配置
 * 只允许安全的标签和属性
 */
const SANITIZE_CONFIG = {
  // 允许的HTML标签
  ALLOWED_TAGS: [
    'a', 'abbr', 'b', 'blockquote', 'br', 'code', 'em', 'i', 
    'li', 'ol', 'p', 'pre', 'small', 'span', 'strong', 'sub', 
    'sup', 'u', 'ul', 'mark', 'del', 'ins', 'kbd', 'samp', 'var'
  ],
  
  // 允许的HTML属性
  ALLOWED_ATTR: [
    'href', 'title', 'target', 'rel', 'class', 'id', 'style'
  ],
  
  // 允许的URI schemes（防止javascript:等危险协议）
  ALLOWED_URI_REGEXP: /^(?:(?:(?:f|ht)tps?|mailto|tel|callto|sms|cid|xmpp):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i,
  
  // 强制所有外部链接在新标签页打开
  ADD_ATTR: ['target'],
  
  // 不允许数据URI
  ALLOW_DATA_ATTR: false,
  
  // 返回DOM而不是字符串
  RETURN_DOM: false,
  RETURN_DOM_FRAGMENT: false,
  
  // 保持安全
  SAFE_FOR_TEMPLATES: true
}

/**
 * 严格模式配置（只允许基本文本格式）
 */
const STRICT_CONFIG = {
  ALLOWED_TAGS: ['b', 'i', 'u', 'strong', 'em', 'br', 'span'],
  ALLOWED_ATTR: ['class'],
  SAFE_FOR_TEMPLATES: true
}

/**
 * 净化HTML内容
 * @param {string} html - 要净化的HTML字符串
 * @param {Object} options - 配置选项
 * @param {boolean} options.strict - 是否使用严格模式（只允许基本格式）
 * @param {Array} options.allowedTags - 自定义允许的标签
 * @param {Array} options.allowedAttr - 自定义允许的属性
 * @returns {string} 净化后的安全HTML
 */
export function sanitizeHtml(html, options = {}) {
  if (typeof html !== 'string') {
    return ''
  }
  
  // 选择配置
  let config = options.strict ? STRICT_CONFIG : SANITIZE_CONFIG
  
  // 自定义配置
  if (options.allowedTags || options.allowedAttr) {
    config = {
      ...config,
      ...(options.allowedTags && { ALLOWED_TAGS: options.allowedTags }),
      ...(options.allowedAttr && { ALLOWED_ATTR: options.allowedAttr })
    }
  }
  
  // 净化HTML
  const cleaned = DOMPurify.sanitize(html, config)
  
  // 自动为外部链接添加安全属性
  return cleaned.replace(
    /<a\s+href="(https?:\/\/[^"]+)"/gi,
    '<a href="$1" target="_blank" rel="noopener noreferrer"'
  )
}

/**
 * 检测字符串是否包含HTML标签
 * @param {string} text - 要检测的文本
 * @returns {boolean} 是否包含HTML
 */
export function containsHtml(text) {
  if (typeof text !== 'string') return false
  
  // 检测HTML标签
  const htmlPattern = /<\/?[a-z][\s\S]*>/i
  return htmlPattern.test(text)
}

/**
 * 将纯文本转换为安全的HTML
 * 保留换行符
 * @param {string} text - 纯文本
 * @returns {string} HTML格式文本
 */
export function textToHtml(text) {
  if (typeof text !== 'string') return ''
  
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
    .replace(/\n/g, '<br>')
}

/**
 * 安全地将内容应用到DOM元素
 * @param {HTMLElement} element - 目标DOM元素
 * @param {string} content - 要应用的内容
 * @param {Object} options - 配置选项
 */
export function safelyApplyContent(element, content, options = {}) {
  if (!element || typeof content !== 'string') return
  
  // 检测是否包含HTML
  if (containsHtml(content)) {
    // 包含HTML，进行净化后使用innerHTML
    element.innerHTML = sanitizeHtml(content, options)
  } else {
    // 纯文本，使用textContent
    element.textContent = content
  }
}

/**
 * 创建Vue v-html指令的安全包装
 * @param {string} html - HTML内容
 * @param {Object} options - 配置选项
 * @returns {string} 净化后的HTML
 */
export function vHtmlSafe(html, options = {}) {
  return sanitizeHtml(html, options)
}

export default {
  sanitizeHtml,
  containsHtml,
  textToHtml,
  safelyApplyContent,
  vHtmlSafe
}






