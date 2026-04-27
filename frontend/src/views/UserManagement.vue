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
              @click="dialogVisible = true"
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
              {{ scope.row.role || '未设置' }}
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

    <!-- 新增/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑用户' : '添加用户'"
      width="500px"
    >
      <el-form
        :model="form"
        label-width="100px"
        :rules="rules"
        ref="formRef"
      >
        <el-form-item label="用&nbsp;户&nbsp;名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="姓&nbsp;&nbsp;&emsp;名" prop="name">
          <el-input v-model="form.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="密&nbsp;&nbsp;&emsp;码" prop="password" v-if="!isEditing">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="角&nbsp;&nbsp;&emsp;色" prop="role">
          <el-select v-model="form.role" placeholder="请选择角色">
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
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">保存</el-button>
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
const dialogVisible = ref(false)
const isEditing = ref(false)
const formRef = ref(null)
const loading = ref(false)

// 表单数据
const form = reactive({
  id: '',
  username: '',
  name: '',
  password: '',
  role: ''
})

// 表单验证规则
const rules = reactive({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  password: [{ required: false, message: '请输入密码', trigger: 'blur' }],
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

const handleEdit = (row) => {
  isEditing.value = true
  form.id = row.id
  form.username = row.username
  form.name = row.name
  form.role = row.role
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    if (isEditing.value) {
      // 编辑用户
      const response = await updateUser(form)
      if (response && response.success) {
        const index = userList.value.findIndex(u => u.id === form.id)
        if (index !== -1) {
          userList.value[index] = {
            ...userList.value[index],
            username: form.username,
            name: form.name,
            role: form.role
          }
        }
        ElMessage.success('用户编辑成功')
      } else {
        ElMessage.error('用户编辑失败')
      }
    } else {
      // 添加用户
      const response = await createUser(form)
      if (response && response.success) {
        // 重新加载用户列表
        await getUsers()
        ElMessage.success('用户添加成功')
      } else {
        ElMessage.error('用户添加失败')
      }
    }
    
    dialogVisible.value = false
  } catch (error) {
    console.error('保存用户失败:', error)
    ElMessage.error('保存用户失败')
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

const getRoleType = (role) => {
  if (!role) return 'info'
  if (role === '管理员') return 'info'
  if (role === '商铺开发') return 'primary'
  if (role === '品牌开发') return 'warning'
  if (role === '品牌选址') return 'danger'
  if (role === '上门服务') return 'success'
  if (role === '商铺招商') return 'info'
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