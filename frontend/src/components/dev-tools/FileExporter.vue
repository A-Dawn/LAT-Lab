<template>
  <div class="file-exporter">
    <div class="exporter-header">
      <h3>导出修改</h3>
      <p class="exporter-description">
        将修改导出为文件，以便在生产环境中应用。
      </p>
    </div>
    
    <div class="exporter-content">
      <div class="format-options">
        <div class="option-group">
          <label>导出格式</label>
          <div class="format-buttons">
            <button 
              v-for="format in exportFormats" 
              :key="format.id"
              :class="['format-button', { active: selectedFormat === format.id }]"
              @click="selectedFormat = format.id"
            >
              {{ format.name }}
            </button>
          </div>
        </div>
        
        <div class="option-group">
          <label>文件名</label>
          <input 
            type="text" 
            v-model="fileName" 
            class="file-name-input"
            :placeholder="`修改导出_${currentDate}`"
          />
        </div>
      </div>
      
      <div class="preview-area">
        <div class="preview-header">
          <h4>预览</h4>
          <div class="preview-actions">
            <button 
              class="copy-button" 
              @click="copyToClipboard"
              title="复制到剪贴板"
            >
              复制
            </button>
          </div>
        </div>
        
        <pre class="code-preview"><code>{{ generatedCode }}</code></pre>
      </div>
      
      <div class="exporter-actions">
        <button 
          class="admin-btn admin-btn-primary"
          @click="downloadFile"
          :disabled="!hasChanges"
        >
          下载文件
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useStore } from 'vuex';

const store = useStore();

const exportFormats = [
  { id: 'css', name: 'CSS', extension: 'css' },
  { id: 'json', name: 'JSON', extension: 'json' },
  { id: 'js', name: 'JavaScript', extension: 'js' }
];

const selectedFormat = ref('css');

const fileName = ref('');

const currentDate = computed(() => {
  const now = new Date();
  return `${now.getFullYear()}${(now.getMonth() + 1).toString().padStart(2, '0')}${now.getDate().toString().padStart(2, '0')}`;
});

const savedChanges = computed(() => store.getters['devTools/savedChanges'] || {
  styles: [],
  texts: [],
  layouts: []
});

const hasChanges = computed(() => {
  return savedChanges.value.styles.length > 0 || 
         savedChanges.value.texts.length > 0 || 
         savedChanges.value.layouts.length > 0;
});

const generatedCode = computed(() => {
  if (!hasChanges.value) {
    return '// 没有可导出的修改';
  }
  
  switch (selectedFormat.value) {
    case 'css':
      return generateCssCode(savedChanges.value);
    case 'json':
      return generateJsonCode(savedChanges.value);
    case 'js':
      return generateJsCode(savedChanges.value);
    default:
      return '// 未知格式';
  }
});

