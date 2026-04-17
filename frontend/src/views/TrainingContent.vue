<template>
  <div class="training-content-layout">
    <!-- 左侧侧边栏 -->
    <aside 
      class="sidebar" 
      :class="{ collapsed: sidebarCollapsed }"
      ref="sidebarRef"
    >
      <!-- 顶部导航 -->
      <div class="sidebar-header">
        <div class="logo" v-if="!sidebarCollapsed">
          <h3>📚 学习中心</h3>
        </div>
        <div class="logo collapsed-logo" v-else>
          <span>📚</span>
        </div>
      </div>

      <!-- 返回首页按钮 -->
      <div class="back-home">
        <el-button
                  link
                  @click="backToDashboard"
                  class="back-btn"
                >
          <el-icon><House /></el-icon>
          <span v-if="!sidebarCollapsed">返回首页</span>
        </el-button>
      </div>

      <!-- 分类菜单 -->
      <div class="category-menu" v-if="!sidebarCollapsed">
        <div 
          v-for="file in files" 
          :key="file.id"
          class="tree-node"
          :class="{ 'is-current': currentCategoryId === file.id }"
          @click="handleCategoryClick({ id: file.id, file: file })"
        >
          <el-icon v-if="getFileIcon(file.type)">
            <component :is="getFileIcon(file.type)" />
          </el-icon>
          <span>{{ file.name }}</span>
        </div>
      </div>
    </aside>

    <!-- 右侧主内容区 -->
    <main class="content-area" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <!-- 顶部工具栏 -->
      <div class="content-header">
        <div class="header-left">
          <el-button
                  link
                  class="sidebar-toggle-btn"
                  @click="toggleSidebar"
                  :title="sidebarCollapsed ? '展开菜单' : '收起菜单'"
                >
            <el-icon v-if="sidebarCollapsed" style="font-size: 24px;"><Expand /></el-icon>
            <el-icon v-else style="font-size: 24px;"><Fold /></el-icon>
          </el-button>
          <div class="breadcrumb">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item v-for="(item, index) in breadcrumb" :key="index">
                {{ item.label }}
              </el-breadcrumb-item>
            </el-breadcrumb>
          </div>
        </div>
        <div class="toolbar">


          <!-- 缩放控制 -->
          <div class="zoom-controls">
            <el-button
                      link
                      @click="zoomOut"
                      :disabled="zoomLevel <= 50"
                      size="small"
                    >
              <el-icon><Minus /></el-icon>
            </el-button>
            <span class="zoom-level">{{ zoomLevel }}%</span>
            <el-button
                      link
                      @click="zoomIn"
                      :disabled="zoomLevel >= 200"
                      size="small"
                    >
              <el-icon><Plus /></el-icon>
            </el-button>
          </div>

          <!-- 收藏按钮 -->
          <el-button
                    :type="isFavorited ? 'primary' : 'default'"
                    link
                    size="small"
                    @click="toggleFavorite"
                  >
            <el-icon v-if="isFavorited"><StarFilled /></el-icon>
            <el-icon v-else><Star /></el-icon>
            <span v-if="!sidebarCollapsed">收藏</span>
          </el-button>
        </div>
      </div>

      <!-- 内容展示区 -->
      <div ref="contentDisplayRef" class="content-display" :style="{ transform: `scale(${zoomLevel / 100})`, transformOrigin: 'top left' }">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <el-skeleton :loading="true" animated>
            <template #template>
              <el-skeleton-item variant="p" style="width: 100%" />
              <el-skeleton-item variant="p" style="width: 90%" />
              <el-skeleton-item variant="p" style="width: 95%" />
              <el-skeleton-item variant="p" style="width: 85%" />
              <el-skeleton-item variant="p" style="width: 100%" />
            </template>
          </el-skeleton>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error" class="error-container">
          <el-empty
            description="
              <span>加载失败，请重试</span>
            "
          >
            <el-button type="primary" @click="loadContent(currentCategoryId)">
              重试
            </el-button>
          </el-empty>
        </div>

        <!-- 内容展示 -->
        <div v-else class="content-body">
          <!-- 文档类内容 -->
          <div v-if="contentType === 'document'" class="document-content">
            <h1>{{ content.title }}</h1>
            <div class="document-body">
              <!-- 文本文件预览 -->
              <div v-if="isTextFile(content.file)" class="text-preview">
                <pre v-if="fileContent" class="text-content">{{ fileContent }}</pre>
                <el-skeleton v-else :loading="loadingContent" animated>
                  <template #template>
                    <el-skeleton-item variant="p" style="width: 100%" />
                    <el-skeleton-item variant="p" style="width: 90%" />
                    <el-skeleton-item variant="p" style="width: 95%" />
                    <el-skeleton-item variant="p" style="width: 85%" />
                    <el-skeleton-item variant="p" style="width: 100%" />
                  </template>
                </el-skeleton>
              </div>
              
              <!-- PDF 文件预览 -->
              <div v-else-if="isPdfFile(content.file)" class="pdf-preview">
                <iframe :src="content.url" width="100%" height="600px" frameborder="0"></iframe>
              </div>
              
              <!-- Office 文件预览 -->
              <div v-else-if="isOfficeFile(content.file)" class="office-preview">
                <div class="office-preview-content">
                  <div class="office-icon">
                    <el-icon size="64"><Document /></el-icon>
                  </div>
                  <p class="office-name">{{ content.file?.name }}</p>
                  <p class="office-tip">此文件不支持在浏览器中直接预览</p>
                  <el-button type="primary" size="large" @click="downloadFile(content.file)">
                    <el-icon><Download /></el-icon>
                    下载文件
                  </el-button>
                </div>
              </div>
              
              <!-- 其他文档类型 -->
              <div v-else class="other-document">
                <p style="margin-left: 20px;">这是一个文档文件，您可以点击下方链接下载查看：</p>
                <div style="margin-left: 20px;margin-bottom: 20px;">
                  <el-button type="primary" @click="downloadFile(content.file)">
                    <el-icon><Download /></el-icon>
                    下载文件
                  </el-button>
                </div>
              </div>
              
              <div v-if="content.file" class="file-info">
                <p><strong>文件大小：</strong>{{ formatFileSize(content.file.size) }}</p>
                <p><strong>文件类型：</strong>{{ formatFileType(content.file.type) }}</p>
                <p><strong>上传时间：</strong>{{ content.file.uploadTime }}</p>
                <p><strong>上传用户：</strong>{{ content.file.username }}</p>
              </div>
            </div>
          </div>

          <!-- 图片类内容 -->
          <div v-else-if="contentType === 'image'" class="image-content">
            <h1>{{ content.title }}</h1>
            <el-image
              :src="content.url"
              fit="contain"
              class="preview-image"
            />
          </div>

          <!-- 视频类内容 -->
          <div v-else-if="contentType === 'video'" class="video-content">
            <h1>{{ content.title }}</h1>
            <video
              :src="content.url"
              controls
              class="preview-video"
            >
              您的浏览器不支持视频播放
            </video>
          </div>

          <!-- 音频类内容 -->
          <div v-else-if="contentType === 'audio'" class="audio-content">
            <h1>{{ content.title }}</h1>
            <audio
              :src="content.url"
              controls
              class="preview-audio"
            >
              您的浏览器不支持音频播放
            </audio>
          </div>

          <!-- 空内容 -->
          <div v-else class="empty-content">
            <el-empty description="请选择培训内容" />
          </div>
        </div>
      </div>

      <!-- 底部导航 -->
      <div class="content-footer">
        <el-button
          link
          @click="previousContent"
          :disabled="!hasPrevious"
        >
          <el-icon><ArrowLeft /></el-icon>
          上一篇
        </el-button>
        <div class="progress-info">
          <span>阅读进度：{{ progressPercentage }}%</span>
          <el-progress
            :percentage="progressPercentage"
            :stroke-width="6"
            :show-text="false"
          />
        </div>
        <el-button
          link
          @click="nextContent"
          :disabled="!hasNext"
        >
          下一篇
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  House, ArrowLeft, ArrowRight, Star, StarFilled, 
  Plus, Minus, Expand, Fold, Document, Picture, VideoCamera, Download 
} from '@element-plus/icons-vue'
import { getFileList } from '@/api/upload'
import axios from 'axios'

