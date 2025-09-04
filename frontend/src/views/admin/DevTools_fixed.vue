<template>
  <div class="dev-tools-container">
    <div class="dev-tools-header">
      <h2>前端开发工具</h2>
      <div class="dev-env-badge">开发环境</div>
    </div>

    <!-- 页面选择器 -->
    <VisualPageSelector 
      @elements-loaded="updateElements"
      @page-change="handlePageChange"
      @iframe-ready="handleIframeReady"
      ref="VisualPageSelector"
    />

    <!-- 状态指示器 -->
    <StatusIndicator 
      :current-page="currentPageUrl || '当前页面'"
      :css-variables-count="cssVariables.length"
      :text-elements-count="textElements.length"
      :layout-elements-count="layoutElements.length"
      :is-loading="isLoading"
    />

    <div class="dev-tools-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        :class="['tab-button', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        {{ tab.name }}
      </button>
    </div>

    <div class="dev-tools-content">
      <div v-if="activeTab === 'styles'" class="tab-content">
        <StyleEditor 
          :cssVariables="cssVariables" 
          @update-variable="updateCssVariable"
          @refresh="refreshElements"
        />
      </div>
      
      <div v-else-if="activeTab === 'text'" class="tab-content">
        <TextEditor 
          :textElements="textElements"
          @update-text="updateTextContent"
          @refresh="refreshElements"
        />
      </div>
      
      <div v-else-if="activeTab === 'layout'" class="tab-content">
        <LayoutEditor 
          :layoutElements="layoutElements"
          @update-layout="updateLayoutProperty"
          @refresh="refreshElements"
        />
      </div>
      
      <div v-else-if="activeTab === 'history'" class="tab-content">
        <ChangeHistory 
          :changes="changeHistory"
          @revert="revertChange"
        />
      </div>
      
      <div v-else-if="activeTab === 'export'" class="tab-content">
        <FileExporter />
      </div>
    </div>

    <div class="dev-tools-actions">
      <button class="admin-btn admin-btn-secondary" @click="resetChanges" :disabled="loading">
        {{ loading ? '重置中...' : '重置所有更改' }}
      </button>
      <button class="admin-btn admin-btn-primary" @click="saveChanges" :disabled="loading">
        {{ loading ? '保存中...' : '保存更改' }}
      </button>
    </div>

    <!-- 消息提示 -->
    <div v-if="message" :class="['message', messageType]">
      {{ message }}
    </div>
  </div>
</template>
