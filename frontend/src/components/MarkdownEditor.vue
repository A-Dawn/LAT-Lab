<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { marked } from 'marked'
import hljs from '../utils/highlight.js'
import 'highlight.js/styles/github.css'
import { sanitizeMarkdown } from '../utils/sanitize';

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  height: {
    type: String,
    default: '400px'
  },
  placeholder: {
    type: String,
    default: '请输入Markdown内容...'
  },
  ariaInvalid: {
    type: Boolean,
    default: false
  },
  ariaRequired: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'save'])

const content = ref(props.modelValue)
const isPreviewMode = ref(false)
const editor = ref(null)
const previewContainer = ref(null)
const selectedFile = ref(null)
const imageUploading = ref(false)
const uploadError = ref(null)
const uploadStatus = ref('')

// 监听内容变化
watch(() => props.modelValue, (newVal) => {
  if (newVal !== content.value) {
    content.value = newVal
  }
})

// 监听内部内容变化
watch(content, (newVal) => {
  emit('update:modelValue', newVal)
})

// 初始化marked配置
onMounted(() => {
  marked.setOptions({
    renderer: new marked.Renderer(),
    highlight: function(code, lang) {
      const language = hljs.getLanguage(lang) ? lang : 'plaintext';
      return hljs.highlight(code, { language }).value;
    },
    langPrefix: 'hljs language-',
    pedantic: false,
    gfm: true,
    breaks: true,
    sanitize: false,
    smartypants: false,
    xhtml: false
  })
})

// 渲染Markdown为HTML
const renderedContent = computed(() => {
  if (!props.modelValue) return '';
  try {
    // 使用marked渲染Markdown，然后通过sanitizeMarkdown净化HTML防止XSS攻击
    return sanitizeMarkdown(marked.parse(props.modelValue));
  } catch (error) {
    console.error('Markdown渲染错误:', error);
    return `<p>渲染错误: ${error.message}</p>`;
  }
});

// 切换预览模式
const togglePreview = () => {
  isPreviewMode.value = !isPreviewMode.value
}

// 插入文本到编辑器
const insertText = (before, after = '') => {
  if (!editor.value) return
  
  const textarea = editor.value
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selectedText = content.value.substring(start, end)
  
  // 构建新文本
  const replacement = before + selectedText + after
  const newText = content.value.substring(0, start) + replacement + content.value.substring(end)
  
  // 更新内容
  content.value = newText
  
  // 重新聚焦并设置光标位置
  setTimeout(() => {
    textarea.focus()
    textarea.setSelectionRange(start + before.length, start + before.length + selectedText.length)
  }, 0)
}

// 工具栏功能
const toolbarActions = {
  heading: () => insertText('# ', '\n'),
  heading2: () => insertText('## ', '\n'),
  heading3: () => insertText('### ', '\n'),
  bold: () => insertText('**', '**'),
  italic: () => insertText('*', '*'),
  quote: () => insertText('> ', '\n'),
  code: () => insertText('```\n', '\n```'),
  link: () => insertText('[链接文字](', ')'),
  image: () => {
    // 触发文件选择
    const fileInput = document.createElement('input')
    fileInput.type = 'file'
    fileInput.accept = 'image/*'
    fileInput.onchange = handleImageUpload
    fileInput.click()
  },
  list: () => insertText('- ', '\n'),
  orderedList: () => insertText('1. ', '\n'),
  horizontalRule: () => insertText('\n---\n', '')
}

// 处理图片上传
const handleImageUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  selectedFile.value = file
  imageUploading.value = true
  uploadError.value = null
  uploadStatus.value = `上传中: ${file.name}`
  
  try {
    // 创建FormData对象
    const formData = new FormData()
    formData.append('file', file)
    
    // 发送请求到后端上传API
          const response = await fetch('/api/upload/image', {
      method: 'POST',
      body: formData,
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (!response.ok) {
      throw new Error('上传失败')
    }
    
    const data = await response.json()
    
    // 获取图片URL并插入到编辑器
            const imageUrl = `${import.meta.env.VITE_UPLOAD_URL || '/uploads'}${data.url}`
    insertText(`![${file.name}](${imageUrl})`, '')
    uploadStatus.value = `上传成功: ${file.name}`
    
    // 2秒后清除上传状态
    setTimeout(() => {
      if (uploadStatus.value.includes(file.name)) {
        uploadStatus.value = ''
      }
    }, 2000)
  } catch (error) {
    console.error('图片上传失败:', error)
    uploadError.value = '图片上传失败，请重试'
  } finally {
    imageUploading.value = false
    selectedFile.value = null
  }
}

// 保存快捷键
const handleKeyDown = (e) => {
  // Ctrl+S 或 Cmd+S
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault()
    emit('save')
  }
}

// 清除上传错误
const clearUploadError = () => {
  uploadError.value = null
}
</script>

