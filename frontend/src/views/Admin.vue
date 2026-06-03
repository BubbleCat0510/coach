<template>
  <div class="admin-container">
    <!-- 侧边栏 -->
    <Sidebar 
      :active-menu="activeMenu"
      :user-nickname="userNickname"
      @menu-change="handleMenuChange"
      @logout="logout"
    />

    <!-- 主内容区域 -->
    <div class="admin-main">
      <!-- 顶部导航 -->
      <AdminHeader :page-title="pageTitle" />

      <!-- 内容区域 -->
      <div class="admin-content">
        <router-view></router-view>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'
import { getNickname, logoutApi } from '@/api/user'
import Sidebar from '@/components/Sidebar.vue'
import AdminHeader from '@/components/AdminHeader.vue'

const router = useRouter()
const route = useRoute()

// 状态管理
const activeMenu = ref('user')
const userNickname = ref('管理员')

// 页面挂载时加载数据
onMounted(() => {
  // 检查是否有token
  const token = localStorage.getItem('token')
  if (!token) {
    // 没有token，跳转到登录页面
    router.push('/login')
    return
  }
  
  // 获取用户昵称
  getNickname().then(response => {
    if (response && response.nickname) {
      userNickname.value = response.nickname
    }
  }).catch(error => {
    console.error('获取用户昵称失败:', error)
  })
  
  // 根据当前路由设置activeMenu
  const currentPath = route.path
  if (currentPath.includes('/admin/user')) {
    activeMenu.value = 'user'
  } else if (currentPath.includes('/admin/file')) {
    activeMenu.value = 'file'
  } else if (currentPath.includes('/admin/learning')) {
    activeMenu.value = 'learning'
  } else if (currentPath.includes('/admin/question')) {
    activeMenu.value = 'question'
  } else if (currentPath.includes('/admin/exam-results')) {
    activeMenu.value = 'exam-results'
  }
})

// 计算属性：用户头像
const userAvatar = computed(() => {
  return `https://ui-avatars.com/api/?name=Admin&background=2e8b57&color=fff`
})

// 计算属性：页面标题
const pageTitle = computed(() => {
  switch (activeMenu.value) {
    case 'user':
      return '用户管理'
    case 'file':
      return '文件上传'
    case 'learning':
      return '学习情况'
    case 'question':
      return '题库管理'
    case 'exam-results':
      return '员工成绩'
    default:
      return '管理员控制台'
  }
})

// 处理菜单切换
const handleMenuChange = (menu) => {
  activeMenu.value = menu
  switch (menu) {
    case 'user':
      router.push('/admin/user')
      break
    case 'file':
      router.push('/admin/file')
      break
    case 'learning':
      router.push('/admin/learning')
      break
    case 'question':
      router.push('/admin/question')
      break
    case 'exam-results':
      router.push('/admin/exam-results')
      break
  }
}

// 退出登录
const logout = async () => {
  try {
    await logoutApi()
  } catch (error) {
    console.error('登出接口失败', error)
  } finally {
    // 清除登录态
    localStorage.removeItem('token')
    localStorage.removeItem('userRole')
    sessionStorage.clear()
    ElMessage.success('已退出登录')
    // 跳转到登录页
    router.push('/login')
  }
}
</script>

<style scoped>
.admin-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  font-family: 'PingFang SC', 'Helvetica Neue', STHeiti, 'Microsoft Yahei', sans-serif;
  overflow: hidden;
}

/* 主内容区域 */
.admin-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.admin-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  box-sizing: border-box;
}
</style>