const router = useRouter()

// 状态管理
const sidebarRef = ref(null)
const sidebarCollapsed = ref(false)
const categories = ref([])
const currentCategoryId = ref(null)
const content = ref({})
const loading = ref(false)
const error = ref(false)

// 文件列表相关状态
const files = ref([])
const loadingFiles = ref(false)

const zoomLevel = ref(100)
const isFavorited = ref(false)
const progressPercentage = ref(0)

// 文件内容预览相关状态
const fileContent = ref('')
const loadingContent = ref(false)

const breadcrumb = computed(() => {
  const path = []
  const current = currentCategoryId.value
  if (current) {
    const file = files.value.find(f => f.id === current)
    if (file) {
      path.push({ id: file.id, label: file.name })
    }
  }
  return path
})

const contentType = computed(() => {
  if (!content.value.file) return 'document'
  const fileType = content.value.file.type
  if (!fileType) {
    // 如果没有文件类型，根据文件名扩展名判断
    const extension = content.value.file.name.split('.').pop().toLowerCase()
    if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(extension)) {
      return 'image'
    } else if (['mp4', 'webm', 'avi', 'mov', 'wmv'].includes(extension)) {
      return 'video'
    } else if (['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'md', 'html'].includes(extension)) {
      return 'document'
    }
    return 'document'
  }
  
  // 根据 MIME 类型判断
  if (fileType.startsWith('image/')) {
    return 'image'
  } else if (fileType.startsWith('video/')) {
    return 'video'
  } else if (fileType.startsWith('audio/')) {
    return 'audio'
  } else if (['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation', 'text/plain', 'text/html', 'text/markdown'].includes(fileType)) {
    return 'document'
  }
  return 'document'
})