<template>
  <div class="markdown-editor" :class="{ 'preview-active': isPreviewMode }">
    <!-- 工具栏 -->
    <div class="editor-toolbar" role="toolbar" aria-label="文本编辑工具栏">
      <button class="toolbar-btn" title="标题1" aria-label="插入一级标题" @click="toolbarActions.heading">
        <span class="icon">H1</span>
      </button>
      <button class="toolbar-btn" title="标题2" aria-label="插入二级标题" @click="toolbarActions.heading2">
        <span class="icon">H2</span>
      </button>
      <button class="toolbar-btn" title="标题3" aria-label="插入三级标题" @click="toolbarActions.heading3">
        <span class="icon">H3</span>
      </button>
      <button class="toolbar-btn" title="加粗" aria-label="加粗文本" @click="toolbarActions.bold">
        <span class="icon">B</span>
      </button>
      <button class="toolbar-btn" title="斜体" aria-label="斜体文本" @click="toolbarActions.italic">
        <span class="icon">I</span>
      </button>
      <div class="toolbar-divider" aria-hidden="true"></div>
      <button class="toolbar-btn" title="引用" aria-label="插入引用" @click="toolbarActions.quote">
        <span class="icon">"</span>
      </button>
      <button class="toolbar-btn" title="代码块" aria-label="插入代码块" @click="toolbarActions.code">
        <span class="icon">{'}'}</span>
      </button>
      <div class="toolbar-divider" aria-hidden="true"></div>
      <button class="toolbar-btn" title="链接" aria-label="插入链接" @click="toolbarActions.link">
        <span class="icon">🔗</span>
      </button>
      <button class="toolbar-btn" title="图片" aria-label="插入图片" @click="toolbarActions.image">
        <span class="icon">🖼️</span>
      </button>
      <div class="toolbar-divider" aria-hidden="true"></div>
      <button class="toolbar-btn" title="无序列表" aria-label="插入无序列表" @click="toolbarActions.list">
        <span class="icon">•</span>
      </button>
      <button class="toolbar-btn" title="有序列表" aria-label="插入有序列表" @click="toolbarActions.orderedList">
        <span class="icon">1.</span>
      </button>
      <button class="toolbar-btn" title="分隔线" aria-label="插入分隔线" @click="toolbarActions.horizontalRule">
        <span class="icon">—</span>
      </button>
      <div class="toolbar-spacer"></div>
      <button 
        class="toolbar-btn preview-btn" 
        :class="{ active: isPreviewMode }"
        @click="togglePreview"
        :aria-pressed="isPreviewMode"
        aria-label="切换预览模式"
      >
        {{ isPreviewMode ? '编辑' : '预览' }}
      </button>
    </div>
    
    <!-- 编辑区域 -->
    <div class="editor-content" :style="{ height }">
      <textarea
        v-if="!isPreviewMode"
        ref="editor"
        v-model="content"
        :placeholder="placeholder"
        class="markdown-textarea"
        @keydown="handleKeyDown"
        :aria-invalid="ariaInvalid"
        :aria-required="ariaRequired"
        aria-label="Markdown编辑器"
      ></textarea>
      
      <div 
        v-else 
        ref="previewContainer"
        class="markdown-preview"
        role="region"
        aria-label="预览内容"
        v-html="renderedContent"
      ></div>
    </div>
    
    <!-- 图片上传状态和错误 -->
    <div v-if="imageUploading || uploadStatus || uploadError" class="upload-status">
      <div v-if="imageUploading" class="upload-indicator" aria-live="polite">
        <div class="upload-spinner" aria-hidden="true"></div>
      <span>正在上传图片...</span>
      </div>
      
      <div v-else-if="uploadStatus" class="upload-success" aria-live="polite">
        <span>{{ uploadStatus }}</span>
      </div>
      
      <div v-else-if="uploadError" class="upload-error" aria-live="assertive" role="alert">
        <span>{{ uploadError }}</span>
        <button @click="clearUploadError" class="error-close" aria-label="关闭错误提示">×</button>
      </div>
    </div>
    
    <!-- Markdown编辑提示 -->
    <div class="markdown-tips" aria-hidden="true">
      <p>支持Markdown语法，可使用工具栏快捷插入格式化标记</p>
    </div>
  </div>
</template>

<style scoped>
.markdown-editor {
  border: 1px solid var(--border-color);
  border-radius: 4px;
  overflow: hidden;
  background-color: var(--input-bg);
  display: flex;
  flex-direction: column;
  transition: all 0.3s;
}

.markdown-editor:focus-within {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(76, 132, 255, 0.2);
}

.editor-toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  padding: 8px;
  border-bottom: 1px solid var(--border-color);
  background-color: var(--bg-elevated);
  position: sticky;
  top: 0;
  z-index: 5;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
  border: none;
  background: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 2px;
  color: var(--text-secondary);
  transition: all 0.2s ease;
  padding: 0 8px;
}

.toolbar-btn:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

