#!/usr/bin/env node

/**
 * 生产环境构建脚本
 * 用于在构建时完全移除开发工具相关代码和模块
 */

import fs from 'fs-extra'
import path from 'path'
import { execSync } from 'child_process'
import { fileURLToPath } from 'url'
import { dirname } from 'path'

// 获取当前文件的目录路径（ES Modules 替代 __dirname）
const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

// 备份目录
const BACKUP_DIR = path.join(__dirname, '.dev-tools-backup')

// 需要备份的开发工具文件和目录
const DEV_TOOLS_FILES = [
  'src/views/admin/DevTools.vue',
  'src/store/modules/devTools.js',
  'src/components/dev-tools'
]

console.log('🚀 开始生产环境构建...')

// 备份开发工具文件
console.log('📦 备份开发工具文件...')
if (!fs.existsSync(BACKUP_DIR)) {
  fs.mkdirSync(BACKUP_DIR, { recursive: true })
}

for (const file of DEV_TOOLS_FILES) {
  const srcPath = path.join(__dirname, file)
  const backupPath = path.join(BACKUP_DIR, file)
  
  if (fs.existsSync(srcPath)) {
    // 确保备份目录存在
    fs.ensureDirSync(path.dirname(backupPath))
    
    if (fs.statSync(srcPath).isDirectory()) {
      fs.copySync(srcPath, backupPath)
    } else {
      fs.copyFileSync(srcPath, backupPath)
    }
    console.log(`  ✓ 已备份: ${file}`)
  }
}

// 临时移除开发工具文件
console.log('🗑️  临时移除开发工具文件...')
for (const file of DEV_TOOLS_FILES) {
  const filePath = path.join(__dirname, file)
  if (fs.existsSync(filePath)) {
    fs.removeSync(filePath)
    console.log(`  ✓ 已移除: ${file}`)
  }
}

try {
  // 设置生产环境变量
  process.env.NODE_ENV = 'production'
  
  console.log('🏗️  执行 Vite 构建...')
  
  // 记录构建开始时间
  const buildStartTime = Date.now()
  
  // 执行构建
  const output = execSync('npm run build', { 
    encoding: 'utf8',
    stdio: 'inherit',
    env: { ...process.env, NODE_ENV: 'production' }
  })
  
  // 计算构建时间
  const buildTime = ((Date.now() - buildStartTime) / 1000).toFixed(2)
  
  console.log('✅ 构建完成!')
  console.log(`⏱️  构建用时: ${buildTime}秒`)
  
  // 分析构建产物
  console.log('📊 分析构建产物...')
  const distPath = path.join(__dirname, 'dist')
  
  if (fs.existsSync(distPath)) {
    const stats = getDirectorySize(distPath)
    console.log(`📁 构建产物大小: ${formatBytes(stats.totalSize)}`)
    console.log(`📄 文件数量: ${stats.fileCount}`)
    
    // 分析各种文件类型的大小
    const jsFiles = getFilesByExtension(distPath, '.js')
    const cssFiles = getFilesByExtension(distPath, '.css')
    const htmlFiles = getFilesByExtension(distPath, '.html')
    const assetFiles = getFilesByExtension(distPath, ['.png', '.jpg', '.jpeg', '.svg', '.ico', '.woff', '.woff2'])
    
    if (jsFiles.length > 0) {
      const jsSize = jsFiles.reduce((sum, file) => sum + fs.statSync(file).size, 0)
      console.log(`🟨 JavaScript文件: ${jsFiles.length}个, ${formatBytes(jsSize)}`)
    }
    
    if (cssFiles.length > 0) {
      const cssSize = cssFiles.reduce((sum, file) => sum + fs.statSync(file).size, 0)
      console.log(`🟦 CSS文件: ${cssFiles.length}个, ${formatBytes(cssSize)}`)
    }
    
    if (htmlFiles.length > 0) {
      const htmlSize = htmlFiles.reduce((sum, file) => sum + fs.statSync(file).size, 0)
      console.log(`🟩 HTML文件: ${htmlFiles.length}个, ${formatBytes(htmlSize)}`)
    }
    
    if (assetFiles.length > 0) {
      const assetSize = assetFiles.reduce((sum, file) => sum + fs.statSync(file).size, 0)
      console.log(`🟪 资源文件: ${assetFiles.length}个, ${formatBytes(assetSize)}`)
    }
    
    // 检查是否有大文件
    const largeFiles = getLargeFiles(distPath, 500 * 1024) // 500KB
    if (largeFiles.length > 0) {
      console.log('⚠️  发现较大的文件:')
      largeFiles.forEach(file => {
        const size = fs.statSync(file).size
        const relativePath = path.relative(distPath, file)
        console.log(`   ${relativePath}: ${formatBytes(size)}`)
      })
    }
    
    // 生成构建报告
    const report = {
      buildTime: buildTime,
      timestamp: new Date().toISOString(),
      totalSize: stats.totalSize,
      fileCount: stats.fileCount,
      files: {
        js: { count: jsFiles.length, size: jsFiles.reduce((sum, file) => sum + fs.statSync(file).size, 0) },
        css: { count: cssFiles.length, size: cssFiles.reduce((sum, file) => sum + fs.statSync(file).size, 0) },
        html: { count: htmlFiles.length, size: htmlFiles.reduce((sum, file) => sum + fs.statSync(file).size, 0) },
        assets: { count: assetFiles.length, size: assetFiles.reduce((sum, file) => sum + fs.statSync(file).size, 0) }
      },
      largeFiles: largeFiles.map(file => ({
        path: path.relative(distPath, file),
        size: fs.statSync(file).size
      }))
    }
    
    fs.writeFileSync(path.join(distPath, 'build-report.json'), JSON.stringify(report, null, 2))
    console.log('📋 构建报告已保存到 dist/build-report.json')
  }
  
} catch (error) {
  console.error('❌ 构建失败:', error.message)
  process.exit(1)
} finally {
  // 恢复开发工具文件
  console.log('🔄 恢复开发工具文件...')
  for (const file of DEV_TOOLS_FILES) {
    const srcPath = path.join(__dirname, file)
    const backupPath = path.join(BACKUP_DIR, file)
    
    if (fs.existsSync(backupPath)) {
      // 确保目标目录存在
      fs.ensureDirSync(path.dirname(srcPath))
      
      if (fs.statSync(backupPath).isDirectory()) {
        fs.copySync(backupPath, srcPath)
      } else {
        fs.copyFileSync(backupPath, srcPath)
      }
      console.log(`  ✓ 已恢复: ${file}`)
    }
  }
  
  // 清理备份文件
  console.log('🧹 已清理备份文件')
  fs.removeSync(BACKUP_DIR)
}

