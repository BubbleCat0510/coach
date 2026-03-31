<template>
  <!-- 整个 Dashboard 页面 -->
  <div class="dashboard-page">
    <!-- 顶部标题栏 -->
    <div class="header">
      <!-- 左侧标题 -->
      <div class="title"><h2>AI 冠军教练 · 员工工作台</h2></div>

      <!-- 右侧用户信息 -->
      <div class="user-info">
        <span>欢迎你，{{ username }}</span>
        <el-button type="text" @click="logout">退出登录</el-button>
      </div>
    </div>

    <!-- 主体内容区域 -->
    <div class="content">
      <!-- 功能卡片 -->
       <el-card class="card">
        <h3>📚 学习中心</h3>
        <p>浏览学习资料，提升专业知识储备</p>
      </el-card>

      <el-card class="card" @click="goTrain">
        <h3>🎯 开始训练</h3>
        <p>进入 AI 冠军教练训练模式</p>
      </el-card>

      <el-card class="card" @click="goExam">
        <h3>🧪 AI 测试中心</h3>
        <p>测试 AI 教练的各项能力指标</p>
      </el-card>

      <el-card class="card">
        <h3>📊 我的成绩</h3>
        <p>查看历史训练评分与进步曲线</p>
      </el-card>
    </div>
  </div>
</template>

<script setup>
// Vue 组合式 API
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getNickname } from '../api/user'

// 路由实例
const router = useRouter()

// 当前登录用户名
const username = ref('')

// 异步逻辑必须放在 onMounted 等 async 函数内，用 ref 响应式变量存用户名；
// 页面加载时获取用户信息
onMounted(async () => {
  const res = await getNickname()
  username.value = res.nickname // 把接口返回值赋值给响应式变量
})


// 退出登录
const logout = () => {
  // 清 token
  localStorage.removeItem('token')
  router.push('/login')
}

// 跳转训练页面
const goTrain = () => {
  router.push('./train')
}

// 跳转AI测试页面
const goExam = () => {
  router.push('./ai-test')
}
</script>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  background: #e8e8e8;
}

/* 顶部栏 */
.header {
  height: 80px;
  background: linear-gradient(135deg, #90EE90, #98FB98);
  color: #2e8b57;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
  box-shadow: 0 4px 20px rgba(144, 238, 144, 0.3);
  position: sticky;
  top: 0;
  z-index: 100;
  min-width: 900px;
  white-space: nowrap;
}

.header h2 {
  font-size: 28px;
  font-weight: 700;
  margin: 0;
  letter-spacing: 1px;
}
.title {
  display: flex;
  width: 350px;
  height: 40px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 15px;
  font-weight: 500;
}

.user-info span {
  opacity: 0.95;
}

.user-info :deep(.el-button) {
  color: #2e8b57 !important;
  font-weight: 500;
  transition: all 0.3s ease;
}

.user-info :deep(.el-button:hover) {
  opacity: 0.7;
  background: rgba(46, 139, 87, 0.1) !important;
}

/* 内容区域 */
.content {
  padding: 50px 40px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 30px;
  max-width: 1400px;
  margin: 0 auto;
}

/* 功能卡片 */
.card {
  width: 100%;
  min-height: 200px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: none !important;
  border-radius: 16px !important;
  background: white;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  overflow: hidden;
  position: relative;
}

.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #8DC149, #7ab838);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s ease;
}

.card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 32px rgba(141, 193, 73, 0.2);
}

.card:hover::before {
  transform: scaleX(1);
}

.card h3 {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 12px 0;
  color: #2c3e50;
  transition: color 0.3s ease;
}

.card:hover h3 {
  color: #8DC149;
}

.card p {
  font-size: 14px;
  color: #7f8c8d;
  margin: 0;
  line-height: 1.6;
  transition: color 0.3s ease;
}

.card:hover p {
  color: #5a6c7d;
}
</style>