.toolbar-btn:focus {
  outline: 2px solid var(--primary-color);
  outline-offset: 1px;
}

.toolbar-btn.active {
  background-color: var(--primary-color);
  color: white;
}

.icon {
  font-style: normal;
  font-size: 16px;
  line-height: 1;
  font-weight: bold;
}

.toolbar-divider {
  width: 1px;
  height: 24px;
  background-color: var(--border-color);
  margin: 0 8px;
}

.toolbar-spacer {
  flex: 1;
}

.preview-btn {
  width: auto;
  padding: 0 12px;
}

.editor-content {
  position: relative;
  height: 400px;
  flex: 1;
}

.markdown-textarea {
  width: 100%;
  height: 100%;
  padding: 15px;
  border: none;
  resize: none;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
  background-color: var(--input-bg);
}

.markdown-textarea:focus {
  outline: none;
}

.markdown-preview {
  width: 100%;
  height: 100%;
  padding: 15px;
  overflow-y: auto;
  line-height: 1.6;
  background-color: var(--card-bg);
  color: var(--text-primary);
}

.upload-status {
  padding: 8px 15px;
  font-size: 14px;
  display: flex;
  align-items: center;
  border-top: 1px solid var(--border-color);
}

.upload-indicator {
  display: flex;
  align-items: center;
  color: var(--primary-color);
}

.upload-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(76, 132, 255, 0.2);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  margin-right: 8px;
  animation: spin 1s linear infinite;
}

.upload-success {
  color: #67c23a;
}

.upload-error {
  color: #f56c6c;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.error-close {
  background: none;
  border: none;
  color: currentColor;
  font-size: 16px;
  cursor: pointer;
  padding: 0;
  margin-left: 8px;
}

.markdown-tips {
  font-size: 12px;
  color: var(--text-tertiary);
  padding: 5px 15px;
  border-top: 1px solid var(--border-color);
  background-color: var(--bg-elevated);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Markdown 预览样式 */
:deep(.markdown-preview h1) {
  font-size: 2em;
  margin-top: 0.67em;
  margin-bottom: 0.67em;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.3em;
  color: var(--text-primary);
}

:deep(.markdown-preview h2) {
  font-size: 1.5em;
  margin-top: 0.83em;
  margin-bottom: 0.83em;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.3em;
  color: var(--text-primary);
}

:deep(.markdown-preview h3) {
  font-size: 1.17em;
  margin-top: 1em;
  margin-bottom: 1em;
  color: var(--text-primary);
}

:deep(.markdown-preview h4) {
  font-size: 1em;
  margin-top: 1.33em;
  margin-bottom: 1.33em;
  color: var(--text-primary);
}

:deep(.markdown-preview p) {
  margin-top: 1em;
  margin-bottom: 1em;
  color: var(--text-secondary);
}

:deep(.markdown-preview strong) {
  color: var(--text-primary);
}

:deep(.markdown-preview a) {
  color: var(--primary-color);
  text-decoration: none;
}

:deep(.markdown-preview a:hover) {
  text-decoration: underline;
}

:deep(.markdown-preview img) {
  max-width: 100%;
  border-radius: 4px;
}

:deep(.markdown-preview pre) {
  background-color: var(--bg-elevated);
  border-radius: 3px;
  padding: 16px;
  overflow: auto;
}

:deep(.markdown-preview code) {
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  background-color: var(--bg-elevated);
  border-radius: 3px;
  padding: 0.2em 0.4em;
  font-size: 85%;
}

:deep(.markdown-preview pre code) {
  background-color: transparent;
  padding: 0;
}

:deep(.markdown-preview blockquote) {
  margin: 0;
  padding: 0 1em;
  color: var(--text-tertiary);
  border-left: 0.25em solid var(--border-color);
}

:deep(.markdown-preview ul), :deep(.markdown-preview ol) {
  padding-left: 2em;
  color: var(--text-secondary);
}

:deep(.markdown-preview hr) {
  height: 0.25em;
  padding: 0;
  margin: 24px 0;
  background-color: var(--border-color);
  border: 0;
}

:deep(.markdown-preview table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
}

:deep(.markdown-preview th),
:deep(.markdown-preview td) {
  border: 1px solid var(--border-color);
  padding: 8px;
  text-align: left;
}

:deep(.markdown-preview th) {
  background-color: var(--bg-elevated);
  font-weight: 600;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .editor-toolbar {
    padding: 4px;
    overflow-x: auto;
  }
  
  .toolbar-btn {
    min-width: 28px;
    height: 28px;
  }
  
  .upload-status {
    padding: 6px 10px;
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .toolbar-btn {
    min-width: 24px;
    height: 24px;
    padding: 0 4px;
  }
  
  .toolbar-divider {
    margin: 0 4px;
  }
  
  .icon {
    font-size: 14px;
  }
  
  .markdown-tips {
    display: none;
  }
}
</style> 