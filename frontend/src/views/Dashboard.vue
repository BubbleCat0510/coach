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
        <el-button link @click="logout">退出登录</el-button>
      </div>
    </div>

    <!-- 主体内容区域 -->
    <div class="welcome-section">
      <div class="welcome-text">
        <h1>欢迎回来，{{ username }}！</h1>
        <p>今天你想进行什么训练？</p>
      </div>
      <div class="date-time">
        <p class="current-date">{{ currentDate }}</p>
        <p class="current-time">{{ currentTime }}</p>
      </div>
    </div>
    <div class="content">
      <!-- 功能卡片 -->
       <el-card class="card" @click="goTraining">
        <h3><el-icon><Reading /></el-icon> 学习中心</h3>
        <p>浏览学习资料，提升专业知识储备</p>
      </el-card>

      <el-card class="card" @click="goTrain">
        <h3><el-icon><Aim /></el-icon> 开始训练</h3>
        <p>进入 AI 冠军教练训练模式</p>
      </el-card>

      <el-card class="card" @click="goExam">
        <h3><el-icon><Histogram /></el-icon> 评估中心</h3>
        <p>AI评估的各项能力指标</p>
      </el-card>

      <el-card class="card" @click="goProfile">
        <h3><el-icon><UserFilled /></el-icon> 个人中心</h3>
        <p>查看个人信息与历史记录</p>
      </el-card>
    </div>

    <!-- 角色选择弹窗 -->
    <el-dialog
      v-model="showRoleDialog"
      title="选择角色"
      width="400px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
      custom-class="role-select-dialog"
    >
      <div class="role-select-content">
        <div class="role-select-header">
          <el-icon class="header-icon"><UserFilled /></el-icon>
          <h3>请选择您的角色</h3>
          <p class="role-select-desc">选择一个角色以开始使用系统</p>
        </div>
        <el-form :model="roleForm" ref="roleFormRef" label-width="0">
          <el-form-item prop="role" class="role-select-item">
            <el-select v-model="roleForm.role" placeholder="请选择角色" style="width: 150px;" size="large" :popper-width="300">
              <el-option label="商铺开发" :value="1" />
              <el-option label="上门服务" :value="2" />
              <el-option label="品牌开发" :value="3" />
              <el-option label="商铺招商" :value="4" />
              <el-option label="品牌选址" :value="5" />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" size="large" @click="saveRole" class="save-role-btn">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
// Vue 组合式 API
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getNickname, getUserRole, updateRole, logoutApi } from '../api/user'
import { ElMessage } from 'element-plus'
import { UserFilled, Reading, Aim, Histogram } from '@element-plus/icons-vue'

// 路由实例
const router = useRouter()

// 当前登录用户名
const username = ref('')
// 当前日期
const currentDate = ref('')
// 当前时间（周几和实时时间）
const currentTime = ref('')
// 角色选择弹窗
const showRoleDialog = ref(false)
// 角色表单
const roleForm = ref({ role: '' })
const roleFormRef = ref(null)

// 更新当前日期时间
const updateDateTime = () => {
  const now = new Date()
  
  // 日期选项
  const dateOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }
  
  // 时间选项
  const timeOptions = {
    weekday: 'long',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  }
  
  // 格式化日期并添加空格
  let dateStr = now.toLocaleDateString('zh-CN', dateOptions)
  dateStr = dateStr.replace(/(\d+)(年|月|日)/g, ' $1 $2')
  currentDate.value = dateStr
  
  // 格式化时间并添加空格
  let timeStr = now.toLocaleDateString('zh-CN', timeOptions)
  timeStr = timeStr.replace(/(\d+):(\d+):(\d+)/g, ' $1 : $2 : $3 ')
  currentTime.value = timeStr
}

// 初始化日期时间并设置定时器
const initDateTime = () => {
  updateDateTime()
  setInterval(updateDateTime, 1000)
}

// 异步逻辑必须放在 onMounted 等 async 函数内，用 ref 响应式变量存用户名；
// 页面加载时获取用户信息
onMounted(async () => {
  // 初始化日期时间
  initDateTime()
  
  try {
    // 获取用户昵称
    const nicknameRes = await getNickname()
    username.value = nicknameRes.nickname // 把接口返回值赋值给响应式变量
    
    // 获取用户角色
    const roleRes = await getUserRole()
    const userRole = roleRes.role
    
    // 控制台输出角色数据
    console.log('用户角色数据:', roleRes)
    console.log('用户角色:', userRole)
    
    // 如果角色为空、空字符串、null或undefined，显示角色选择弹窗（0是有效的管理员角色）
    if (userRole === null || userRole === undefined || (typeof userRole === 'string' && userRole.trim() === '')) {
      showRoleDialog.value = true
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
    ElMessage.error('获取用户信息失败')
  }
})

// 保存角色
const saveRole = async () => {
  if (!roleForm.value.role) {
    ElMessage.warning('请选择角色')
    return
  }
  
  try {
    // 调用API保存角色
    await updateRole(roleForm.value.role)
    
    ElMessage.success('角色选择成功')
    showRoleDialog.value = false
    
    // 重新获取用户信息
    const roleRes = await getUserRole()
    console.log('更新后的角色:', roleRes.role)
  } catch (error) {
    console.error('保存角色失败:', error)
    ElMessage.error('保存角色失败')
  }
}

// 退出登录
const logout = async () => {
  try {
    await logoutApi()
  } catch (error) {
    console.error('登出接口失败', error)
  } finally {
    localStorage.removeItem('token')
    sessionStorage.clear()
    router.push('/login')
  }
}

// 跳转训练页面
const goTrain = () => {
  ElMessage.info('功能开发中...')
  //router.push('./train')
}

// // 跳转AI测试页面
// const goExam = () => {
//   router.push('./ai-test')
// }

// 跳转评估中心页面
const goExam = () => {
  router.push('/exam-center')
}

// 跳转培训内容页面
const goTraining = () => {
  router.push('./training')
}

// 跳转个人中心页面
const goProfile = () => {
  router.push('./profile')
}</script>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  background: #d9f4e6;
}

