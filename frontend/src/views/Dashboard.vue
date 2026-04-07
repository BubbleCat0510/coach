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
    <div class="content">
      <!-- 功能卡片 -->
       <el-card class="card" @click="goTraining">
        <h3>📚 学习中心</h3>
        <p>浏览学习资料，提升专业知识储备</p>
      </el-card>

      <el-card class="card" @click="goTrain">
        <h3>🎯 开始训练</h3>
        <p>进入 AI 冠军教练训练模式</p>
      </el-card>

      <el-card class="card" @click="goExam">
        <h3>🧪 评估中心</h3>
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
              <el-option label="商铺开发" value="商铺开发" />
              <el-option label="品牌开发" value="品牌开发" />
              <el-option label="品牌选址" value="品牌选址" />
              <el-option label="上门服务" value="上门服务" />
              <el-option label="商铺招商" value="商铺招商" />
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
import { getNickname, getUserRole, updateRole } from '../api/user'
import { ElMessage } from 'element-plus'
import { UserFilled } from '@element-plus/icons-vue'

// 路由实例
const router = useRouter()

// 当前登录用户名
const username = ref('')
// 角色选择弹窗
const showRoleDialog = ref(false)
// 角色表单
const roleForm = ref({ role: '' })
const roleFormRef = ref(null)

// 异步逻辑必须放在 onMounted 等 async 函数内，用 ref 响应式变量存用户名；
// 页面加载时获取用户信息
onMounted(async () => {
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
    
    // 如果角色为空、空字符串或null，显示角色选择弹窗
    if (!userRole || (typeof userRole === 'string' && userRole.trim() === '')) {
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

// 跳转培训内容页面
const goTraining = () => {
  router.push('./training')
}

// 跳转个人中心页面
const goProfile = () => {
  // 这里可以添加个人中心页面的路由跳转
  // 暂时先弹出提示
  ElMessage.info('个人中心功能开发中')
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
  display: flex;
  align-items: center;
  gap: 8px;
}

.card h3 .el-icon {
  font-size: 24px;
  vertical-align: middle;
  margin-top: -2px;
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
