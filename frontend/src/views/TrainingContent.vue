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
          text
          @click="backToDashboard"
          class="back-btn"
        >
          <el-icon><House /></el-icon>
          <span v-if="!sidebarCollapsed">返回首页</span>
        </el-button>
      </div>

      <!-- 分类菜单 -->
      <div class="category-menu" v-if="!sidebarCollapsed">
        <el-tree
          :data="categories"
          :props="treeProps"
          node-key="id"
          default-expand-all
          @node-click="handleCategoryClick"
          :current-node-key="currentCategoryId"
          :highlight-current="true"
          class="category-tree"
        >
          <template #default="{ node, data }">
            <div class="tree-node">
              <el-icon v-if="data.icon">
                <component :is="data.icon" />
              </el-icon>
              <span>{{ node.label }}</span>
            </div>
          </template>
        </el-tree>
      </div>
    </aside>

    <!-- 右侧主内容区 -->
    <main class="content-area" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <!-- 顶部工具栏 -->
      <div class="content-header">
        <div class="header-left">
          <el-button
            text
            class="sidebar-toggle-btn"
            @click="toggleSidebar"
            :title="sidebarCollapsed ? '展开菜单' : '收起菜单'"
          >
            <el-icon v-if="sidebarCollapsed"><ArrowLeft /></el-icon>
            <el-icon v-else><ArrowRight /></el-icon>
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
              text
              @click="zoomOut"
              :disabled="zoomLevel <= 50"
              size="small"
            >
              <el-icon><Minus /></el-icon>
            </el-button>
            <span class="zoom-level">{{ zoomLevel }}%</span>
            <el-button
              text
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
            text
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
      <div class="content-display" :style="{ transform: `scale(${zoomLevel / 100})`, transformOrigin: 'top left' }">
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
            <div v-html="content.content" class="document-body"></div>
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

          <!-- 空内容 -->
          <div v-else class="empty-content">
            <el-empty description="请选择培训内容" />
          </div>
        </div>
      </div>

      <!-- 底部导航 -->
      <div class="content-footer">
        <el-button
          text
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
          text
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
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  House, ArrowLeft, ArrowRight, Star, StarFilled, 
  Plus, Minus 
} from '@element-plus/icons-vue'

const router = useRouter()

// 状态管理
const sidebarRef = ref(null)
const sidebarCollapsed = ref(false)
const categories = ref([])
const currentCategoryId = ref(null)
const content = ref({})
const loading = ref(false)
const error = ref(false)

const zoomLevel = ref(100)
const isFavorited = ref(false)
const progressPercentage = ref(0)

// 计算属性
const treeProps = {
  children: 'children',
  label: 'name'
}

const breadcrumb = computed(() => {
  const path = []
  let current = currentCategoryId.value
  while (current) {
    const category = findCategoryById(categories.value, current)
    if (category) {
      path.unshift({ id: category.id, label: category.name })
      current = category.parentId
    } else {
      break
    }
  }
  return path
})