/* 顶部栏 */
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

/* 欢迎语区域 */
.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30px 40px;
  max-width: 1400px;
  margin: 30px auto 20px;
  flex-wrap: wrap;
  gap: 20px;
  background: linear-gradient(135deg, #f0f9f4, #e6f7ee);
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(141, 193, 73, 0.2);
  border: 1px solid rgba(141, 193, 73, 0.3);
  position: relative;
  overflow: hidden;
}

.welcome-section::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(152, 251, 152, 0.1) 0%, rgba(152, 251, 152, 0) 70%);
  animation: rotate 20s linear infinite;
}

@keyframes rotate {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 日期时间区域 */
.date-time {
  flex: 1;
  min-width: 300px;
  text-align: right;
}

.current-date {
  font-size: 20px;
  color: #7f8c8d;
  margin: 0 0 4px 0;
  line-height: 1.4;
  font-family: monospace;
  font-weight: 500;
  text-align: right;
}

.current-time {
  font-size: 18px;
  color: #7f8c8d;
  margin: 0;
  line-height: 1.4;
  font-family: monospace;
  font-weight: 500;
  text-align: right;
}

/* 欢迎语文本区域 */
.welcome-text {
  flex: 2;
  text-align: left;
  min-width: 300px;
}

.welcome-text h1 {
  font-size: 36px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 12px 0;
  letter-spacing: 1px;
}

.welcome-text p {
  font-size: 18px;
  color: #7f8c8d;
  margin: 0;
  line-height: 1.6;
}

/* 内容区域 */
.content {
  padding: 20px 40px 50px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 30px;
  max-width: 1400px;
  margin: 0 auto;
}

/* 功能卡片 */
.card {
  width: 100%;
  min-height: 220px;
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
  padding: 30px 20px;
  box-sizing: border-box;
  border: 1px solid rgba(141, 193, 73, 0.3);
}

.card::before {
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

.card::after {
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

.card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 16px 40px rgba(152, 251, 152, 0.3);
}

.card:hover::before {
  transform: scaleX(1);
}

.card:hover::after {
  opacity: 1;
}

.card h3 {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 12px 0;
  color: #228b22;
  transition: color 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex-shrink: 0;
}

.card h3 .el-icon {
  font-size: 32px;
  vertical-align: middle;
  margin-top: -2px;
  color: #32cd32;
  background: rgba(152, 251, 152, 0.2);
  padding: 12px;
  border-radius: 50%;
  margin-right: 12px;
  transition: all 0.3s ease;
}

.card:hover h3 .el-icon {
  background: rgba(152, 251, 152, 0.4);
  transform: scale(1.1) rotate(5deg);
  box-shadow: 0 4px 12px rgba(152, 251, 152, 0.4);
}

.card:hover h3 {
  color: #32cd32;
}

.card p {
  font-size: 14px;
  color: #669966;
  margin: 0;
  line-height: 1.6;
  transition: color 0.3s ease;
  flex-shrink: 0;
  max-width: 100%;
}

.card:hover p {
  color: #32cd32;
}
/* 角色选择弹窗样式 */
.role-select-dialog {
  .el-dialog__header {
    text-align: center;
    padding: 20px 20px 10px;
  }
  
  .el-dialog__title {
    font-size: 20px;
    font-weight: 600;
    color: #303133;
  }
  
  .el-dialog__body {
    padding: 20px;
  }
  
  .el-dialog__footer {
    padding: 10px 20px 20px;
    text-align: center;
  }
}

.role-select-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.role-select-header {
  text-align: center;
  margin-bottom: 24px;
  width: 100%;
}

.header-icon {
  font-size: 48px;
  color: #409EFF;
  margin-bottom: 16px;
}

.role-select-header h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.role-select-desc {
  margin: 0;
  font-size: 14px;
  color: #909399;
  line-height: 1.5;
}

.role-select-item {
  width: 100%;
  max-width: 300px;
  
  /* 让选择框内的内容居中显示 */
  :deep(.el-select .el-input__inner) {
    text-align: center;
  }
}

/* 让下拉菜单中的内容居中显示 */
.el-select-dropdown__item {
  text-align: center !important;
}

/* 确保选择框内的内容也居中显示 */
.el-select .el-input__inner {
  text-align: center !important;
}

.save-role-btn {
  width: 120px;
  font-size: 16px;
}

.dialog-footer {
  display: flex;
  justify-content: center;
  width: 100%;
}
</style>