console.log('🎉 生产环境构建完成! 开发工具已完全移除。')
console.log('📁 构建产物位于 dist/ 目录')

// 辅助函数
function getDirectorySize(dirPath) {
  let totalSize = 0
  let fileCount = 0
  
  function scanDirectory(currentPath) {
    const items = fs.readdirSync(currentPath)
    
    for (const item of items) {
      const itemPath = path.join(currentPath, item)
      const stats = fs.statSync(itemPath)
      
      if (stats.isDirectory()) {
        scanDirectory(itemPath)
      } else {
        totalSize += stats.size
        fileCount++
      }
    }
  }
  
  scanDirectory(dirPath)
  return { totalSize, fileCount }
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

function getFilesByExtension(dirPath, extensions) {
  const files = []
  const exts = Array.isArray(extensions) ? extensions : [extensions]
  
  function scanDirectory(currentPath) {
    const items = fs.readdirSync(currentPath)
    
    for (const item of items) {
      const itemPath = path.join(currentPath, item)
      const stats = fs.statSync(itemPath)
      
      if (stats.isDirectory()) {
        scanDirectory(itemPath)
      } else {
        const ext = path.extname(itemPath).toLowerCase()
        if (exts.includes(ext)) {
          files.push(itemPath)
        }
      }
    }
  }
  
  scanDirectory(dirPath)
  return files
}

function getLargeFiles(dirPath, sizeThreshold) {
  const largeFiles = []
  
  function scanDirectory(currentPath) {
    const items = fs.readdirSync(currentPath)
    
    for (const item of items) {
      const itemPath = path.join(currentPath, item)
      const stats = fs.statSync(itemPath)
      
      if (stats.isDirectory()) {
        scanDirectory(itemPath)
      } else if (stats.size > sizeThreshold) {
        largeFiles.push(itemPath)
      }
    }
  }
  
  scanDirectory(dirPath)
  return largeFiles.sort((a, b) => fs.statSync(b).size - fs.statSync(a).size)
} 