const hasPrevious = ref(false)
const hasNext = ref(false)

// 方法
const toggleSidebar = () => {
  // 切换折叠状态
  sidebarCollapsed.value = !sidebarCollapsed.value
  // 保存折叠状态
  localStorage.setItem('sidebarCollapsed', sidebarCollapsed.value)
  
  // 如果是展开侧边栏，需要重新触发动画
  if (!sidebarCollapsed.value) {
    nextTick(() => {
      // 触发重绘，重新执行动画
      const sidebar = sidebarRef.value
      if (sidebar) {
        sidebar.classList.add('animate-in')
        setTimeout(() => {
          sidebar.classList.remove('animate-in')
        }, 100)
      }
    })
  }
}

const backToDashboard = () => {
  router.push('/dashboard')
}

const handleCategoryClick = (data) => {
  currentCategoryId.value = data.id
  loadContent(data.id)
  // 保存当前分类
  localStorage.setItem('currentCategoryId', data.id)
}

const loadContent = async (categoryId) => {
  if (!categoryId) return
  
  loading.value = true
  error.value = false
  
  try {
    // 查找对应的文件
    const file = files.value.find(f => f.id === categoryId)
    if (file) {
      // 根据文件类型设置内容
      content.value = {
        id: file.id,
        title: file.name,
        url: `http://localhost:8001/upload/download/${file.id}`,
        file: file
      }
      
      // 加载文本文件内容
      if (isTextFile(file)) {
        await loadTextFileContent(file.id)
      } else {
        fileContent.value = ''
      }
      
      // 模拟收藏状态
      isFavorited.value = categoryId % 2 === 0
      
      // 初始进度设置
      progressPercentage.value = 0
      
      // 模拟上下篇
      const fileIndex = files.value.findIndex(f => f.id === categoryId)
      hasPrevious.value = fileIndex > 0
      hasNext.value = fileIndex < files.value.length - 1
      
      // 恢复滚动位置
      nextTick(() => {
        const savedScroll = localStorage.getItem(`scroll_${categoryId}`)
        if (savedScroll && contentDisplayRef.value) {
          contentDisplayRef.value.scrollTop = parseInt(savedScroll)
        }
        
        // 检查是否有滚动条，如果没有直接显示100%
        if (contentDisplayRef.value) {
          const scrollHeight = contentDisplayRef.value.scrollHeight
          const clientHeight = contentDisplayRef.value.clientHeight
          if (scrollHeight <= clientHeight) {
            progressPercentage.value = 100
          }
        }
      })
    } else {
      // 没有找到文件，显示空内容
      content.value = {}
      ElMessage.warning('未找到文件')
    }
  } catch (err) {
    console.error('加载内容失败:', err)
    error.value = true
    ElMessage.error('加载内容失败，请重试')
  } finally {
    loading.value = false
  }
}

