<!--
  @component MainLayout
  @description 博客网站的主布局组件，负责组织各个区域的位置排列
  @props {Array} widgets - 插件小部件列表
  @slots main - 主内容区域插槽
  @slots left - 左侧区域插槽
  @slots right - 右侧区域插槽
  @slots top - 顶部区域插槽
  @emits {widget-refresh} - 当用户刷新小部件时触发
-->
<script setup>
import PluginWidget from './PluginWidget.vue';

const props = defineProps({
  // 插件小部件列表
  widgets: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['widget-refresh']);

/**
 * 刷新插件小部件
 * @param {String} widgetId - 小部件ID
 */
const refreshWidget = (widgetId) => {
  emit('widget-refresh', widgetId);
};
</script>

<template>
  <div class="main-layout">
    <div class="container">
      <!-- 顶部区域插件小部件 -->
      <div class="top-widgets" v-if="widgets.filter(w => w.position === 'top').length > 0">
        <plugin-widget
          v-for="widget in widgets.filter(w => w.position === 'top')"
          :key="widget.id"
          :id="widget.id"
          :name="widget.name"
          :content="widget.content"
          :html="widget.html"
          position="top"
          @refresh="refreshWidget(widget.id)"
        />
      </div>
      
      <!-- 顶部插槽 -->
      <div class="top-slot">
        <slot name="top"></slot>
      </div>
      
      <!-- 内容区域 -->
      <div class="content-layout">
        <!-- 左侧区域 -->
        <div 
          class="left-column" 
          v-if="$slots.left || widgets.filter(w => w.position === 'left').length > 0"
        >
          <!-- 左侧插件小部件 -->
          <plugin-widget
            v-for="widget in widgets.filter(w => w.position === 'left')"
            :key="widget.id"
            :id="widget.id"
            :name="widget.name"
            :content="widget.content"
            :html="widget.html"
            position="left"
            @refresh="refreshWidget(widget.id)"
          />
          
          <!-- 左侧插槽 -->
          <slot name="left"></slot>
        </div>
        
        <!-- 主内容区域 -->
        <div class="main-column">
          <slot name="main"></slot>
        </div>
        
        <!-- 右侧区域 -->
        <div 
          class="right-column" 
          v-if="$slots.right || widgets.filter(w => w.position === 'right').length > 0"
        >
          <!-- 右侧插件小部件 -->
          <plugin-widget
            v-for="widget in widgets.filter(w => w.position === 'right')"
            :key="widget.id"
            :id="widget.id"
            :name="widget.name"
            :content="widget.content"
            :html="widget.html"
            position="right"
            @refresh="refreshWidget(widget.id)"
          />
          
          <!-- 右侧插槽 -->
          <slot name="right"></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 主布局样式 */
.main-layout {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.container {
  max-width: var(--layout-max-width, 1400px);
  margin: 0 auto;
  padding: 0 var(--layout-side-padding, 20px);
  width: 100%;
}

/* 顶部区域 */
.top-widgets,
.top-slot {
  margin-bottom: 30px;
}

/* 内容区域 */
.content-layout {
  display: flex;
  gap: 30px;
}

/* 左侧区域 */
.left-column {
  width: 250px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 主内容区域 */
.main-column {
  flex: 1;
  min-width: 0; /* 防止溢出 */
}

/* 右侧区域 */
.right-column {
  width: 250px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 响应式设计 */
@media (max-width: 1100px) {
  .content-layout {
    flex-direction: column;
    gap: 20px;
  }
  
  .left-column,
  .right-column {
    width: 100%;
  }
}

/* 小屏幕设备进一步优化 */
@media (max-width: 768px) {
  .container {
    padding: 0 15px;
  }
  
  .main-layout {
    gap: 20px;
  }
}
</style> 