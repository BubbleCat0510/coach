<template>
  <div class="exam-center-page">
    <!-- 顶部标题栏 -->
    <div class="header">
      <div class="header-left">
        <el-button link @click="goBack" class="back-btn">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
      </div>
      <div class="header-title">
        <h2>AI 冠军教练 · 评估中心</h2>
      </div>
      <div class="header-right">
        <span class="username">{{ username }}</span>
        <el-button link @click="logout" class="logout-btn">退出登录</el-button>
      </div>
    </div>

    <!-- 主体内容区域 -->
    <div class="content">
      <div class="exam-container">
        <div class="exam-title">
          <h1>能力评估测试</h1>
          <p>通过测试评估你的各项能力指标</p>
        </div>

        <!-- 功能按钮区域 -->
        <div class="action-buttons">
          <el-card class="action-card" @click="startTest">
            <div class="card-content">
              <el-icon class="action-icon"><EditPen /></el-icon>
              <h3>开始测试</h3>
              <p>进入正式评估</p>
            </div>
          </el-card>

          <el-card class="action-card" @click="startMockTest">
            <div class="card-content">
              <el-icon class="action-icon"><Star /></el-icon>
              <h3>模拟测试</h3>
              <p>练习模式</p>
            </div>
          </el-card>

          <el-card class="action-card" @click="viewHistory">
            <div class="card-content">
              <el-icon class="action-icon"><Document /></el-icon>
              <h3>历史成绩</h3>
              <p>查看过往测试记录</p>
            </div>
          </el-card>

          <el-card class="action-card" @click="goHome">
            <div class="card-content">
              <el-icon class="action-icon"><HomeFilled /></el-icon>
              <h3>返回首页</h3>
              <p>回到工作台</p>
            </div>
          </el-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getNickname } from '../api/user'
import { ElMessage } from 'element-plus'
import { ArrowLeft, EditPen, Document, HomeFilled, Star } from '@element-plus/icons-vue'

const router = useRouter()

const username = ref('')

onMounted(async () => {
  try {
    const nicknameRes = await getNickname()
    username.value = nicknameRes.nickname || '用户'
  } catch (error) {
    console.error('获取用户信息失败:', error)
    username.value = '用户'
  }
})

const goBack = () => {
  router.back()
}

const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}

const startTest = () => {
  ElMessage.info('开始测试功能开发中...')
  //router.push('/exam-test')
}

const startMockTest = () => {
  ElMessage.info('模拟测试功能开发中...')
  //router.push('/mock-test')
}

const viewHistory = () => {
  router.push('/profile')
}

const goHome = () => {
  router.push('/dashboard')
}
</script>

<style scoped>
.exam-center-page {
  min-height: 100vh;
  background: #d9f4e6;
}

.header {
  height: 80px;
  background: linear-gradient(135deg, #8DC149, #7ab838);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
  box-shadow: 0 4px 20px rgba(141, 193, 73, 0.3);
  position: sticky;
  top: 0;
  z-index: 100;
  min-width: 900px;
  white-space: nowrap;
}

.header-left {
  flex: 1;
  display: flex;
  align-items: center;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  color: white;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.back-btn:hover {
  opacity: 0.7;
  background: rgba(255, 255, 255, 0.1) !important;
}

.header-title {
  flex: 2;
  text-align: center;
}

.header-title h2 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 1px;
}

.header-right {
  flex: 1;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 16px;
  font-size: 15px;
  font-weight: 500;
}

.username {
  opacity: 0.95;
}

.logout-btn {
  color: white !important;
  font-weight: 500;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  opacity: 0.7;
  background: rgba(255, 255, 255, 0.1) !important;
}

.content {
  padding: 40px 24px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: calc(100vh - 80px);
  box-sizing: border-box;
}

.exam-container {
  max-width: 1200px;
  width: 100%;
}

.exam-title {
  text-align: center;
  margin-bottom: 50px;
}

.exam-title h1 {
  font-size: 42px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 16px 0;
  letter-spacing: 1px;
}

.exam-title p {
  font-size: 18px;
  color: #7f8c8d;
  margin: 0;
  line-height: 1.6;
}

.action-buttons {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
}

.action-card {
  width: 100%;
  min-height: 200px;
  height: auto;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: none !important;
  border-radius: 16px !important;
  background: linear-gradient(135deg, #f0f9f4, #e6f7ee);
  box-shadow: 0 4px 16px rgba(141, 193, 73, 0.2);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  overflow: hidden;
  position: relative;
  padding: 24px 16px;
  border: 1px solid rgba(141, 193, 73, 0.3);
  box-sizing: border-box;
}

.action-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #98FB98, #7ab838, #98FB98);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s ease;
}

.action-card::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(152, 251, 152, 0.1), rgba(152, 251, 152, 0));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.action-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 16px 40px rgba(152, 251, 152, 0.3);
}

.action-card:hover::before {
  transform: scaleX(1);
}

.action-card:hover::after {
  opacity: 1;
}

.card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 20px;
  text-align: center;
}

.action-icon {
  font-size: 32px;
  color: #228b22;
  background: rgba(152, 251, 152, 0.2);
  padding: 12px;
  border-radius: 50%;
  margin-bottom: 12px;
  transition: all 0.3s ease;
}

.action-card:hover .action-icon {
  background: rgba(152, 251, 152, 0.4);
  transform: scale(1.1) rotate(5deg);
  box-shadow: 0 4px 12px rgba(152, 251, 152, 0.4);
}

.card-content h3 {
  font-size: 24px;
  font-weight: 700;
  color: #228b22;
  margin: 0 0 12px 0;
  transition: color 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex-shrink: 0;
}

.card-content p {
  font-size: 14px;
  color: #669966;
  margin: 0;
  line-height: 1.6;
  transition: color 0.3s ease;
  flex-shrink: 0;
  max-width: 100%;
}

.action-card:hover .card-content h3,
.action-card:hover .card-content p {
  color: #32cd32;
}

@media (max-width: 768px) {
  .header {
    min-width: 100%;
    padding: 0 20px;
  }

  .action-buttons {
    grid-template-columns: 1fr;
  }

  .exam-title h1 {
    font-size: 32px;
  }
}
</style>
