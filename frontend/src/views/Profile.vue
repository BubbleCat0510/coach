<template>
  <!-- 整个个人中心页面 -->
  <div class="profile-page">
    <!-- 顶部标题栏 -->
    <div class="header">
      <!-- 左侧标题 -->
      <div class="title"><h2>AI 冠军教练 · 个人中心</h2></div>

      <!-- 右侧用户信息 -->
      <div class="user-info">
        <span>欢迎你，{{ userInfo.name }}</span>
        <el-button link @click="logout">退出登录</el-button>
      </div>
    </div>

    <!-- 主体内容区域 -->
    <div class="content">
      <!-- 个人信息卡片 -->
      <el-card class="profile-card">
        <template #header>
          <div class="card-header">
            <span class="header-title">个人信息</span>
            <el-button type="primary" size="small" @click="editProfile">
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
              <h3>{{ userInfo.name }}</h3>
              <p class="user-role">{{ userInfo.role || '未设置' }}</p>
            </div>
          </div>
          
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">用户名</span>
              <span class="info-value">{{ userInfo.username }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">姓名</span>
              <span class="info-value">{{ userInfo.name }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">角色</span>
              <span class="info-value">{{ userInfo.role || '未设置' }}</span>
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
            <span class="header-title">学习记录</span>
          </div>
        </template>
        
        <div class="record-list">
          <el-table :data="learningRecords" style="width: 100%">
            <el-table-column prop="date" label="日期" width="180" />
            <el-table-column prop="type" label="类型" width="120" />
            <el-table-column prop="content" label="内容" />
            <el-table-column prop="duration" label="时长" width="100" />
          </el-table>
        </div>
      </el-card>

      <!-- 考试记录卡片 -->
      <el-card class="exam-card">
        <template #header>
          <div class="card-header">
            <span class="header-title">考试记录</span>
          </div>
        </template>
        
        <div class="exam-list">
          <el-table :data="examRecords" style="width: 100%">
            <el-table-column prop="date" label="日期" width="180" />
            <el-table-column prop="type" label="类型" width="120" />
            <el-table-column prop="score" label="得分" width="100" />
            <el-table-column prop="result" label="结果" width="100" />
          </el-table>
        </div>
      </el-card>
    </div>

    <!-- 编辑个人信息弹窗 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑个人信息"
      width="400px"
    >
      <el-form :model="editForm" ref="editFormRef" label-width="80px">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="editForm.role" placeholder="请选择角色">
            <el-option label="商铺开发" value="商铺开发" />
            <el-option label="品牌开发" value="品牌开发" />
            <el-option label="品牌选址" value="品牌选址" />
            <el-option label="上门服务" value="上门服务" />
            <el-option label="商铺招商" value="商铺招商" />
          </el-select>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="editForm.password" type="password" placeholder="请输入新密码（不修改请留空）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" @click="saveProfile">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
// Vue 组合式 API
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getNickname, getUserRole, updateUser } from '../api/user'
import { ElMessage } from 'element-plus'
import { UserFilled, Edit } from '@element-plus/icons-vue'

// 路由实例
const router = useRouter()

// 用户信息
const userInfo = ref({
  username: '',
  name: '',
  role: '',
  createdAt: ''
})

// 编辑表单
const editForm = ref({
  name: '',
  role: '',
  password: ''
})

const editFormRef = ref(null)
const showEditDialog = ref(false)

// 学习记录
const learningRecords = ref([
  { date: '2026-04-08', type: '学习', content: '品牌开发基础知识', duration: '45分钟' },
  { date: '2026-04-07', type: '训练', content: 'AI教练对话训练', duration: '60分钟' },
  { date: '2026-04-06', type: '学习', content: '商铺选址技巧', duration: '30分钟' }
])

// 考试记录
const examRecords = ref([
  { date: '2026-04-05', type: '专项测试', score: '85', result: '优秀' },
  { date: '2026-04-01', type: '综合测试', score: '78', result: '良好' }
])

// 页面加载时获取用户信息
onMounted(async () => {
  try {
    // 获取用户昵称
    const nicknameRes = await getNickname()
    userInfo.value.name = nicknameRes.nickname
    userInfo.value.username = nicknameRes.username || '未知'
    
    // 获取用户角色
    const roleRes = await getUserRole()
    userInfo.value.role = roleRes.role
    
    // 模拟获取创建时间
    userInfo.value.createdAt = '2026-04-01 10:00:00'
  } catch (error) {
    console.error('获取用户信息失败:', error)
    ElMessage.error('获取用户信息失败')
  }
})

// 编辑个人信息
const editProfile = () => {
  // 填充编辑表单
  editForm.value = {
    name: userInfo.value.name,
    role: userInfo.value.role,
    password: ''
  }
  showEditDialog.value = true
}

// 保存个人信息
const saveProfile = async () => {
  try {
    // 调用API更新用户信息
    await updateUser({
      name: editForm.value.name,
      role: editForm.value.role,
      password: editForm.value.password
    })
    
    // 更新本地用户信息
    userInfo.value.name = editForm.value.name
    userInfo.value.role = editForm.value.role
    
    ElMessage.success('个人信息更新成功')
    showEditDialog.value = false
  } catch (error) {
    console.error('更新个人信息失败:', error)
    ElMessage.error('更新个人信息失败')
  }
}

// 退出登录
const logout = () => {
  // 清 token
  localStorage.removeItem('token')
  router.push('/login')
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
</style>