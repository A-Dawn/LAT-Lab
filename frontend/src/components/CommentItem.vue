<script setup>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'
import { commentApi } from '../services/api'

const props = defineProps({
  comment: {
    type: Object,
    required: true
  },
  articleId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['refresh-comments'])

const store = useStore()
const currentUser = computed(() => store.getters.currentUser)
const isAuthenticated = computed(() => store.getters.isAuthenticated)
const isAdmin = computed(() => currentUser.value?.role === 'admin')

const showReplyForm = ref(false)
const replyContent = ref('')
const isSubmittingReply = ref(false)
const replyError = ref('')
const showReplies = ref(false)

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 判断是否可以编辑或删除评论
const canModifyComment = computed(() => {
  if (!isAuthenticated.value) return false
  if (isAdmin.value) return true
  return currentUser.value?.id === props.comment.user_id
})

// 切换回复表单显示状态
const toggleReplyForm = () => {
  if (!isAuthenticated.value) {
    alert('请先登录后再回复评论')
    return
  }
  showReplyForm.value = !showReplyForm.value
  if (showReplyForm.value) {
    replyContent.value = ''
    replyError.value = ''
  }
}

// 切换显示回复
const toggleReplies = () => {
  showReplies.value = !showReplies.value
}

// 提交回复
const submitReply = async () => {
  if (!replyContent.value.trim()) {
    replyError.value = '回复内容不能为空'
    return
  }
  
  try {
    isSubmittingReply.value = true
    replyError.value = ''
    
    await commentApi.addComment(props.articleId, {
      content: replyContent.value,
      article_id: props.articleId,
      parent_id: props.comment.id
    })
    
    // 提交成功后刷新评论
    emit('refresh-comments')
    
    // 重置表单
    replyContent.value = ''
    showReplyForm.value = false
  } catch (e) {
    console.error('提交回复失败:', e)
    replyError.value = '提交回复失败，请稍后再试'
  } finally {
    isSubmittingReply.value = false
  }
}

// 点赞评论
const likeComment = async () => {
  if (!isAuthenticated.value) {
    alert('请先登录后再点赞')
    return
  }
  
  try {
    await commentApi.likeComment(props.comment.id)
    emit('refresh-comments')
  } catch (e) {
    console.error('点赞失败:', e)
  }
}

// 删除评论
const deleteComment = async () => {
  if (!canModifyComment.value) return
  
  if (!confirm('确定要删除这条评论吗？此操作不可恢复。')) {
    return
  }
  
  try {
    await commentApi.deleteComment(props.comment.id)
    emit('refresh-comments')
  } catch (e) {
    console.error('删除评论失败:', e)
    alert('删除评论失败，请稍后再试')
  }
}

// 审核评论
const approveComment = async () => {
  if (!isAdmin.value) return
  
  try {
    await commentApi.updateComment(props.comment.id, {
      is_approved: true
    })
    emit('refresh-comments')
  } catch (e) {
    console.error('审核评论失败:', e)
    alert('审核评论失败，请稍后再试')
  }
}
</script>

<template>
  <div class="comment-item" :class="{ 'pending': !comment.is_approved }">
    <div class="comment-avatar">
      {{ comment.user?.username?.charAt(0).toUpperCase() || '?' }}
    </div>
    
    <div class="comment-content">
      <div class="comment-header">
        <span class="comment-author">{{ comment.user?.username || '匿名用户' }}</span>
        <span v-if="!comment.is_approved" class="comment-pending">待审核</span>
        <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
      </div>
      
      <div class="comment-text">
        {{ comment.content }}
      </div>
      
      <div class="comment-actions">
        <button class="action-btn like-btn" @click="likeComment">
          <i class="icon-heart"></i>
          <span>{{ comment.likes || 0 }}</span>
        </button>
        
        <button class="action-btn reply-btn" @click="toggleReplyForm">
          <i class="icon-reply"></i>
          <span>回复</span>
        </button>
        
        <button v-if="comment.replies && comment.replies.length > 0" 
                class="action-btn show-replies-btn" 
                @click="toggleReplies">
          <i class="icon-comments"></i>
          <span>{{ showReplies ? '收起回复' : `显示${comment.replies.length}条回复` }}</span>
        </button>
        
        <button v-if="canModifyComment" class="action-btn delete-btn" @click="deleteComment">
          <i class="icon-trash"></i>
          <span>删除</span>
        </button>
        
        <button v-if="isAdmin && !comment.is_approved" 
                class="action-btn approve-btn" 
                @click="approveComment">
          <i class="icon-check"></i>
          <span>审核通过</span>
        </button>
      </div>
      
      <!-- 回复表单 -->
      <div v-if="showReplyForm" class="reply-form">
        <div v-if="replyError" class="reply-error">{{ replyError }}</div>
        <textarea 
          v-model="replyContent" 
          placeholder="写下你的回复..." 
          rows="3"
          :disabled="isSubmittingReply"
        ></textarea>
        <div class="reply-form-actions">
          <button 
            class="cancel-btn" 
            @click="toggleReplyForm"
            :disabled="isSubmittingReply"
          >
            取消
          </button>
          <button 
            class="submit-btn" 
            @click="submitReply"
            :disabled="isSubmittingReply"
          >
            {{ isSubmittingReply ? '提交中...' : '提交回复' }}
          </button>
        </div>
      </div>
      
      <!-- 嵌套回复 -->
      <div v-if="showReplies && comment.replies && comment.replies.length > 0" class="nested-replies">
        <div v-for="reply in comment.replies" :key="reply.id" class="nested-reply">
          <CommentItem 
            :comment="reply" 
            :article-id="articleId"
            @refresh-comments="emit('refresh-comments')"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.comment-item {
  display: flex;
  margin-bottom: 20px;
  position: relative;
}

.comment-item.pending {
  opacity: 0.7;
}

.comment-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #4c84ff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 12px;
  flex-shrink: 0;
}