const contentType = computed(() => {
  if (!content.value.url) return 'document'
  const extension = content.value.url.split('.').pop().toLowerCase()
  if (['jpg', 'jpeg', 'png', 'gif'].includes(extension)) {
    return 'image'
  } else if (['mp4', 'webm'].includes(extension)) {
    return 'video'
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

const findCategoryById = (categories, id) => {
  for (const category of categories) {
    if (category.id === id) return category
    if (category.children) {
      const found = findCategoryById(category.children, id)
      if (found) return found
    }
  }
  return null
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
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 模拟数据
    content.value = {
      id: categoryId,
      title: `培训内容 ${categoryId}`,
      content: `<h2>章节 1</h2><p>这是培训内容的第一章节，包含详细的知识点和操作指南。</p><h2>章节 2</h2><p>这是培训内容的第二章节，包含更多的实践案例和应用场景。</p>`,
      url: categoryId % 3 === 0 ? 'https://example.com/sample.jpg' : 
           categoryId % 3 === 1 ? 'https://example.com/sample.mp4' : ''
    }
    
    // 模拟收藏状态
    isFavorited.value = categoryId % 2 === 0
    
    // 模拟进度
    progressPercentage.value = Math.floor(Math.random() * 100)
    
    // 模拟上下篇
    hasPrevious.value = categoryId > 1
    hasNext.value = categoryId < 10
    
    // 恢复滚动位置
    nextTick(() => {
      const savedScroll = localStorage.getItem(`scroll_${categoryId}`)
      if (savedScroll) {
        window.scrollTo(0, parseInt(savedScroll))
      }
    })
  } catch (err) {
    console.error('加载内容失败:', err)
    error.value = true
    ElMessage.error('加载内容失败，请重试')
  } finally {
    loading.value = false
  }
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

const previousContent = () => {
  if (hasPrevious.value) {
    const prevId = currentCategoryId.value - 1
    currentCategoryId.value = prevId
    loadContent(prevId)
  }
}

const nextContent = () => {
  if (hasNext.value) {
    const nextId = currentCategoryId.value + 1
    currentCategoryId.value = nextId
    loadContent(nextId)
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
const handleScroll = () => {
  const scrollTop = window.scrollY
  const docHeight = document.documentElement.scrollHeight - window.innerHeight
  const progress = Math.round((scrollTop / docHeight) * 100)
  progressPercentage.value = progress
  
  // 保存滚动位置
  if (currentCategoryId.value) {
    localStorage.setItem(`scroll_${currentCategoryId.value}`, scrollTop)
  }
}

// 模拟加载分类数据
const loadCategories = async () => {
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 模拟数据
    categories.value = [
      {
        id: 1,
        name: '产品知识',
        icon: 'Goods',
        children: [
          {
            id: 2,
            name: '产品介绍',
            children: [
              { id: 3, name: '核心功能' },
              { id: 4, name: '使用场景' }
            ]
          },
          {
            id: 5,
            name: '产品更新',
            children: [
              { id: 6, name: '版本历史' },
              { id: 7, name: '新功能介绍' }
            ]
          }
        ]
      },
      {
        id: 8,
        name: '操作指南',
        icon: 'Operation',
        children: [
          {
            id: 9,
            name: '基础操作',
            children: [
              { id: 10, name: '账号管理' },
              { id: 11, name: '系统设置' }
            ]
          },
          {
            id: 12,
            name: '高级功能',
            children: [
              { id: 13, name: '数据分析' },
              { id: 14, name: '自动化流程' }
            ]
          }
        ]
      },
      {
        id: 15,
        name: '常见问题',
        icon: 'QuestionFilled',
        children: [
          { id: 16, name: '技术问题' },
          { id: 17, name: '业务问题' }
        ]
      }
    ]
  } catch (err) {
    console.error('加载分类失败:', err)
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
  window.addEventListener('scroll', handleScroll)
})

// 清理事件监听
const onUnmounted = () => {
  window.removeEventListener('keydown', handleKeydown)
  window.removeEventListener('scroll', handleScroll)
}
</script>

<style scoped>
.training-content-layout {
  display: flex;
  height: 100vh;
  background: #f5f7fa;
  transition: all 0.3s ease;
}

/* 侧边栏 */
.sidebar {
  width: 200px;
  background: #ffffff;
  border-right: 1px solid #e8eef3;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
  transition: width 0.5s ease-in-out;
  overflow: hidden;
}

.sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #f0f5f9;
  transition: all 0.5s ease-in-out;
}

.logo h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #2f5d50;
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

.back-btn .el-icon {
  font-size: 20px;
  transition: all 0.5s ease-in-out;
  min-width: 20px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
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
  padding: 16px;
  transition: all 0.5s ease-in-out;
  opacity: 0;
  transform: translateX(-20px);
  animation: slideIn 0.5s ease-in-out forwards;
  animation-delay: 0.3s;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
}

.tree-node .el-icon {
  font-size: 20px;
  transition: all 0.5s ease-in-out;
}

.tree-node span {
  opacity: 0;
  transform: translateX(-10px);
  animation: slideIn 0.5s ease-in-out forwards;
}

/* 为每个树节点添加不同的动画延迟，实现逐个显示效果 */
.el-tree-node {
  animation: fadeIn 0.5s ease-in-out forwards;
  opacity: 0;
}

.el-tree-node:nth-child(1) {
  animation-delay: 0.4s;
}

.el-tree-node:nth-child(2) {
  animation-delay: 0.5s;
}

.el-tree-node:nth-child(3) {
  animation-delay: 0.6s;
}

.el-tree-node:nth-child(4) {
  animation-delay: 0.7s;
}

.el-tree-node:nth-child(5) {
  animation-delay: 0.8s;
}

/* 侧边栏收起时的图标居中 */
.sidebar.collapsed .back-btn {
  justify-content: center;
  transition: all 0.5s ease-in-out;
}

/* 侧边栏收起时隐藏标题 */
.sidebar.collapsed .logo h3 {
  display: none;
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

.category-tree {
  --el-tree-node-content-hover-bg-color: rgba(52, 211, 153, 0.08);
  --el-tree-node-hover-bg-color: rgba(52, 211, 153, 0.08);
  --el-tree-node-current-bg-color: rgba(52, 211, 153, 0.15);
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 主内容区 */
.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  transition: all 0.5s ease-in-out;
}

.content-header {
  background: #ffffff;
  border-bottom: 1px solid #f0f5f9;
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
}

.header-left {
  display: flex;
  align-items: center;
  flex: 1;
  gap: 12px;
}

.sidebar-toggle-btn {
  color: #6b7280;
  transition: all 0.3s ease-in-out;
}

.sidebar-toggle-btn:hover {
  color: #2f5d50;
  background: rgba(52, 211, 153, 0.1);
}

.breadcrumb {
  flex: 1;
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
  color: #6b7280;
}

.content-display {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  transition: transform 0.3s ease;
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
  background: #ffffff;
  padding: 32px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.document-content h1 {
  color: #1f2937;
  margin-bottom: 24px;
  font-size: 24px;
}

.document-body {
  line-height: 1.8;
  color: #374151;
}

.document-body h2 {
  color: #1f2937;
  margin: 24px 0 16px;
  font-size: 20px;
}

.document-body p {
  margin-bottom: 16px;
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

.content-footer {
  background: #ffffff;
  border-top: 1px solid #f0f5f9;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.04);
}

.progress-info {
  flex: 1;
  margin: 0 20px;
}

.progress-info span {
  display: block;
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
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