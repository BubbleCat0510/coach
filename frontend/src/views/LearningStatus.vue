<template>
  <div class="learning-status-page">
    <!-- 学习情况表格 -->
    <el-card class="learning-status-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>学习情况</span>
          <el-input
            v-model="searchQuery"
            placeholder="搜索用户或文件"
            clearable
            style="width: 300px;"
            @keyup.enter="handleSearch"
            @input="handleSearch"
            @clear="handleSearch"
          >
            <template #prefix>
              <el-icon class="el-input__icon"><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </template>
      
      <el-table
        :data="learningStatusList"
        :style="{ width: '100%', height: tableHeight + 'px' }"
        border
        stripe
      >
        <el-table-column prop="userId" label="用户ID" width="80" align="center" header-align="center"></el-table-column>
        <el-table-column prop="nickname" label="用户昵称" width="100" align="center" header-align="center"></el-table-column>
        <el-table-column prop="userRole" label="用户角色" width="120" align="center" header-align="center">
          <template #default="scope">
            <el-tag size="small" :type="getRoleTagType(scope.row.userRole)">{{ getRoleText(scope.row.userRole) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="fileId" label="文件ID" width="100" align="center" header-align="center"></el-table-column>
        <el-table-column prop="fileName" label="文件名称" min-width="300" align="center" header-align="center">
          <template #default="scope">
            <div class="file-name">
              {{ scope.row.fileName }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="学习进度" width="150" align="center" header-align="center">
          <template #default="scope">
            <el-progress 
              :percentage="scope.row.progress" 
              :color="getProgressColor(scope.row.progress)"
              :stroke-width="10"
            />
          </template>
        </el-table-column>
        <el-table-column prop="isCompleted" label="是否完成" width="120" align="center" header-align="center">
          <template #default="scope">
            <el-tag :type="scope.row.isCompleted ? 'success' : 'info'">
              {{ scope.row.isCompleted ? '已完成' : '未完成' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="learningTime" label="学习时长" width="120" align="center" header-align="center">
          <template #default="scope">
            {{ formatLearningTime(scope.row.learningTime) }}
          </template>
        </el-table-column>
        <el-table-column prop="lastReadTime" label="最后学习时间" width="200" align="center" header-align="center">
          <template #default="scope">
            {{ scope.row.lastReadTime }}
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
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getLearningStatus } from '@/api/upload'

// 状态管理
const learningStatusList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchQuery = ref('')
const tableHeight = ref(460) // 表格高度，默认值
const pageHeight = ref(600) // 页面高度

// 方法
const getLearningStatusData = () => {
  getLearningStatus(currentPage.value, pageSize.value, searchQuery.value).then(res => {
    learningStatusList.value = res.records || []
    total.value = res.total || 0
  }).catch(err => {
    console.error('获取学习情况错误:', err)
  })
}

// 防抖定时器
let searchTimer = null

const handleSearch = () => {
  if (searchTimer) {
    clearTimeout(searchTimer)
  }
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    getLearningStatusData()
  }, 300)
}

const handleSizeChange = (size) => {
  pageSize.value = size
  getLearningStatusData()
}

const handleCurrentChange = (current) => {
  currentPage.value = current
  getLearningStatusData()
}

const getProgressColor = (progress) => {
  if (progress >= 100) {
    return '#67C23A'
  } else if (progress >= 60) {
    return '#E6A23C'
  } else {
    return '#409EFF'
  }
}

// 岗位映射
const roleMap = {
  0: '管理员',
  1: '商铺开发',
  2: '上门服务',
  3: '品牌开发',
  4: '商铺招商',
  5: '品牌选址'
}

// 获取岗位文本
const getRoleText = (role) => {
  return roleMap[role] || '其他'
}

// 获取岗位标签类型
const getRoleTagType = (role) => {
  const typeMap = {
    0: 'warning',     // 管理员 - 橙色
    1: 'primary',    // 商铺开发 - 蓝色
    2: 'success',    // 上门服务 - 绿色
    3: 'warning',    // 品牌开发 - 橙色
    4: 'danger',     // 商铺招商 - 红色
    5: 'info'        // 品牌选址 - 灰色
  }
  return typeMap[role] || 'info'
}

const formatLearningTime = (seconds) => {
  if (!seconds || seconds === 0) return '0秒'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  let result = ''
  if (hours > 0) result += `${hours}小时`
  if (minutes > 0) result += `${minutes}分`
  if (secs > 0 && hours === 0) result += `${secs}秒`
  return result || '0秒'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 计算表格高度
const calculateTableHeight = () => {
  const windowHeight = window.innerHeight
  const offsetHeight = 320
  tableHeight.value = Math.max(400, windowHeight - offsetHeight)
  pageHeight.value = Math.max(500, windowHeight - 100)
}

// 生命周期
onMounted(() => {
  getLearningStatusData()
  calculateTableHeight()
  window.addEventListener('resize', calculateTableHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', calculateTableHeight)
})
</script>

<style scoped>
.learning-status-page {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.file-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}
</style>