.comment-content {
  flex: 1;
}

.comment-header {
  margin-bottom: 5px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.comment-author {
  font-weight: bold;
  margin-right: 10px;
}

.comment-pending {
  font-size: 0.8rem;
  color: #e6a23c;
  background-color: #fdf6ec;
  padding: 2px 6px;
  border-radius: 4px;
  margin-right: 10px;
}

.comment-date {
  font-size: 0.8rem;
  color: #909399;
}

.comment-text {
  margin-bottom: 10px;
  line-height: 1.5;
  word-break: break-word;
}

.comment-actions {
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
}

.action-btn {
  background: none;
  border: none;
  font-size: 0.9rem;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  padding: 0;
}

.action-btn:hover {
  color: #4c84ff;
}

.like-btn:hover {
  color: #f56c6c;
}

.delete-btn:hover {
  color: #f56c6c;
}

.approve-btn:hover {
  color: #67c23a;
}

.reply-form {
  margin-top: 10px;
  margin-bottom: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 10px;
}

.reply-error {
  color: #f56c6c;
  font-size: 0.9rem;
  margin-bottom: 8px;
}

.reply-form textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  resize: vertical;
  margin-bottom: 10px;
}

.reply-form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.cancel-btn, .submit-btn {
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
}

.cancel-btn {
  background-color: #f5f7fa;
  border: 1px solid #dcdfe6;
  color: #606266;
}

.submit-btn {
  background-color: #4c84ff;
  border: none;
  color: white;
}

.submit-btn:hover {
  background-color: #3a70e3;
}

.submit-btn:disabled, .cancel-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.nested-replies {
  margin-top: 15px;
  margin-left: 20px;
  border-left: 2px solid #ebeef5;
  padding-left: 15px;
}

.nested-reply {
  margin-bottom: 15px;
}

.nested-reply:last-child {
  margin-bottom: 0;
}
</style> 