<template>
  <!-- 整个个人中心页面 -->
  <div class="profile-page">
    <!-- 顶部标题栏 -->
    <div class="header">
      <!-- 左侧返回按钮和标题 -->
      <div class="header-left">
        <el-button class="back-button" @click="goBack">
          <el-icon class="back-icon"><ArrowLeft /></el-icon>
        </el-button>
        <div class="title"><h2>AI 冠军教练 · 个人中心</h2></div>
      </div>

      <!-- 右侧用户信息 -->
      <div class="user-info">
        <span>欢迎你，{{ userInfo.nickname }}</span>
        <el-button class="logout-button" @click="logout">
          <el-icon class="logout-icon"><SwitchButton /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- 主体内容区域 -->
    <div class="content">
      <!-- 个人信息卡片 -->
      <el-card class="profile-card">
        <template #header>
          <div class="card-header">
            <span style="margin-left: 10px;" class="header-title">个人信息</span>
            <el-button class="edit-button" @click="editProfile">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
          </div>
        </template>
        
        <div class="profile-info">
          <div class="avatar-section">
            <div class="avatar">
              <el-icon class="avatar-icon"><UserFilled /></el-icon>
            </div>
            <div class="avatar-info">
              <h3>{{ userInfo.nickname }}</h3>
              <p class="user-role">{{ getRoleName(userInfo.role) }}</p>
            </div>
          </div>
          
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">用户名</span>
              <span class="info-value">{{ userInfo.username }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">昵称</span>
              <span class="info-value">{{ userInfo.nickname }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">角色</span>
              <span class="info-value">{{ getRoleName(userInfo.role) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">创建时间</span>
              <span class="info-value">{{ userInfo.createdAt || '未知' }}</span>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 学习记录卡片 -->
      <el-card class="record-card">
        <template #header>
          <div class="card-header">
            <span style="margin-left: 10px;" class="header-title">学习记录</span>
          </div>
        </template>
        
        <div class="record-list">
          <el-table :data="learningRecords" style="width: 100%" :fit="true">
            <el-table-column prop="date" label="日期" min-width="140" />
            <el-table-column prop="progress" label="学习进度" min-width="120">
              <template #default="scope">
                {{ scope.row.progress || 0 }}%
              </template>
            </el-table-column>
            <el-table-column prop="content" label="内容" min-width="380" />
            <el-table-column prop="duration" label="时长" min-width="100" />
          </el-table>
        </div>
      </el-card>

      <!-- 考试记录卡片 -->
      <el-card class="exam-card">
        <template #header>
          <div class="card-header">
            <span style="margin-left: 10px;" class="header-title">考试记录</span>
          </div>
        </template>
        
        <div class="exam-list">
          <el-table :data="examRecords" style="width: 100%" :fit="true" class="exam-table">
            <el-table-column prop="date" label="日期" text-align="center" />
            <el-table-column prop="type" label="类型" text-align="center" />
            <el-table-column prop="score" label="得分" text-align="center" />
            <el-table-column prop="result" label="结果" text-align="center" />
          </el-table>
        </div>
      </el-card>
    </div>

    <!-- 编辑个人信息弹窗 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑个人信息"
      width="480px"
      custom-class="profile-edit-dialog"
      :close-on-click-modal="false"
    >
      <div class="dialog-content">
        <div class="dialog-header">
          <el-icon class="header-icon"><UserFilled /></el-icon>
          <h3>更新您的个人信息</h3>
        </div>
        <el-form :model="editForm" ref="editFormRef" :rules="rules" label-width="100px" class="profile-form">
          <el-form-item label="昵&ensp;&ensp;&ensp;&ensp;称" prop="nickname" class="form-item">
            <el-input 
              v-model="editForm.nickname" 
              placeholder="请输入昵称" 
              class="form-input"

            />
          </el-form-item>
          <el-form-item label="角&ensp;&ensp;&ensp;&ensp;色" class="form-item">
            <el-input 
              v-model="editForm.role" 
              placeholder="角色" 
              disabled 
              class="form-input disabled-input"

            />
          </el-form-item>
          <el-form-item label="密&ensp;&ensp;&ensp;&ensp;码" prop="password" class="form-item">
            <el-input 
              v-model="editForm.password" 
              type="password" 
              placeholder="请输入新密码（不修改请留空）" 
              class="form-input"

            />
          </el-form-item>
          <el-form-item label="确认密码" prop="confirmPassword" class="form-item">
            <el-input 
              v-model="editForm.confirmPassword" 
              type="password" 
              placeholder="请确认新密码" 
              class="form-input"

            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button class="cancel-btn" @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" class="save-btn" @click="saveProfile">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
// Vue 组合式 API
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getProfile, updateUser, logoutApi } from '../api/user'
import { getMyLearningRecords } from '../api/upload'
import { ElMessage } from 'element-plus'
import { UserFilled, Edit, ArrowLeft, SwitchButton } from '@element-plus/icons-vue'

// 路由实例
const router = useRouter()

// 用户信息
const userInfo = ref({
  id: '',
  username: '',
  nickname: '',
  role: '',
  createdAt: ''
})

// 编辑表单
const editForm = ref({
  nickname: '',
  role: '',
  password: '',
  confirmPassword: ''
})

const editFormRef = ref(null)
const showEditDialog = ref(false)

// 验证密码
const validatePassword = (rule, value, callback) => {
  if (value && value.length < 6) {
    callback(new Error('密码长度不能少于6位'))
  } else {
    callback()
  }
}

// 验证确认密码
const validateConfirmPassword = (rule, value, callback) => {
  if (value && value !== editForm.value.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

// 表单验证规则
const rules = {
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  password: [{ validator: validatePassword, trigger: 'blur' }],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }]
}

// 学习记录
const learningRecords = ref([])

// 考试记录
const examRecords = ref([
  { date: '2026-04-05', type: '专项测试', score: '85', result: '优秀' },
  { date: '2026-04-01', type: '综合测试', score: '78', result: '良好' }
])

// 加载学习记录
const loadLearningRecords = async () => {
  try {
    const res = await getMyLearningRecords()
    if (res.success && res.records) {
      learningRecords.value = res.records
    }
  } catch (error) {
    console.error('获取学习记录失败:', error)
  }
}

// 页面加载时获取用户信息
onMounted(async () => {
  try {
    // 获取用户完整信息
    const profileRes = await getProfile()
    if (profileRes.user) {
      userInfo.value = {
        id: profileRes.user.id || '',
        username: profileRes.user.username || '未知',
        nickname: profileRes.user.name || '未知',
        role: profileRes.user.role !== null && profileRes.user.role !== undefined ? profileRes.user.role : '未设置',
        createdAt: profileRes.user.createdAt || '未知'
      }
    }
    // 加载学习记录
    await loadLearningRecords()
  } catch (error) {
    console.error('获取用户信息失败:', error)
    ElMessage.error('获取用户信息失败')
  }
})

// 编辑个人信息
const editProfile = () => {
  // 填充编辑表单
  editForm.value = {
    nickname: userInfo.value.nickname,
    role: userInfo.value.role,
    password: ''
  }
  showEditDialog.value = true
}

// 保存个人信息
const saveProfile = async () => {
  try {
    // 表单验证
    await editFormRef.value.validate()
    
    // 调用API更新用户信息（不包含角色）
    await updateUser({
      name: editForm.value.nickname,
      password: editForm.value.password
    })
    
    // 更新本地用户信息
    userInfo.value.nickname = editForm.value.nickname
    
    ElMessage.success('个人信息更新成功')
    showEditDialog.value = false
  } catch (error) {
    console.error('更新个人信息失败:', error)
    if (error.name === 'Error') {
      // 表单验证错误，由Element Plus自动处理
    } else {
      ElMessage.error('更新个人信息失败')
    }
  }
}

// 角色映射
const roleMap = {
  0: '管理员',
  1: '商铺开发',
  2: '品牌开发',
  3: '品牌选址',
  4: '上门服务',
  5: '商铺招商'
}

const getRoleName = (role) => {
  // 处理字符串类型的数字（如 "0", "1" 等）
  const roleNum = typeof role === 'string' ? parseInt(role, 10) : role
  return roleMap[roleNum] || '未设置'
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

// 返回上一页
const goBack = () => {
  router.back()
}
</script>

<style scoped>
.profile-page {
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

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header h2 {
  font-size: 28px;
  font-weight: 700;
  margin: 0;
  letter-spacing: 1px;
}

.title {
  display: flex;
  height: 40px;
}

.back-button {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  transition: all 0.3s ease;
  padding: 0;
}

.back-button:hover {
  background-color: rgba(255, 255, 255, 0.25);
  transform: translateX(-2px);
  box-shadow: 0 2px 8px rgba(255, 255, 255, 0.2);
  color: white;
  border-color: rgba(255, 255, 255, 0.5);
}

.back-icon {
  font-size: 18px;
}

/* 退出登录按钮样式 */
.logout-button {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  transition: all 0.3s ease;
  padding: 0;
}

.logout-button:hover {
  background-color: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(255, 255, 255, 0.2);
  color: white;
  border-color: rgba(255, 255, 255, 0.5);
}

.logout-icon {
  font-size: 18px;
}

/* 编辑按钮样式 */
.edit-button {
  background: linear-gradient(135deg, #8DC149, #7ab838);
  border: none;
  border-radius: 8px;
  padding: 6px 16px;
  font-size: 14px;
  font-weight: 500;
  color: white;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(141, 193, 73, 0.2);
}

.edit-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(141, 193, 73, 0.3);
  background: linear-gradient(135deg, #7ab838, #8DC149);
  color: white;
}

/* 考试表格样式 */
.exam-table :deep(.el-table__header-wrapper th) {
  text-align: center !important;
  border-right: 1px solid #e6f7ee !important;
}

.exam-table :deep(.el-table__body-wrapper td) {
  text-align: center !important;
  border-right: 1px solid #e6f7ee !important;
}

.exam-table :deep(.el-table__header-wrapper th:last-child) {
  border-right: none !important;
}

.exam-table :deep(.el-table__body-wrapper td:last-child) {
  border-right: none !important;
}

/* 学习记录表格样式 */
.record-list :deep(.el-table__header-wrapper th) {
  border-right: 1px solid #e6f7ee !important;
}

.record-list :deep(.el-table__body-wrapper td) {
  border-right: 1px solid #e6f7ee !important;
}

.record-list :deep(.el-table__header-wrapper th:last-child) {
  border-right: none !important;
}

.record-list :deep(.el-table__body-wrapper td:last-child) {
  border-right: none !important;
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
  padding: 30px 40px 50px;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 30px;
}

/* 卡片样式 */
.profile-card,
.record-card,
.exam-card {
  border-radius: 16px !important;
  box-shadow: 0 4px 16px rgba(141, 193, 73, 0.2) !important;
  border: 1px solid rgba(141, 193, 73, 0.3) !important;
  background: linear-gradient(135deg, #f0f9f4, #e6f7ee) !important;
  overflow: hidden;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

/* 个人信息区域 */
.profile-info {
  padding: 20px;
}

.avatar-section {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(141, 193, 73, 0.2);
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, #98FB98, #8DC149);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 30px;
  box-shadow: 0 4px 12px rgba(141, 193, 73, 0.3);
}

.avatar-icon {
  font-size: 48px;
  color: white;
}

.avatar-info h3 {
  font-size: 24px;
  font-weight: 700;
  color: #228b22;
  margin: 0 0 8px 0;
}

.user-role {
  font-size: 16px;
  color: #669966;
  margin: 0;
}

/* 信息网格 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 14px;
  color: #7f8c8d;
  font-weight: 500;
}

.info-value {
  font-size: 16px;
  color: #2c3e50;
  font-weight: 500;
}

/* 表格样式 */
.record-list,
.exam-list {
  padding: 10px 0;
}

:deep(.el-table) {
  border-radius: 8px !important;
  overflow: hidden;
}

:deep(.el-table th) {
  background-color: #e6f7ee !important;
  font-weight: 600 !important;
  color: #2e8b57 !important;
  border-bottom: 2px solid #8DC149 !important;
}

:deep(.el-table tr:nth-child(odd) td) {
  background-color: #ffffff !important;
}

:deep(.el-table tr:nth-child(even) td) {
  background-color: #f9fff5 !important;
}

:deep(.el-table tr:hover td) {
  background-color: #e6f7ee !important;
}

/* 编辑个人信息弹窗样式 */
.profile-edit-dialog {
  border-radius: 16px !important;
  overflow: hidden;
}

.profile-edit-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #8DC149, #7ab838);
  color: white;
  padding: 20px 24px;
  text-align: center;
}

.profile-edit-dialog :deep(.el-dialog__title) {
  font-size: 20px;
  font-weight: 600;
  color: white;
}

.profile-edit-dialog :deep(.el-dialog__body) {
  padding: 30px 24px;
  background: #f9fff5;
}

.profile-edit-dialog :deep(.el-dialog__footer) {
  padding: 20px 24px;
  background: #f9fff5;
  border-top: 1px solid rgba(141, 193, 73, 0.2);
}

/* 弹窗内容 */
.dialog-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.dialog-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(141, 193, 73, 0.2);
}

.header-icon {
  font-size: 48px;
  color: #8DC149;
}

.dialog-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

/* 表单样式 */
.profile-form {
  width: 100%;
}

.form-item {
  margin-bottom: 20px;
}

.form-input {
  border-radius: 8px !important;
  border: 1px solid rgba(141, 193, 73, 0.3) !important;
  transition: all 0.3s ease;
  margin-right: 20px;
}

.form-input:focus {
  border-color: #8DC149 !important;
  box-shadow: 0 0 0 2px rgba(141, 193, 73, 0.2) !important;
}

.disabled-input {
  background-color: #f0f9f4 !important;
  border-color: rgba(141, 193, 73, 0.2) !important;
  color: #669966 !important;
}

/* 按钮样式 */
.dialog-footer {
  display: flex;
  justify-content: center;
  gap: 16px;
  width: 100%;
}

.cancel-btn {
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
}

.save-btn {
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 16px;
  background: linear-gradient(135deg, #8DC149, #7ab838);
  border: none;
  transition: all 0.3s ease;
}

.save-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(141, 193, 73, 0.3);
}

/* 表单验证错误提示 */
.profile-edit-dialog :deep(.el-form-item__error) {
  color: #f56c6c;
  font-size: 12px;
  margin-top: 4px;
}
</style>