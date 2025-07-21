# 前端安全措施说明

## XSS防护措施

本项目已实施以下XSS（跨站脚本攻击）防护措施：

### 1. HTML内容净化

所有使用`v-html`指令渲染的内容都经过DOMPurify库的净化处理，防止恶意脚本注入：

- `sanitizeHtml`: 基本HTML净化，适用于大多数内容
- `strictSanitizeHtml`: 更严格的HTML净化，仅允许最基本标签，适用于用户评论等高风险内容
- `sanitizeMarkdown`: 针对Markdown渲染内容的特定净化，允许更多的标签以支持Markdown格式

### 2. URL参数验证

所有从URL获取的参数都经过严格验证：

- 数字参数: 使用`validateNumericParam`验证
- 字符串参数: 使用`validateStringParam`验证并限制长度
- 页码参数: 使用`validatePageParam`验证
- 重定向URL: 仅允许站内相对路径

### 3. 内容安全策略

应考虑在生产环境中添加合适的内容安全策略(CSP)头，进一步限制可执行的脚本来源。

## 开发者注意事项

### 使用v-html的安全指南

1. **永远不要直接使用v-html渲染不可信内容**
   ```vue
   <!-- 错误示例 -->
   <div v-html="userContent"></div>
   
   <!-- 正确示例 -->
   <div v-html="sanitizeHtml(userContent)"></div>
   ```

2. **根据内容类型选择合适的净化函数**
   - 用户评论等高风险内容: `strictSanitizeHtml`
   - Markdown渲染内容: `sanitizeMarkdown`
   - 一般HTML内容: `sanitizeHtml`

3. **导入方式**
   ```javascript
   import { sanitizeHtml, strictSanitizeHtml, sanitizeMarkdown } from '../utils/sanitize';
   ```

### URL参数处理

1. **始终验证URL参数**
   ```javascript
   // 错误示例
   const categoryId = route.query.category;
   
   // 正确示例
   const categoryId = validateNumericParam(route.query.category);
   ```

2. **对重定向URL进行验证**
   ```javascript
   // 确保只接受内部相对路径
   if (redirectUrl.startsWith('/') && !redirectUrl.includes('://')) {
     router.push(redirectUrl);
   }
   ```

## 安全测试

在实施任何新功能时，建议进行以下安全测试：

1. XSS测试：尝试在用户输入字段中注入脚本
2. URL参数测试：尝试通过URL参数注入恶意内容
3. 文件上传测试：确保上传文件被正确验证和处理

## 漏洞报告

如果发现任何安全漏洞，请联系安全团队：security@luminarc.tech 