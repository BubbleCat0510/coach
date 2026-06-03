<template>
  <div class="user-management-page">
    <!-- 用户表格 -->
    <el-card class="user-management-card" shadow="hover" style="height: 100%">
      <template #header>
        <div class="card-header">
          <span>用户列表</span>
          <div class="header-actions">
            <el-input
              v-model="searchQuery"
              placeholder="搜索用户"
              clearable
              style="width: 300px;"
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon class="el-input__icon"><Search /></el-icon>
              </template>
            </el-input>
            <el-button 
              type="primary" 
              @click="handleAdd"
              style="margin-left: 10px;"
            >
              <el-icon><Plus /></el-icon>
              添加用户
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table
        :data="userList"
        style="width: 100%; height: 88%;"
        border
        stripe
        v-loading="loading"
        element-loading-text="加载中..."
        element-loading-spinner="el-icon-loading"
        element-loading-background="rgba(255, 255, 255, 0.8)"
      >
        <el-table-column prop="id" label="ID" width="80" align="center" header-align="center"></el-table-column>
        <el-table-column prop="username" label="用户名" align="center" header-align="center"></el-table-column>
        <el-table-column prop="name" label="姓名" align="center" header-align="center"></el-table-column>
        <el-table-column prop="role" label="角色" align="center" header-align="center">
          <template #default="scope">
            <el-tag effect="light" :type="getRoleType(scope.row.role)">
              {{ getRoleName(scope.row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" align="center" header-align="center"></el-table-column>
        <el-table-column label="操作" width="180" align="center" header-align="center">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              @click="handleEdit(scope.row)"
              style="margin-right: 5px;"
            >
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleDelete(scope.row)"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 添加用户对话框 -->
    <el-dialog
      v-model="addDialogVisible"
      title="添加用户"
      width="500px"
    >
      <el-form
        :model="addForm"
        label-width="100px"
        :rules="addRules"
        ref="addFormRef"
      >
        <el-form-item label="用&nbsp;户&nbsp;名" prop="username">
          <el-input v-model="addForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="姓&nbsp;&nbsp;&emsp;名" prop="name">
          <el-input v-model="addForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="密&nbsp;&nbsp;&emsp;码" prop="password">
          <el-input v-model="addForm.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="角&nbsp;&nbsp;&emsp;色" prop="role">
          <el-select v-model="addForm.role" placeholder="请选择角色">
            <el-option label="管理员" :value="0" />
            <el-option label="商铺开发" :value="1" />
            <el-option label="上门服务" :value="2" />
            <el-option label="品牌开发" :value="3" />
            <el-option label="商铺招商" :value="4" />
            <el-option label="品牌选址" :value="5" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleAddSubmit">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑用户对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑用户"
      width="500px"
    >
      <el-form
        :model="editForm"
        label-width="100px"
        :rules="editRules"
        ref="editFormRef"
      >
        <el-form-item label="用&nbsp;户&nbsp;名" prop="username">
          <el-input v-model="editForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="姓&nbsp;&nbsp;&emsp;名" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="角&nbsp;&nbsp;&emsp;色" prop="role">
          <el-select v-model="editForm.role" placeholder="请选择角色">
            <el-option label="管理员" :value="0" />
            <el-option label="商铺开发" :value="1" />
            <el-option label="上门服务" :value="2" />
            <el-option label="品牌开发" :value="3" />
            <el-option label="商铺招商" :value="4" />
            <el-option label="品牌选址" :value="5" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleEditSubmit">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, Plus, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUserList, createUser, updateUser, deleteUser as deleteUserApi } from '@/api/user'

// 状态管理
const userList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchQuery = ref('')
const addDialogVisible = ref(false)
const editDialogVisible = ref(false)
const addFormRef = ref(null)
const editFormRef = ref(null)
const loading = ref(false)

// 添加用户表单数据
const addForm = reactive({
  username: '',
  name: '',
  password: '',
  role: ''
})

// 编辑用户表单数据
const editForm = reactive({
  id: '',
  username: '',
  name: '',
  role: ''
})

// 添加用户表单验证规则
const addRules = reactive({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
})

// 编辑用户表单验证规则
const editRules = reactive({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
})

// 方法
const getUsers = async () => {
  try {
    loading.value = true
    const response = await getUserList()
    if (response && response.users) {
      userList.value = response.users
      total.value = response.users.length
    } else {
      ElMessage.error('获取用户列表失败')
    }
  } catch (error) {
    console.error('获取用户列表错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  // 简单的前端搜索
  // 实际项目中应该调用后端API进行搜索
  currentPage.value = 1
  getUsers()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (current) => {
  currentPage.value = current
}

const handleAdd = () => {
  addForm.username = ''
  addForm.name = ''
  addForm.password = ''
  addForm.role = ''
  if (addFormRef.value) {
    addFormRef.value.resetFields()
  }
  addDialogVisible.value = true
}

const handleEdit = (row) => {
  editForm.id = row.id
  editForm.username = row.username
  editForm.name = row.name
  editForm.role = row.role
  if (editFormRef.value) {
    editFormRef.value.resetFields()
  }
  editDialogVisible.value = true
}

const handleAddSubmit = async () => {
  if (!addFormRef.value) return
  
  try {
    await addFormRef.value.validate()
    
    const response = await createUser(addForm)
    if (response && response.success) {
      await getUsers()
      addDialogVisible.value = false
      ElMessage.success('用户添加成功')
    } else {
      ElMessage.error('用户添加失败')
    }
  } catch (error) {
    console.error('添加用户失败:', error)
    ElMessage.error('添加用户失败')
  }
}

const handleEditSubmit = async () => {
  if (!editFormRef.value) return
  
  try {
    await editFormRef.value.validate()
    
    const response = await updateUser(editForm)
    if (response && response.success) {
      const index = userList.value.findIndex(u => u.id === editForm.id)
      if (index !== -1) {
        userList.value[index] = {
          ...userList.value[index],
          username: editForm.username,
          name: editForm.name,
          role: editForm.role
        }
      }
      editDialogVisible.value = false
      ElMessage.success('用户编辑成功')
    } else {
      ElMessage.error('用户编辑失败')
    }
  } catch (error) {
    console.error('编辑用户失败:', error)
    ElMessage.error('编辑用户失败')
  }
}

const handleDelete = (user) => {
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
        const index = userList.value.findIndex(u => u.id === user.id)
        if (index !== -1) {
          userList.value.splice(index, 1)
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
    // 取消删除
  })
}

const roleMap = {
  0: '管理员',
  1: '商铺开发',
  2: '上门服务',
  3: '品牌开发',
  4: '商铺招商',
  5: '品牌选址'
}

const getRoleName = (role) => {
  // 处理字符串类型的数字（如 "0", "1" 等）
  const roleNum = typeof role === 'string' ? parseInt(role, 10) : role
  return roleMap[roleNum] || '未设置'
}

const getRoleType = (role) => {
  if (!role && role !== 0) return 'info'
  if (role === 0 || role === '管理员') return 'info'
  if (role === 1 || role === '商铺开发') return 'primary'
  if (role === 2 || role === '上门服务') return 'success'
  if (role === 3 || role === '品牌开发') return 'warning'
  if (role === 4 || role === '商铺招商') return 'info'
  if (role === 5 || role === '品牌选址') return 'danger'
  return 'warning'
}

// 生命周期
onMounted(() => {
  getUsers()
})
</script>

<style scoped>
.user-management-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>