<template>
  <div class="exam-results-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>员工成绩管理</h2>
      <p class="description">查看所有员工的考试成绩记录</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-card class="stat-card">
        <div class="stat-info">
          <p class="stat-value">{{ totalExams }}</p>
          <p class="stat-label">总考试次数</p>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-info">
          <p class="stat-value">{{ totalUsers }}</p>
          <p class="stat-label">参与员工数</p>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-info">
          <p class="stat-value">{{ avgScore }}</p>
          <p class="stat-label">平均得分</p>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-info">
          <p class="stat-value">{{ passRate }}%</p>
          <p class="stat-label">通过率</p>
        </div>
      </el-card>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索用户名或昵称"
        clearable
        style="width: 200px; margin-right: 10px;"
        @keyup.enter="handleSearch"
        @clear="handleSearch"
      >
        <template #prefix>
          <el-icon class="el-input__icon"><Search /></el-icon>
        </template>
      </el-input>
      <el-select 
        v-model="roleFilter" 
        placeholder="筛选角色" 
        clearable
        style="width: 120px; margin-right: 10px;"
        @change="handleSearch"
        @clear="handleSearch"
      >
        <el-option label="商铺开发" :value="1" />
        <el-option label="上门服务" :value="2" />
        <el-option label="品牌开发" :value="3" />
        <el-option label="商铺招商" :value="4" />
        <el-option label="品牌选址" :value="5" />
      </el-select>
      <el-button type="primary" icon="Search" @click="handleSearch">搜索</el-button>
    </div>

    <!-- 成绩表格 -->
    <el-card class="result-table-card">
      <el-table 
        :data="examResults" 
        :style="{ width: '100%', height: tableHeight + 'px' }"
        :loading="isLoading"
        border
        :fit="true"
      >
        <el-table-column prop="name" label="员工姓名" min-width="120">
          <template #default="scope">
            <div class="user-info">
              <el-avatar :size="32" :src="`https://ui-avatars.com/api/?name=${encodeURIComponent(scope.row.name.length <= 2 ? scope.row.name : scope.row.name.slice(-2))}&background=2e8b57&color=fff`">
                <User />
              </el-avatar>
              <span class="user-name">{{ scope.row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户名" min-width="100" />
        <el-table-column prop="role" label="角色" min-width="100" align="center" header-align="center">
          <template #default="scope">
            <span :class="['role-tag', `role-${scope.row.role}`]">
              {{ getRoleName(scope.row.role) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="exam_mode" label="考试类型" min-width="120" align="center" header-align="center">
          <template #default="scope">
            <span :class="['exam-type', scope.row.exam_mode]">
              {{ scope.row.exam_mode === 'comprehensive' ? '综合测试' : '专项测试' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="total_score" label="得分" min-width="80" align="center" header-align="center">
          <template #default="scope">
            <span :class="['score-value', getScoreClass(scope.row.total_score)]">
              {{ scope.row.total_score }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="accuracy" label="正确率" min-width="100" align="center" header-align="center">
          <template #default="scope">
            <span class="accuracy-value">{{ scope.row.accuracy || 0 }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="用时" min-width="100" align="center" header-align="center" />
        <el-table-column prop="exam_date" label="考试日期" min-width="160" align="center" header-align="center" />
        <el-table-column label="操作" min-width="100" align="center">
          <template #default="scope">
            <el-button size="small" link @click="viewDetail(scope.row)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
        />
      </div>
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="showDetailDialog"
      title="考试详情"
      width="520px"
      custom-class="exam-detail-dialog"
      :close-on-click-modal="false"
    >
      <div v-if="selectedResult" class="detail-content">
        <div class="detail-section">
          <div class="detail-user">
            <el-avatar :size="72" :src="`https://ui-avatars.com/api/?name=${selectedResult.name}&background=8DC149&color=fff`">
              <User />
            </el-avatar>
            <div class="user-info">
              <h3>{{ selectedResult.name }}</h3>
              <span class="role-tag">{{ getRoleName(selectedResult.role) }}</span>
            </div>
          </div>
        </div>
        
        <div class="detail-stats">
          <div class="stat-item">
            <span class="stat-value score">{{ selectedResult.total_score }}</span>
            <span class="stat-label">得分</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-value">{{ selectedResult.accuracy || 0 }}%</span>
            <span class="stat-label">正确率</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-value">{{ selectedResult.duration }}s</span>
            <span class="stat-label">用时</span>
          </div>
        </div>
        
        <div class="detail-grid">
          <div class="grid-item">
            <span class="grid-label">考试类型</span>
            <span class="grid-value">{{ selectedResult.exam_mode === 'comprehensive' ? '综合测试' : '专项测试' }}</span>
          </div>
          <div class="grid-item">
            <span class="grid-label">正确题数</span>
            <span class="grid-value correct">{{ selectedResult.correct_count || 0 }}</span>
          </div>
          <div class="grid-item">
            <span class="grid-label">错误题数</span>
            <span class="grid-value wrong">{{ selectedResult.wrong_count || 0 }}</span>
          </div>
          <div class="grid-item">
            <span class="grid-label">未答题数</span>
            <span class="grid-value">{{ selectedResult.unanswered_count || 0 }}</span>
          </div>
          <div class="grid-item full">
            <span class="grid-label">考试时间</span>
            <span class="grid-value">{{ selectedResult.exam_date }}</span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAllExamResults } from '../api/exam'
import { ElMessage } from 'element-plus'
import { Search, User } from '@element-plus/icons-vue'

const router = useRouter()

// 状态管理
const examResults = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const isLoading = ref(false)
const searchKeyword = ref('')
const roleFilter = ref('')
const showDetailDialog = ref(false)
const selectedResult = ref(null)
const tableHeight = ref(60)

// 角色映射
const roleMap = {
  0: '管理员',
  1: '商铺开发',
  2: '上门服务',
  3: '品牌开发',
  4: '商铺招商',
  5: '品牌选址'
}

const getRoleName = (role) => {
  const roleNum = typeof role === 'string' ? parseInt(role, 10) : role
  return roleMap[roleNum] || '未设置'
}

// 获取分数样式类
const getScoreClass = (score) => {
  const scoreNum = parseInt(score) || 0
  if (scoreNum >= 90) return 'excellent'
  if (scoreNum >= 80) return 'good'
  if (scoreNum >= 60) return 'pass'
  return 'fail'
}

// 统计数据
const totalExams = computed(() => total.value)
const totalUsers = computed(() => {
  const userIds = new Set(examResults.value.map(item => item.user_id))
  return userIds.size
})
const avgScore = computed(() => {
  if (examResults.value.length === 0) return 0
  const totalScore = examResults.value.reduce((sum, item) => sum + (parseInt(item.total_score) || 0), 0)
  return Math.round(totalScore / examResults.value.length)
})
const passRate = computed(() => {
  if (examResults.value.length === 0) return 0
  const passCount = examResults.value.filter(item => (parseInt(item.total_score) || 0) >= 60).length
  return Math.round((passCount / examResults.value.length) * 100)
})

// 加载数据
const loadData = async () => {
  isLoading.value = true
  try {
    const res = await getAllExamResults(currentPage.value, pageSize.value, searchKeyword.value, roleFilter.value)
    if (res.success && res.results) {
      examResults.value = res.results
      total.value = res.total
    }
  } catch (error) {
    console.error('获取考试成绩失败:', error)
    ElMessage.error('获取考试成绩失败')
  } finally {
    isLoading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

// 分页
const handlePageChange = (page) => {
  currentPage.value = page
  loadData()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadData()
}

// 查看详情
const viewDetail = (row) => {
  selectedResult.value = row
  showDetailDialog.value = true
}

// 计算表格高度
const calculateTableHeight = () => {
  const windowHeight = window.innerHeight
  const offsetHeight = 620
  tableHeight.value = Math.max(400, windowHeight - offsetHeight)
}

// 页面挂载
onMounted(() => {
  loadData()
  calculateTableHeight()
  window.addEventListener('resize', calculateTableHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', calculateTableHeight)
})
</script>

<style scoped>
.exam-results-page {
  height: 95%;
  padding: 20px;
  background: #f5f7fa;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.page-header .description {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 28px;
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px 24px;
  border-radius: 16px;
  background: linear-gradient(145deg, #ffffff, #f8f9fa);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}

.stat-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.stat-value {
  font-size: 42px;
  font-weight: 800;
  color: #1a1a1a;
  margin: 0 0 12px 0;
  line-height: 1.2;
  letter-spacing: -1px;
}

.stat-label {
  font-size: 18px;
  color: #666666;
  margin: 0;
  font-weight: 500;
}

/* 搜索栏 */
.search-bar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

/* 表格卡片 */
.result-table-card {
  border-radius: 12px;
  overflow: hidden;
}

/* 用户信息 */
.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-name {
  font-weight: 500;
  color: #303133;
}

/* 角色标签 */
.role-tag {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.role-1 { background: #e6f7ff; color: #1890ff; }
.role-2 { background: #f6ffed; color: #52c41a; }
.role-3 { background: #fff7e6; color: #faad14; }
.role-4 { background: #fff0f6; color: #eb2f96; }
.role-5 { background: #f9f0ff; color: #722ed1; }
.role-0 { background: #f5f5f5; color: #666; }

/* 考试类型 */
.exam-type {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.exam-type.comprehensive {
  background: #e6f7ff;
  color: #1890ff;
}

.exam-type.special {
  background: #f6ffed;
  color: #52c41a;
}

/* 分数样式 */
.score-value {
  font-weight: 600;
  font-size: 16px;
}

.score-value.excellent { color: #52c41a; }
.score-value.good { color: #1890ff; }
.score-value.pass { color: #faad14; }
.score-value.fail { color: #f5222d; }

/* 正确率 */
.accuracy-value {
  font-weight: 600;
  color: #52c41a;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  padding: 12px 0;
  flex-shrink: 0;
}

/* 详情弹窗 */
.exam-detail-dialog {
  border-radius: 16px !important;
  overflow: hidden;
}

.exam-detail-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #8DC149, #7ab838);
  color: white;
  padding: 20px 24px;
}

.exam-detail-dialog :deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: white;
}

.exam-detail-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.exam-detail-dialog :deep(.el-dialog__footer) {
  padding: 16px 24px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
}

.detail-content {
  padding: 24px;
}

/* 用户信息区域 */
.detail-section {
  padding-bottom: 20px;
  margin-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.detail-user {
  display: flex;
  align-items: center;
  gap: 16px;
}

.detail-user .el-avatar {
  width: 72px;
  height: 72px;
  font-size: 28px;
}

.user-info h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.user-info .role-tag {
  display: inline-block;
  padding: 4px 12px;
  background: #f6ffed;
  color: #52c41a;
  border-radius: 20px;
  font-size: 12px;
}

/* 统计数据区域 */
.detail-stats {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 32px;
  padding: 20px;
  margin-bottom: 20px;
  background: #f9fff5;
  border-radius: 12px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.stat-value.score {
  color: #8DC149;
  font-size: 36px;
}

.stat-label {
  font-size: 13px;
  color: #909399;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: #d9d9d9;
}

/* 详情网格 */
.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.grid-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.grid-item.full {
  grid-column: span 2;
}

.grid-label {
  font-size: 13px;
  color: #909399;
}

.grid-value {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.grid-value.correct {
  color: #52c41a;
}

.grid-value.wrong {
  color: #f5222d;
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .search-bar {
    flex-wrap: wrap;
  }
}
</style>