// 加载文本文件内容
const loadTextFileContent = async (fileId) => {
  loadingContent.value = true
  try {
    const response = await axios({
      url: `http://localhost:8001/upload/download/${fileId}`,
      method: 'GET',
      responseType: 'text',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    fileContent.value = response.data
  } catch (error) {
    console.error('加载文件内容失败:', error)
    fileContent.value = ''
  } finally {
    loadingContent.value = false
  }
}

// 判断是否为文本文件
const isTextFile = (file) => {
  if (!file) return false
  const extension = file.name.split('.').pop().toLowerCase()
  return ['txt', 'md', 'html', 'css', 'js', 'json', 'xml', 'csv', 'log'].includes(extension)
}

// 判断是否为PDF文件
const isPdfFile = (file) => {
  if (!file) return false
  const extension = file.name.split('.').pop().toLowerCase()
  return extension === 'pdf'
}

// 判断是否为Office文件
const isOfficeFile = (file) => {
  if (!file) return false
  const extension = file.name.split('.').pop().toLowerCase()
  return ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'].includes(extension)
}

// 获取Office文件预览URL
const getOfficePreviewUrl = (file) => {
  // 在开发环境下，由于Office Online无法访问localhost，直接返回下载链接
  // 生产环境可以使用Office Online预览
  const fileUrl = `http://localhost:8001/upload/download/${file.id}`
  return fileUrl
}

const zoomIn = () => {
  if (zoomLevel.value < 200) {
    zoomLevel.value += 10
  }
}

const zoomOut = () => {
  if (zoomLevel.value > 50) {
    zoomLevel.value -= 10
  }
}

const toggleFavorite = () => {
  isFavorited.value = !isFavorited.value
  ElMessage.success(isFavorited.value ? '已添加到收藏' : '已取消收藏')
  // 同步到后端
}

// 下载文件
const downloadFile = async (file) => {
  try {
    // 使用 axios 下载文件
    const response = await axios({
      url: `http://localhost:8001/upload/download/${file.id}`,
      method: 'GET',
      responseType: 'blob',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    // 创建一个 Blob URL
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    
    // 创建一个隐藏的 a 标签来触发下载
    const link = document.createElement('a')
    link.href = url
    link.download = file.name
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    
    // 清理
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('文件下载成功: ' + file.name)
  } catch (error) {
    ElMessage.error('下载文件失败')
    console.error('下载文件失败:', error)
  }
}

// 格式化文件大小
const formatFileSize = (size) => {
  if (size < 1024) {
    return size + ' B'
  } else if (size < 1024 * 1024) {
    return (size / 1024).toFixed(2) + ' KB'
  } else {
    return (size / (1024 * 1024)).toFixed(2) + ' MB'
  }
}

// 格式化文件类型
const formatFileType = (type) => {
  if (!type) return '未知'
  
  const typeMap = {
    'application/pdf': 'PDF 文档',
    'application/msword': 'Word 文档',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word 文档',
    'application/vnd.ms-excel': 'Excel 表格',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Excel 表格',
    'application/vnd.ms-powerpoint': 'PowerPoint 演示文稿',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'PowerPoint 演示文稿',
    'image/jpeg': '图片',
    'image/png': '图片',
    'image/gif': '图片',
    'image/bmp': '图片',
    'image/webp': '图片',
    'text/plain': '文本文件',
    'text/html': 'HTML 文件',
    'application/zip': '压缩文件',
    'application/x-rar-compressed': '压缩文件',
    'application/x-7z-compressed': '压缩文件',
    'application/x-tar': '压缩文件',
    'application/x-gzip': '压缩文件',
    'video/mp4': '视频',
    'video/avi': '视频',
    'video/mov': '视频',
    'video/wmv': '视频',
    'audio/mpeg': '音频',
    'audio/wav': '音频',
    'audio/ogg': '音频'
  }
  
  return typeMap[type] || type
}

const previousContent = () => {
  if (hasPrevious.value) {
    const fileIndex = files.value.findIndex(f => f.id === currentCategoryId.value)
    if (fileIndex > 0) {
      const prevFile = files.value[fileIndex - 1]
      currentCategoryId.value = prevFile.id
      loadContent(prevFile.id)
    }
  }
}

const nextContent = () => {
  if (hasNext.value) {
    const fileIndex = files.value.findIndex(f => f.id === currentCategoryId.value)
    if (fileIndex < files.value.length - 1) {
      const nextFile = files.value[fileIndex + 1]
      currentCategoryId.value = nextFile.id
      loadContent(nextFile.id)
    }
  }
}

// 键盘快捷键
const handleKeydown = (event) => {
  if (event.ctrlKey) {
    switch (event.key) {
      case 'f':
        event.preventDefault()
        document.querySelector('.search-input input').focus()
        break
      case '=':
        event.preventDefault()
        zoomIn()
        break
      case '-':
        event.preventDefault()
        zoomOut()
        break
    }
  }
  switch (event.key) {
    case 'Escape':
      if (!sidebarCollapsed.value) {
        toggleSidebar()
      }
      break
    case 'ArrowLeft':
      if (hasPrevious.value) {
        previousContent()
      }
      break
    case 'ArrowRight':
      if (hasNext.value) {
        nextContent()
      }
      break
  }
}

// 滚动事件，记录阅读进度
const contentDisplayRef = ref(null)

const handleScroll = () => {
  if (contentDisplayRef.value) {
    const scrollTop = contentDisplayRef.value.scrollTop
    const scrollHeight = contentDisplayRef.value.scrollHeight
    const clientHeight = contentDisplayRef.value.clientHeight
    const docHeight = scrollHeight - clientHeight
    
    if (docHeight > 0) {
      const progress = Math.round((scrollTop / docHeight) * 100)
      // 只有当当前进度小于100%时才更新
      if (progressPercentage.value < 100) {
        progressPercentage.value = progress
      }
    } else {
      // 没有滚动条时直接显示100%
      progressPercentage.value = 100
    }
    
    // 保存滚动位置
    if (currentCategoryId.value) {
      localStorage.setItem(`scroll_${currentCategoryId.value}`, scrollTop)
    }
  }
}

// 根据文件类型获取图标
const getFileIcon = (fileType) => {
  if (!fileType) {
    return 'Document'
  }
  
  if (fileType.startsWith('image/')) {
    return 'Picture'
  } else if (fileType.startsWith('video/')) {
    return 'VideoCamera'
  } else if (fileType.startsWith('audio/')) {
    return 'VideoCamera'
  } else {
    return 'Document'
  }
}

// 加载文件列表
const loadCategories = async () => {
  try {
    loadingFiles.value = true
    // 调用API获取文件列表
    const response = await getFileList(1, 100, '')
    if (response && response.success && response.files) {
      files.value = response.files
    }
  } catch (err) {
    console.error('加载文件列表失败:', err)
    ElMessage.error('加载文件列表失败，请重试')
  } finally {
    loadingFiles.value = false
  }
}

// 生命周期
onMounted(async () => {
  // 加载分类数据
  await loadCategories()
  
  // 恢复状态
  const savedCollapsed = localStorage.getItem('sidebarCollapsed')
  if (savedCollapsed !== null) {
    sidebarCollapsed.value = savedCollapsed === 'true'
  }
  
  const savedCategoryId = localStorage.getItem('currentCategoryId')
  if (savedCategoryId) {
    currentCategoryId.value = parseInt(savedCategoryId)
    loadContent(currentCategoryId.value)
  }
  
  // 添加事件监听
  window.addEventListener('keydown', handleKeydown)
  if (contentDisplayRef.value) {
    contentDisplayRef.value.addEventListener('scroll', handleScroll)
  }
})

// 清理事件监听
onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  if (contentDisplayRef.value) {
    contentDisplayRef.value.removeEventListener('scroll', handleScroll)
  }
})
</script>

<style scoped>
.training-content-layout {
  display: flex;
  height: 100vh;
  background: #d9f4e6;
  transition: all 0.3s ease;
  font-family: 'PingFang SC', 'Helvetica Neue', STHeiti, 'Microsoft Yahei', sans-serif;
}

/* 侧边栏 */
.sidebar {
  width: 280px;
  background: linear-gradient(135deg, #f0f9f4, #e6f7ee);
  border-right: 1px solid rgba(141, 193, 73, 0.3);
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(141, 193, 73, 0.2);
  transition: width 0.5s ease-in-out;
  overflow: hidden;
  border-radius: 0 16px 16px 0;
}

.sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 2px solid rgba(141, 193, 73, 0.3);
  transition: all 0.5s ease-in-out;
  height: 64px;
  box-sizing: border-box;
  background: linear-gradient(135deg, #8DC149, #7ab838);
  color: white;
  border-radius: 0 16px 0 0;
}

.logo h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: white;
  transition: all 0.5s ease-in-out;
  opacity: 0;
  transform: translateX(-20px);
  animation: slideIn 0.5s ease-in-out forwards;
  animation-delay: 0.1s;
}

.collapsed-logo {
  font-size: 24px;
  transition: all 0.5s ease-in-out;
}

.back-home {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f5f9;
  transition: all 0.5s ease-in-out;
}

.back-btn {
  color: #2f5d50;
  width: 100%;
  justify-content: flex-start;
  transition: all 0.5s ease-in-out;
  font-size: 16px;
  position: relative;
}

.back-btn:hover {
  background: rgba(141, 193, 73, 0.2) !important;
  color: #228b22 !important;
}

.back-btn .el-icon {
  font-size: 24px;
  transition: all 0.5s ease-in-out;
  min-width: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #32cd32;
  background: rgba(152, 251, 152, 0.2);
  padding: 8px;
  border-radius: 50%;
  margin-right: 8px;
}

.back-btn:hover .el-icon {
  background: rgba(152, 251, 152, 0.4);
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(152, 251, 152, 0.4);
}

.back-btn span {
  opacity: 0;
  transform: translateX(-20px);
  animation: slideIn 0.5s ease-in-out forwards;
  animation-delay: 0.2s;
}

/* 侧边栏收起时的图标居中 */
.sidebar.collapsed .back-btn {
  justify-content: center;
  transition: all 0.5s ease-in-out;
}

/* 确保图标在收起状态下保持居中 */
.sidebar.collapsed .back-btn .el-icon {
  margin: 0;
}

.category-menu {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  transition: all 0.5s ease-in-out;
  opacity: 0;
  transform: translateX(-20px);
  animation: slideIn 0.5s ease-in-out forwards;
  animation-delay: 0.3s;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 16px;
  padding: 2px 6px;
  border-radius: 6px;
  transition: all 0.3s ease;
  background-color: transparent;
}

.tree-node:hover {
  background-color: rgba(141, 193, 73, 0.15);
}

.tree-node.is-current {
  background-color: rgba(141, 193, 73, 0.2);
}

.tree-node .el-icon {
  font-size: 16px;
  transition: all 0.5s ease-in-out;
  min-width: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #32cd32;
  background: rgba(152, 251, 152, 0.2);
  padding: 3px;
  border-radius: 3px;
}

.tree-node span {
  opacity: 0;
  transform: translateX(-10px);
  animation: slideIn 0.5s ease-in-out forwards;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  background-color: transparent;
}

/* 动画定义 */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .sidebar {
    width: 240px;
  }
  
  .sidebar.collapsed {
    width: 0;
  }
  
  .logo h3 {
    font-size: 16px;
  }
  
  .back-btn {
    font-size: 14px;
  }
  
  .back-btn .el-icon {
    font-size: 18px;
  }
  
  .tree-node {
    font-size: 14px;
  }
  
  .tree-node .el-icon {
    font-size: 18px;
  }
}

/* 主内容区 */
.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  transition: all 0.5s ease-in-out;
  margin: 20px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(141, 193, 73, 0.2);
  background: linear-gradient(135deg, #f0f9f4, #e6f7ee);
  border: 1px solid rgba(141, 193, 73, 0.3);
}

.content-header {
  background: linear-gradient(135deg, #8DC149, #7ab838);
  border-bottom: 2px solid rgba(141, 193, 73, 0.3);
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(141, 193, 73, 0.2);
  height: 64px;
  box-sizing: border-box;
  color: white;
}

.header-left {
  display: flex;
  align-items: center;
  flex: 1;
  gap: 12px;
}

.sidebar-toggle-btn {
  color: white;
  transition: all 0.3s ease-in-out;
}

.sidebar-toggle-btn:hover {
  color: #f0f9f4;
  background: rgba(255, 255, 255, 0.2) !important;
}

.breadcrumb {
  flex: 1;
}

.breadcrumb :deep(.el-breadcrumb__inner) {
  color: white !important;
}

.breadcrumb :deep(.el-breadcrumb__separator) {
  color: rgba(255, 255, 255, 0.7) !important;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.zoom-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.zoom-level {
  min-width: 40px;
  text-align: center;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
}

.toolbar :deep(.el-button) {
  color: white !important;
}

.toolbar :deep(.el-button:hover) {
  background: rgba(255, 255, 255, 0.2) !important;
}

.content-display {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  transition: transform 0.3s ease;
  background: linear-gradient(135deg, #f0f9f4, #e6f7ee);
}

.loading-container,
.error-container,
.empty-content {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.content-body {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  padding: 32px;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(141, 193, 73, 0.2);
  border: 1px solid rgba(141, 193, 73, 0.3);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.content-body:hover {
  box-shadow: 0 8px 32px rgba(141, 193, 73, 0.3);
  transform: translateY(-2px);
}

.content-body::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #98FB98, #7ab838, #98FB98);
  transform: scaleX(1);
  transform-origin: left;
  transition: transform 0.3s ease;
}

.document-content h1 {
  color: #228b22;
  margin-bottom: 24px;
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.document-body {
  line-height: 1.8;
  color: #374151;
}

.document-body h2 {
  color: #32cd32;
  margin: 24px 0 16px;
  font-size: 20px;
  font-weight: 600;
}

.document-body p {
  margin-bottom: 16px;
  color: #374151;
  line-height: 1.8;
}

/* 文本文件预览样式 */
.text-preview {
  margin-bottom: 20px;
}

.text-content {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 600px;
  overflow-y: auto;
}

/* PDF 和 Office 文件预览样式 */
.pdf-preview,
.office-preview {
  margin-bottom: 20px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  overflow: hidden;
}

.office-preview-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  min-height: 400px;
}

.office-icon {
  color: #8DC149;
  margin-bottom: 20px;
}

.office-name {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 10px 0;
  text-align: center;
  word-break: break-all;
  max-width: 100%;
}

.office-tip {
  font-size: 14px;
  color: #666;
  margin-bottom: 30px;
}

.preview-image {
  max-width: 100%;
  max-height: 600px;
  margin: 20px 0;
}

.preview-video {
  width: 100%;
  max-height: 600px;
  margin: 20px 0;
}

.preview-audio {
  width: 100%;
  margin: 20px 0;
}

.file-info {
  margin-top: 20px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.file-info p {
  margin-bottom: 8px;
  color: #495057;
}

.file-info p strong {
  color: #2c3e50;
  margin-right: 8px;
}

.content-footer {
  background: linear-gradient(135deg, #8DC149, #7ab838);
  border-top: 2px solid rgba(141, 193, 73, 0.3);
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 -2px 8px rgba(141, 193, 73, 0.2);
  color: white;
}

.progress-info {
  flex: 1;
  margin: 0 20px;
}

.progress-info span {
  display: block;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 4px;
}

.content-footer :deep(.el-button) {
  color: white !important;
}

.content-footer :deep(.el-button:hover) {
  background: rgba(255, 255, 255, 0.2) !important;
}

.content-footer :deep(.el-progress__bar) {
  background-color: rgba(255, 255, 255, 0.3) !important;
}

.content-footer :deep(.el-progress__inner) {
  background-color: #98FB98 !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .training-content-layout {
    flex-direction: column;
  }
  
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    z-index: 1000;
    transform: translateX(0);
  }
  
  .sidebar.collapsed {
    transform: translateX(-100%);
  }
  
  .content-area {
    margin-left: 0;
  }
  
  .content-header {
    padding: 12px;
  }
  
  .content-display {
    padding: 16px;
  }
  
  .content-body {
    padding: 24px;
  }
  
  .toolbar {
    gap: 8px;
  }
  
  .search-input {
    width: 160px;
  }
}
</style>