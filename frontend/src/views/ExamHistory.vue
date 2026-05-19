<template>
  <div class="exam-history-page">
    <div class="header">
      <div class="header-left">
        <el-button link @click="goBack" class="back-btn">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
      </div>
      <div class="header-title">
        <h2>AI 冠军教练 · 历史成绩</h2>
      </div>
      <div class="header-right">
        <span class="username">{{ username }}</span>
        <el-button link @click="logout" class="logout-btn">退出登录</el-button>
      </div>
    </div>

    <div class="content">
      <div class="history-container">
        <div class="history-title">
          <h1>考试历史记录</h1>
          <p>查看您过往的考试成绩和统计分析</p>
        </div>

        <div v-loading="isLoading" class="history-content">
          <el-empty v-if="!isLoading && historyList.length === 0" description="暂无考试记录" />

          <div v-else class="history-list">
            <el-card v-for="item in historyList" :key="item.id" class="history-item">
              <div class="item-header">
                <div class="item-info">
                  <span class="exam-mode">{{ getExamModeText(item.exam_mode) }}</span>
                  <span class="exam-date">{{ item.exam_date }}</span>
                </div>
                <div class="item-score" :class="getScoreClass(item.total_score)">
                  {{ item.total_score }}分
                </div>
              </div>

              <div class="item-stats">
                <div class="stat-item correct">
                  <span class="stat-value">{{ item.correct_count }}</span>
                  <span class="stat-label">正确</span>
                </div>
                <div class="stat-item wrong">
                  <span class="stat-value">{{ item.wrong_count }}</span>
                  <span class="stat-label">错误</span>
                </div>
                <div class="stat-item unanswered">
                  <span class="stat-value">{{ item.unanswered_count }}</span>
                  <span class="stat-label">未答</span>
                </div>
                <div class="stat-item accuracy">
                  <span class="stat-value">{{ item.accuracy }}%</span>
                  <span class="stat-label">正确率</span>
                </div>
                <div class="stat-item duration">
                  <span class="stat-value">{{ formatDuration(item.duration) }}</span>
                  <span class="stat-label">用时</span>
                </div>
              </div>

              <div class="item-actions">
                <el-button type="primary" link @click="viewDetail(item.id)">查看详情</el-button>
              </div>
            </el-card>
          </div>

          <div v-if="total > pageSize" class="pagination-container">
            <el-pagination
              v-model:current-page="currentPage"
              :page-size="pageSize"
              :total="total"
              layout="prev, pager, next"
              @current-change="handlePageChange"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getNickname, logoutApi } from '../api/user'
import { getExamHistory } from '../api/exam'
import { ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()

const username = ref('')
const isLoading = ref(true)
const historyList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

onMounted(async () => {
  await Promise.all([loadUserInfo(), loadHistory()])
})

const loadUserInfo = async () => {
  try {
    const nicknameRes = await getNickname()
    username.value = nicknameRes.nickname || '用户'
  } catch (error) {
    console.error('获取用户信息失败:', error)
    username.value = '用户'
  }
}

const loadHistory = async () => {
  isLoading.value = true
  try {
    const res = await getExamHistory(currentPage.value, pageSize.value)
    if (res.success) {
      historyList.value = res.history || []
      total.value = res.total || 0
    } else {
      ElMessage.error('获取历史成绩失败')
    }
  } catch (error) {
    console.error('获取历史成绩失败:', error)
    ElMessage.error('获取历史成绩失败')
  } finally {
    isLoading.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadHistory()
}

const goBack = () => {
  router.back()
}

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

const getExamModeText = (mode) => {
  const modeMap = {
    'comprehensive': '正式考试',
    'simulation': '模拟测试',
    'specialized': '专项测试'
  }
  return modeMap[mode] || mode || '考试'
}

const getScoreClass = (score) => {
  if (score >= 80) return 'excellent'
  if (score >= 60) return 'good'
  return 'pass'
}

const formatDuration = (seconds) => {
  if (!seconds) return '0秒'
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  if (minutes > 0) {
    return `${minutes}分${secs}秒`
  }
  return `${secs}秒`
}

const viewDetail = (id) => {
  ElMessage.info('功能开发中...')
}
</script>

<style scoped>
.exam-history-page {
  min-height: 100vh;
  background: #d9f4e6;
}

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
  flex: 1;
  display: flex;
  align-items: center;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  color: white;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.back-btn:hover {
  opacity: 0.7;
  background: rgba(255, 255, 255, 0.1) !important;
}

.header-title {
  flex: 2;
  text-align: center;
}

.header-title h2 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 1px;
}

.header-right {
  flex: 1;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 16px;
  font-size: 15px;
  font-weight: 500;
}

.username {
  opacity: 0.95;
}

.logout-btn {
  color: white !important;
  font-weight: 500;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  opacity: 0.7;
  background: rgba(255, 255, 255, 0.1) !important;
}

.content {
  padding: 40px 24px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: calc(100vh - 80px);
  box-sizing: border-box;
}

.history-container {
  max-width: 900px;
  width: 100%;
}

.history-title {
  text-align: center;
  margin-bottom: 40px;
}

.history-title h1 {
  font-size: 36px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 12px 0;
  letter-spacing: 1px;
}

.history-title p {
  font-size: 16px;
  color: #7f8c8d;
  margin: 0;
}

.history-content {
  min-height: 400px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-item {
  border-radius: 12px;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  background: white;
}

.history-item:hover {
  box-shadow: 0 6px 20px rgba(141, 193, 73, 0.2);
}

.item-actions {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: flex-end;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.item-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.exam-mode {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.exam-date {
  font-size: 14px;
  color: #999;
}

.item-score {
  font-size: 28px;
  font-weight: 700;
  padding: 4px 16px;
  border-radius: 8px;
}

.item-score.excellent {
  color: #52c41a;
  background: rgba(82, 196, 26, 0.1);
}

.item-score.good {
  color: #1890ff;
  background: rgba(24, 144, 255, 0.1);
}

.item-score.pass {
  color: #faad14;
  background: rgba(250, 173, 20, 0.1);
}

.item-stats {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.stat-label {
  font-size: 12px;
  color: #999;
}

.stat-item.correct .stat-value {
  color: #52c41a;
}

.stat-item.wrong .stat-value {
  color: #ff4d4f;
}

.stat-item.unanswered .stat-value {
  color: #999;
}

.stat-item.accuracy .stat-value {
  color: #1890ff;
}

.stat-item.duration .stat-value {
  color: #722ed1;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

@media (max-width: 768px) {
  .header {
    min-width: 100%;
    padding: 0 20px;
  }

  .item-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .item-stats {
    gap: 16px;
  }
}
</style>