const generateCssCode = (changes) => {
  let code = '/* 自动生成的样式修改 */\n';
  code += `/* 生成时间: ${new Date().toLocaleString()} */\n\n`;
  
  if (changes.styles && changes.styles.length > 0) {
    code += ':root {\n';
    changes.styles.forEach(style => {
      code += `  ${style.name}: ${style.value};\n`;
    });
    code += '}\n\n';
  }
  
  if (changes.layouts && changes.layouts.length > 0) {
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
  
  // 文本修改（作为CSS注释）
  if (changes.texts && changes.texts.length > 0) {
    code += '/* 文本修改 */\n';
    changes.texts.forEach(text => {
      code += `/* ${text.selector}: "${text.currentValue}" */\n`;
    });
  }
  
  return code;
};

// 生成JSON代码
const generateJsonCode = (changes) => {
  const jsonData = {
    metadata: {
      generatedAt: new Date().toISOString(),
      format: 'LAT-Lab DevTools Export'
    },
    changes: {
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
    }
  };
  
  return JSON.stringify(jsonData, null, 2);
};

// 生成JavaScript代码
const generateJsCode = (changes) => {
  let code = '// 自动生成的样式修改\n';
  code += `// 生成时间: ${new Date().toLocaleString()}\n\n`;
  
  // CSS变量修改
  if (changes.styles && changes.styles.length > 0) {
    code += '// 应用CSS变量修改\n';
    code += 'function applyStyleChanges() {\n';
    changes.styles.forEach(style => {
      code += `  document.documentElement.style.setProperty('${style.name}', '${style.value}');\n`;
    });
    code += '}\n\n';
  }
  
  // 布局修改
  if (changes.layouts && changes.layouts.length > 0) {
    code += '// 应用布局修改\n';
    code += 'function applyLayoutChanges() {\n';
    changes.layouts.forEach(layout => {
      code += `  document.querySelectorAll('${layout.selector}').forEach(el => {\n`;
      code += `    el.style['${layout.property}'] = '${layout.currentValue}';\n`;
      code += '  });\n';
    });
    code += '}\n\n';
  }
  
  // 文本修改
  if (changes.texts && changes.texts.length > 0) {
    code += '// 应用文本修改\n';
    code += 'function applyTextChanges() {\n';
    changes.texts.forEach(text => {
      code += `  document.querySelectorAll('${text.selector}').forEach(el => {\n`;
      code += `    el.textContent = '${text.currentValue.replace(/'/g, "\\'")}';\n`;
      code += '  });\n';
    });
    code += '}\n\n';
  }
  
  // 主函数
  code += '// 应用所有修改\n';
  code += 'function applyAllChanges() {\n';
  if (changes.styles && changes.styles.length > 0) {
    code += '  applyStyleChanges();\n';
  }
  if (changes.layouts && changes.layouts.length > 0) {
    code += '  applyLayoutChanges();\n';
  }
  if (changes.texts && changes.texts.length > 0) {
    code += '  applyTextChanges();\n';
  }
  code += '}\n\n';
  code += '// 在页面加载完成后执行\n';
  code += 'document.addEventListener("DOMContentLoaded", applyAllChanges);\n';
  
  return code;
};

// 复制到剪贴板
const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(generatedCode.value);
    toast.success('已复制到剪贴板');
  } catch (err) {
    console.error('复制失败:', err);
    toast.error('复制失败，请手动复制');
  }
};

// 修改downloadFile方法，使用Vuex的导出功能
const downloadFile = () => {
  // 获取文件扩展名
  const format = exportFormats.find(f => f.id === selectedFormat.value);
  const extension = format ? format.extension : 'txt';
  
  // 生成文件名
  const name = fileName.value || `修改导出_${currentDate.value}`;
  const fullFileName = `${name}.${extension}`;
  
  // 使用Vuex的导出功能
  store.dispatch('devTools/exportToFile', {
    format: selectedFormat.value,
    fileName: fullFileName
  }).then(result => {
    if (!result.success) {
      toast.error('导出失败，请查看控制台了解详情。');
    }
  }).catch(error => {
    console.error('导出失败:', error);
    toast.error('导出失败，请查看控制台了解详情。');
  });
};

// 获取MIME类型
const getMimeType = (extension) => {
  switch (extension) {
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
</script>

<style scoped>
.file-exporter {
  margin-bottom: 20px;
}

.exporter-header {
  margin-bottom: 15px;
}

.exporter-header h3 {
  margin: 0 0 10px 0;
  color: var(--text-primary);
}

.exporter-description {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin: 0;
}

.exporter-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.format-options {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.option-group {
  flex: 1;
  min-width: 200px;
}

.option-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-secondary);
}

.format-buttons {
  display: flex;
  gap: 10px;
}

.format-button {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  background-color: var(--bg-elevated);
  color: var(--text-secondary);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.format-button.active {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.format-button:hover:not(.active) {
  background-color: var(--bg-hover);
}

.file-name-input {
  width: 100%;
  padding: 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--input-bg);
  color: var(--text-primary);
}

.file-name-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(76, 132, 255, 0.2);
}

.preview-area {
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

.copy-button {
  padding: 4px 10px;
  background-color: var(--bg-elevated);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s;
}

.copy-button:hover {
  background-color: var(--bg-hover);
}

.code-preview {
  padding: 15px;
  margin: 0;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  max-height: 300px;
  overflow: auto;
  font-family: monospace;
  font-size: 0.9rem;
  line-height: 1.5;
  white-space: pre-wrap;
}

.exporter-actions {
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .format-options {
    flex-direction: column;
  }
}
</style> 