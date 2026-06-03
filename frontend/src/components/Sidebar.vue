<template>
  <div class="admin-sidebar">
    <div class="sidebar-header">
      <el-icon class="logo-icon"><Management /></el-icon>
      <h1 class="sidebar-title">管理员控制台</h1>
    </div>
    
    <div class="sidebar-menu">
      <div 
        class="menu-item" 
        :class="{ active: activeMenu === 'user' }"
        @click="handleMenuClick('user')"
      >
        <el-icon class="menu-icon"><User /></el-icon>
        <span class="menu-text">用户管理</span>
      </div>
      <div 
        class="menu-item" 
        :class="{ active: activeMenu === 'file' }"
        @click="handleMenuClick('file')"
      >
        <el-icon class="menu-icon"><Upload /></el-icon>
        <span class="menu-text">文件上传</span>
      </div>
      <div 
        class="menu-item" 
        :class="{ active: activeMenu === 'learning' }"
        @click="handleMenuClick('learning')"
      >
        <el-icon class="menu-icon"><Document /></el-icon>
        <span class="menu-text">学习情况</span>
      </div>
      <div 
        class="menu-item" 
        :class="{ active: activeMenu === 'question' }"
        @click="handleMenuClick('question')"
      >
        <el-icon class="menu-icon"><HelpFilled /></el-icon>
        <span class="menu-text">题库管理</span>
      </div>
      <div 
        class="menu-item" 
        :class="{ active: activeMenu === 'exam-results' }"
        @click="handleMenuClick('exam-results')"
      >
        <el-icon class="menu-icon"><Trophy /></el-icon>
        <span class="menu-text">员工成绩</span>
      </div>
    </div>
    
    <div class="sidebar-footer">
      <div class="user-info" @click="showUserMenu = !showUserMenu">
        <el-avatar size="small" :src="userAvatar"></el-avatar>
        <span class="user-name">{{ userNickname }}</span>
        <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
      </div>
      <div v-if="showUserMenu" class="user-menu">
        <div class="menu-item" @click="$emit('logout')">
          <el-icon class="menu-icon"><SwitchButton /></el-icon>
          <span class="menu-text">退出登录</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Management, User, Upload, Document, HelpFilled, Trophy, ArrowDown, SwitchButton } from '@element-plus/icons-vue'

// Props
const props = defineProps({
  activeMenu: {
    type: String,
    default: 'user'
  },
  userNickname: {
    type: String,
    default: '管理员'
  }
})

// Emits
const emit = defineEmits(['menu-change', 'logout'])

const showUserMenu = ref(true)

// 计算属性：用户头像
const userAvatar = computed(() => {
  const nickname = props.userNickname || '管理员'
  const avatarName = nickname.length <= 2 ? nickname : nickname.slice(-2)
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(avatarName)}&background=2e8b57&color=fff`
})

// 方法
const handleMenuClick = (menu) => {
  emit('menu-change', menu)
}
</script>

<style scoped>
/* 侧边栏样式 */
.admin-sidebar {
  width: 250px;
  background: #ffffff;
  border-right: 1px solid #e8eef3;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.sidebar-header {
  padding: 24px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 24px;
  color: #2e8b57;
}

.sidebar-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #2e8b57;
}

.sidebar-menu {
  flex: 1;
  padding: 16px 0;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
}

.menu-item:hover {
  background-color: #f0f2f5;
}

.menu-item.active {
  background-color: #e6f7ee;
  border-left-color: #2e8b57;
  color: #2e8b57;
}

.menu-icon {
  font-size: 18px;
}

.menu-text {
  font-size: 14px;
  font-weight: 500;
}

.sidebar-footer {
  padding: 16px 0;
  border-top: 1px solid #f0f0f0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 24px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-info:hover {
  background-color: #f0f2f5;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  flex: 1;
}

.dropdown-icon {
  font-size: 12px;
  color: #666;
  transition: transform 0.3s ease;
}

.user-menu {
  background-color: #f0f2f5;
  margin: 8px 16px;
  border-radius: 8px;
  overflow: hidden;
}

.user-menu .menu-item {
  padding: 8px 16px;
  border-left: none;
}

.user-menu .menu-item:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-sidebar {
    width: 200px;
  }
  
  .sidebar-title {
    font-size: 16px;
  }
}
</style>