<template>
  <div class="admin-container">
    <!-- 侧边栏 -->
    <div class="admin-sidebar">
      <div class="sidebar-header">
        <el-icon class="logo-icon"><Management /></el-icon>
        <h1 class="sidebar-title">管理员控制台</h1>
      </div>
      
      <div class="sidebar-menu">
        <div 
          class="menu-item" 
          :class="{ active: activeMenu === 'user' }"
          @click="activeMenu = 'user'; showUserManagement = true"
        >
          <el-icon class="menu-icon"><User /></el-icon>
          <span class="menu-text">用户管理</span>
        </div>
      </div>
      
      <div class="sidebar-footer">
        <div class="user-info" @click="showUserMenu = !showUserMenu">
          <el-avatar size="small" :src="userAvatar"></el-avatar>
          <span class="user-name">{{ userNickname }}</span>
          <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
        </div>
        <div v-if="showUserMenu" class="user-menu">
          <div class="menu-item" @click="logout">
            <el-icon class="menu-icon"><SwitchButton /></el-icon>
            <span class="menu-text">退出登录</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="admin-main">
      <!-- 顶部导航 -->
      <div class="admin-header">
        <h2 class="page-title">{{ pageTitle }}</h2>
      </div>

      <!-- 内容区域 -->
      <div class="admin-content">
        <!-- 用户管理模块 -->
        <el-card v-if="showUserManagement" class="user-management-card">
          <template #header>
            <div class="card-header">
              <span class="header-title">用户管理</span>
              <el-button type="primary" @click="openAddUserDialog">
                <el-icon><Plus /></el-icon>
                添加用户
              </el-button>
            </div>
          </template>

          <!-- 搜索和筛选 -->
          <div class="search-filter">
            <el-input
              v-model="searchQuery"
              placeholder="搜索用户"
              prefix-icon="Search"
              class="search-input"
            />
            <el-select v-model="roleFilter" placeholder="按角色筛选" class="filter-select">
              <el-option label="全部" value="" />
              <el-option label="管理员" value="管理员" />
              <el-option label="商铺开发" value="商铺开发" />
              <el-option label="品牌开发" value="品牌开发" />
              <el-option label="品牌选址" value="品牌选址" />
              <el-option label="上门服务" value="上门服务" />
              <el-option label="商铺招商" value="商铺招商" />
            </el-select>
          </div>

          <!-- 用户列表 -->
        <el-table 
          :data="filteredUsers" 
          style="width: 100%" 
          class="user-table"
          v-loading="loading"
          element-loading-text="加载中..."
          element-loading-spinner="el-icon-loading"
          element-loading-background="rgba(255, 255, 255, 0.8)"
        >
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="name" label="姓名" />
          <el-table-column prop="role" label="角色">
            <template #default="scope">
              <el-tag effect="light" :type="getRoleType(scope.row.role)">
                {{ scope.row.role || '未设置' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="createdAt" label="创建时间" />
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="scope">
              <el-button
                type="primary"
                size="small"
                @click="openEditUserDialog(scope.row)"
                class="action-btn edit-btn"
              >
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click="deleteUser(scope.row)"
                class="action-btn delete-btn"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

          <!-- 分页 -->
          <div class="pagination">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="users.length"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </el-card>
      </div>
    </div>

    <!-- 添加/编辑用户对话框 -->
    <el-dialog
      v-model="userDialogVisible"
      :title="isEditing ? '编辑用户' : '添加用户'"
      width="500px"
    >
      <el-form :model="userForm" :rules="userRules" ref="userFormRef" label-width="100px">
        <el-form-item label="用&nbsp;户&nbsp;名" prop="username">
          <el-input style="padding-right: 30px;" v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="姓&nbsp;&nbsp;&emsp;名" prop="name">
          <el-input style="padding-right: 30px;" v-model="userForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="密&nbsp;&nbsp;&emsp;码" prop="password">
          <el-input style="padding-right: 30px;" v-model="userForm.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="角&nbsp;&nbsp;&emsp;色" prop="role">
          <el-select style="padding-right: 30px;" v-model="userForm.role" placeholder="请选择角色">
            <el-option label="管理员" value="管理员" />
            <el-option label="商铺开发" value="商铺开发" />
            <el-option label="品牌开发" value="品牌开发" />
            <el-option label="品牌选址" value="品牌选址" />
            <el-option label="上门服务" value="上门服务" />
            <el-option label="商铺招商" value="商铺招商" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="userDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveUser">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import {
  User, Management, ArrowDown, SwitchButton,
  Plus, Search, Edit, Delete
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { getUserList, getNickname, createUser, updateUser, deleteUser as deleteUserApi } from '@/api/user'

const router = useRouter()

// 状态管理
const showUserManagement = ref(true)
const searchQuery = ref('')
const roleFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const userDialogVisible = ref(false)
const isEditing = ref(false)
const userFormRef = ref(null)
const activeMenu = ref('user')
const showUserMenu = ref(true)
const loading = ref(false)
const userNickname = ref('管理员')

// 用户数据
const users = ref([])

// 加载用户数据
const loadUsers = async () => {
  try {
    loading.value = true
    
    // 并行请求用户列表和用户昵称
    const [usersResponse, nicknameResponse] = await Promise.all([
      getUserList(),
      getNickname()
    ])
    
    // 处理用户列表
    if (usersResponse && usersResponse.users) {
      users.value = usersResponse.users
    }
    
    // 处理用户昵称
    if (nicknameResponse && nicknameResponse.nickname) {
      userNickname.value = nicknameResponse.nickname
    }
  } catch (error) {
    ElMessage.error('获取用户列表失败')
    console.error('获取用户列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 页面挂载时加载数据
onMounted(() => {
  // 检查是否有token
  const token = localStorage.getItem('token')
  if (!token) {
    // 没有token，跳转到登录页面
    router.push('/login')
    return
  }
  loadUsers()
})

// 表单数据
const userForm = reactive({
  id: '',
  username: '',
  name: '',
  password: '',
  role: ''
})

// 表单验证规则
const userRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  password: [{ required: false, message: '请输入密码', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

// 计算属性：过滤后的用户列表
const filteredUsers = computed(() => {
  let result = users.value
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(user => 
      user.username.toLowerCase().includes(query) || 
      user.name.toLowerCase().includes(query)
    )
  }
  
  // 角色过滤
  if (roleFilter.value) {
    result = result.filter(user => user.role === roleFilter.value)
  }
  
  // 分页
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return result.slice(start, end)
})

// 方法
const logout = () => {
  // 清除登录态
  localStorage.removeItem('token')
  localStorage.removeItem('userRole')
  ElMessage.success('已退出登录')
  // 跳转到登录页
  router.push('/login')
}

const openAddUserDialog = () => {
  isEditing.value = false
  Object.assign(userForm, {
    id: '',
    username: '',
    name: '',
    password: '',
    role: ''
  })
  userDialogVisible.value = true
}

const openEditUserDialog = (user) => {
  isEditing.value = true
  Object.assign(userForm, {
    id: user.id,
    username: user.username,
    name: user.name,
    password: '',
    role: user.role
  })
  userDialogVisible.value = true
}

const saveUser = async () => {
  if (!userFormRef.value) return
  
  try {
    await userFormRef.value.validate()
    
    if (isEditing.value) {
      // 编辑用户
      const response = await updateUser(userForm)
      if (response && response.success) {
        const index = users.value.findIndex(u => u.id === userForm.id)
        if (index !== -1) {
          users.value[index] = {
            ...users.value[index],
            username: userForm.username,
            name: userForm.name,
            role: userForm.role
          }
        }
        ElMessage.success('用户编辑成功')
      } else {
        ElMessage.error('用户编辑失败')
      }
    } else {
      // 添加用户
      const response = await createUser(userForm)
      if (response && response.success) {
        // 重新加载用户列表
        await loadUsers()
        ElMessage.success('用户添加成功')
      } else {
        ElMessage.error('用户添加失败')
      }
    }
    
    userDialogVisible.value = false
  } catch (error) {
    console.error('保存用户失败:', error)
    ElMessage.error('保存用户失败')
  }
}

const deleteUser = (user) => {
  ElMessageBox.confirm(
    `确定要删除用户 ${user.name} 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await deleteUserApi(user.id)
      if (response && response.success) {
        const index = users.value.findIndex(u => u.id === user.id)
        if (index !== -1) {
          users.value.splice(index, 1)
        }
        ElMessage.success('用户删除成功')
      } else {
        ElMessage.error('用户删除失败')
      }
    } catch (error) {
      console.error('删除用户失败:', error)
      ElMessage.error('删除用户失败')
    }
  }).catch(() => {
    // 用户取消删除
  })
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (current) => {
  currentPage.value = current
}

// 计算属性：用户头像
const userAvatar = computed(() => {
  return `https://ui-avatars.com/api/?name=Admin&background=2e8b57&color=fff`
})

// 计算属性：页面标题
const pageTitle = computed(() => {
  switch (activeMenu.value) {
    case 'user':
      return '用户管理'
    default:
      return '管理员控制台'
  }
})

// 获取角色标签类型
const getRoleType = (role) => {
  if (!role) return 'info'
  if (role === '管理员') return 'info'
  if (role === '商铺开发') return 'custom'
  if (role === '品牌开发') return 'warning'
  if (role === '品牌选址') return 'danger'
  if (role === '上门服务') return 'primary'
  if (role === '商铺招商') return 'success'
  return 'warning'
}
</script>

<style scoped>
.admin-container {
  width: 100vw;
  min-height: 100vh;
  display: flex;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  font-family: 'PingFang SC', 'Helvetica Neue', STHeiti, 'Microsoft Yahei', sans-serif;
}

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

/* 主内容区域 */
.admin-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.admin-header {
  background: #ffffff;
  border-bottom: 1px solid #e8eef3;
  padding: 0 30px;
  display: flex;
  align-items: center;
  height: 70px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.admin-content {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
}

/* 用户管理卡片 */
.user-management-card {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 60px;
  border-bottom: 1px solid #f0f0f0;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

/* 搜索和筛选 */
.search-filter {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  align-items: center;
}

.search-input {
  width: 300px;
}

.filter-select {
  width: 150px;
}

/* 用户表格 */
.user-table {
  margin-bottom: 24px;
  border-radius: 8px;
  overflow: hidden;
  min-height: 350px;
  height: auto;
}

/* 表格样式美化 */
:deep(.user-table th) {
  background-color: #e6f7ee !important;
  font-weight: 600 !important;
  color: #2e8b57 !important;
  border-bottom: 2px solid #8DC149 !important;
}

/* 奇数行 */
:deep(.user-table tr:nth-child(odd) td) {
  vertical-align: middle !important;
  background-color: #ffffff !important;
  border-bottom: 1px solid #f0f0f0 !important;
}

/* 偶数行 */
:deep(.user-table tr:nth-child(even) td) {
  vertical-align: middle !important;
  background-color: #f9fff5 !important;
  border-bottom: 1px solid #f0f0f0 !important;
}

/* 悬停效果 */
:deep(.user-table tr:hover td) {
  background-color: #e6f7ee !important;
}

.action-btn {
  margin-right: 8px;
}

.edit-btn {
  background-color: #409eff;
  border-color: #409eff;
}

.edit-btn:hover {
  background-color: #66b1ff;
  border-color: #66b1ff;
}

.delete-btn {
  background-color: #f56c6c;
  border-color: #f56c6c;
}

.delete-btn:hover {
  background-color: #f78989;
  border-color: #f78989;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-sidebar {
    width: 200px;
  }
  
  .sidebar-title {
    font-size: 16px;
  }
  
  .admin-header {
    padding: 0 20px;
  }
  
  .admin-content {
    padding: 20px;
  }
  
  .search-filter {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-input,
  .filter-select {
    width: 100%;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    padding: 16px 24px;
    height: auto;
    gap: 12px;
  }
}

/* 按钮样式 */
.el-button--primary {
  background-color: #2e8b57;
  border-color: #2e8b57;
}

.el-button--primary:hover {
  background-color: #3cb371;
  border-color: #3cb371;
}

/* 对话框样式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* 标签样式 */
.el-tag--primary {
  background-color: #409eff;
  border-color: #409eff;
  color: white;
}

.el-tag--success {
  background-color: #67c23a;
  border-color: #67c23a;
  color: white;
}

/* 标签样式 */
:deep(.el-tag--light.el-tag--success) {
  background-color: #f0f9eb !important;
  border-color: #e6f7ee !important;
  color: #67c23a !important;
}

:deep(.el-tag--light.el-tag--warning) {
  background-color: #fdf6ec !important;
  border-color: #faecd8 !important;
  color: #e6a23c !important;
}

:deep(.el-tag--light.el-tag--danger) {
  background-color: #fef0f0 !important;
  border-color: #fde2e2 !important;
  color: #f56c6c !important;
}

:deep(.el-tag--light.el-tag--info) {
  background-color: #ecf5ff !important;
  border-color: #ebeef5 !important;
  color: #909399 !important;
}

:deep(.el-tag--light.el-tag--primary) {
  background-color: #ecf5ff !important;
  border-color: #ebeef5 !important;
  color: #409eff !important;
}

:deep(.el-tag--light.el-tag--dark) {
  background-color: #f4f4f5 !important;
  border-color: #e9e9eb !important;
  color: #606266 !important;
}

:deep(.el-tag--light.el-tag--custom) {
  background-color: #f0f5ff !important;
  border-color: #e6efff !important;
  color: #667cff !important;
}
</style>