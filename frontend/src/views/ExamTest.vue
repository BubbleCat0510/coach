<template>
  <div class="exam-test-page">
    <!-- 顶部标题栏 -->
    <div class="header">
      <div class="header-left">
        <el-button link @click="goBack" class="back-btn">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
      </div>
      <div class="header-title">
        <h2>AI 冠军教练 · 正式测试</h2>
      </div>
      <div class="header-right">
        <span class="username">{{ username }}</span>
        <span class="timer">剩余时间: {{ formatTime(remainingTime) }}</span>
      </div>
    </div>

    <!-- 主体内容区域 -->
    <div class="content">
      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-container">
        <div class="loading-spinner"></div>
        <div class="loading-text">正在加载题目...</div>
      </div>

      <div v-else class="exam-container">
        <!-- 测试信息 -->
        <div class="exam-info">
          <div class="info-item">
            <span class="label">题目总数</span>
            <span class="value">{{ questions.length }}</span>
          </div>
          <div class="info-item">
            <span class="label">已答题目</span>
            <span class="value">{{ answeredCount }}</span>
          </div>
          <div class="info-item">
            <span class="label">测试时长</span>
            <span class="value">60分钟</span>
          </div>
        </div>

        <!-- 题目内容 -->
        <div class="question-content">
          <div class="question-header">
            <span class="question-type" :class="getQuestionTypeClass(currentQuestion.type)">{{ getTypeName(currentQuestion.type) }}</span>
            <span class="question-number">第 {{ currentIndex + 1 }} 题</span>
          </div>
          <h2 class="question-text">{{ currentQuestion.question }}</h2>
          
          <!-- 选项 -->
          <div class="options" v-if="currentQuestion.type !== 'judge'">
            <div
              v-for="(opt, optIndex) in currentQuestion.options"
              :key="optIndex"
              :class="['option-item', { selected: isSelected(optIndex) }]"
              @click="selectOption(optIndex)"
            >
              <span class="option-label">{{ ['A', 'B', 'C', 'D'][optIndex] }}</span>
              <span class="option-text">{{ opt }}</span>
            </div>
          </div>

          <!-- 判断题选项 -->
          <div class="judge-options" v-else>
            <div
              :class="['judge-item', { selected: answers[currentIndex] === '正确' }]"
              @click="selectJudge('正确')"
            >
              <span class="judge-icon correct">✓</span>
              <span>正确</span>
            </div>
            <div
              :class="['judge-item', { selected: answers[currentIndex] === '错误' }]"
              @click="selectJudge('错误')"
            >
              <span class="judge-icon wrong">✗</span>
              <span>错误</span>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button :disabled="currentIndex === 0" @click="prevQuestion">上一题</el-button>
          <el-button v-if="currentIndex < questions.length - 1" @click="nextQuestion">下一题</el-button>
          <el-button v-else type="primary" @click="submitExam">提交试卷</el-button>
        </div>
      </div>
    </div>

    <!-- 侧边浮窗题目导航 -->
    <div class="side-nav-wrapper">
      <button class="side-nav-toggle" @click="toggleSideNav">
        <span class="toggle-icon">{{ sideNavExpanded ? '›' : '‹' }}</span>
      </button>
      <div class="side-nav" :class="{ collapsed: !sideNavExpanded }">
        <div class="side-nav-inner">
          <div class="side-nav-header">
            <span>题目导航</span>
          </div>
          <div class="side-nav-grid">
            <button
              v-for="(q, index) in questions"
              :key="index"
              :class="['side-nav-btn', { active: currentIndex === index, answered: answers[index] }]"
              @click="goToQuestion(index)"
            >
              <span class="question-badge" :class="getQuestionTypeClass(q.type)"></span>
              {{ index + 1 }}
            </button>
          </div>
          <div class="side-nav-legend">
            <div class="legend-item"><span class="dot answered"></span>已答</div>
            <div class="legend-item"><span class="dot current"></span>当前</div>
            <div class="legend-item"><span class="dot unanswered"></span>未答</div>
            <div class="legend-item"><span class="dot type-single"></span>单选</div>
            <div class="legend-item"><span class="dot type-multiple"></span>多选</div>
            <div class="legend-item"><span class="dot type-judge"></span>判断</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 提交确认弹窗 -->
    <el-dialog title="确认提交" v-model="showSubmitDialog" width="480px">
      <p>您已完成 {{ answeredCount }}/{{ questions.length }} 道题目</p>
      <div v-if="unansweredQuestions.length > 0">
        <p class="warning">
          还有 {{ unansweredQuestions.length }} 道题目未作答：
        </p>
        <div class="unanswered-list">
          <button
            v-for="num in unansweredQuestions"
            :key="num"
            class="unanswered-btn"
            @click="jumpToUnanswered(num - 1)"
          >
            {{ num }}
          </button>
        </div>
        <p class="hint">点击题号可快速跳转</p>
      </div>
      <template #footer>
        <el-button @click="showSubmitDialog = false">继续答题</el-button>
        <el-button type="primary" @click="confirmSubmit">确认提交</el-button>
      </template>
    </el-dialog>

    <!-- 分数结算弹窗 -->
    <el-dialog
      v-model="showResultDialog"
      width="480px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
      :header-hidden="true"
      class="result-dialog"
    >
      <div class="result-content">
        <div class="score-circle">
          <div class="score-number">{{ examResult.totalScore.toFixed(1) }}</div>
          <div class="score-label">总分</div>
        </div>
        <div class="result-stats">
          <div class="stat-item">
            <span class="stat-label">正确</span>
            <span class="stat-value correct">{{ examResult.correctCount }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">错误</span>
            <span class="stat-value wrong">{{ examResult.wrongCount }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">未答</span>
            <span class="stat-value unanswered">{{ examResult.unansweredCount }}</span>
          </div>
        </div>
        <div class="accuracy-section">
          <div class="accuracy-header">
            <span class="accuracy-label">正确率</span>
            <span class="accuracy-value">{{ examResult.accuracy }}%</span>
          </div>
          <div class="accuracy-progress">
            <div class="progress-fill" :style="{ width: examResult.accuracy + '%' }"></div>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="result-footer">
          <el-button class="result-btn" @click="closeResultDialog">返回评估中心</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 防作弊警告弹窗 -->
    <el-dialog
      v-model="showCheatWarning"
      width="480px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
      title="⚠️ 考试提醒"
      class="cheat-warning-dialog"
    >
      <div class="cheat-warning-content">
        <p class="warning-message">{{ cheatWarningMessage }}</p>
        <p class="warning-count">已提醒 {{ cheatWarningCount }}/3 次，累计3次将自动提交试卷</p>
      </div>
      <template #footer>
        <el-button type="primary" @click="confirmCheatWarning">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { getNickname } from '../api/user'
import { saveExamResult, getRandomQuestions } from '../api/exam'
import { ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()

const username = ref('')
const currentIndex = ref(0)
const answers = ref({})
const TOTAL_TIME = 60 * 60 * 1000 // 60分钟，毫秒级
const remainingTime = ref(TOTAL_TIME)
const showSubmitDialog = ref(false)
const sideNavExpanded = ref(true)
const showResultDialog = ref(false)
const examResult = ref({
  totalScore: 0,
  correctCount: 0,
  wrongCount: 0,
  unansweredCount: 0,
  accuracy: 0
})

const startTimestamp = ref(null)
const examStartTime = ref(null)
const isLoading = ref(true)
let timer = null

// 防作弊相关变量
const showCheatWarning = ref(false)
const cheatWarningCount = ref(0)
const cheatWarningMessage = ref('')
const MAX_WARNING_COUNT = 3

// 题目列表（从数据库获取）
const questions = ref([])

// 解析选项字符串
const parseOptions = (optionsStr) => {
  if (!optionsStr) return []
  if (optionsStr.startsWith('[')) {
    try {
      return JSON.parse(optionsStr)
    } catch {
      return []
    }
  }
  const options = []
  const parts = optionsStr.split(',')
  for (const part of parts) {
    const match = part.match(/^([A-D])\.(.+)$/)
    if (match) {
      options.push(match[2].trim())
    } else if (part.trim()) {
      options.push(part.trim())
    }
  }
  return options
}

const currentQuestion = computed(() => questions.value[currentIndex.value])
const answeredCount = computed(() => Object.keys(answers.value).length)
const unansweredQuestions = computed(() => {
  const list = []
  questions.value.forEach((_, index) => {
    if (!answers.value[index]) {
      list.push(index + 1)
    }
  })
  return list
})

onMounted(async () => {
  try {
    const nicknameRes = await getNickname()
    username.value = nicknameRes.nickname || '用户'
  } catch (error) {
    console.error('获取用户信息失败:', error)
    username.value = '用户'
  }

  // 记录考试开始时间
  examStartTime.value = new Date().toISOString().replace('T', ' ').substring(0, 19)

  // 从数据库获取随机题目（单选题10题、判断题10题、多选题5题）
  try {
    const questionsRes = await getRandomQuestions()
    if (questionsRes.success && questionsRes.questions) {
      questions.value = questionsRes.questions.map(q => ({
        id: q.id,
        question: q.question,
        options: parseOptions(q.options),
        answer: q.answer,
        type: q.type
      }))
    } else {
      console.error('获取题目失败')
      ElMessage.error('获取题目失败，请刷新重试')
    }
  } catch (error) {
    console.error('获取题目失败:', error)
    ElMessage.error('获取题目失败，请刷新重试')
  }

  // 加载完成
  isLoading.value = false

  // 开始倒计时（使用 requestAnimationFrame）
  startTimestamp.value = Date.now()
  
  const updateTimer = () => {
    const elapsed = Date.now() - startTimestamp.value
    remainingTime.value = Math.max(0, TOTAL_TIME - elapsed)
    
    if (remainingTime.value <= 0) {
      // 倒计时结束，强制提交试卷
      ElMessage.warning('考试时间已到，系统将自动提交试卷')
      confirmSubmit()
    } else {
      timer = requestAnimationFrame(updateTimer)
    }
  }
  
  timer = requestAnimationFrame(updateTimer)

  // 切屏/失焦警告
  document.addEventListener('visibilitychange', handleVisibilityChange)
  document.addEventListener('blur', handleBlur)
  
  // 意外关闭拦截
  window.addEventListener('beforeunload', handleBeforeUnload)
  
  // 键盘快捷键
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  if (timer) {
    cancelAnimationFrame(timer)
  }
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  document.removeEventListener('blur', handleBlur)
  window.removeEventListener('beforeunload', handleBeforeUnload)
  document.removeEventListener('keydown', handleKeydown)
})

// 显示防作弊警告弹窗
const showCheatWarningDialog = (message) => {
  // 如果弹窗已显示或已达到最大警告次数，不再处理
  if (showCheatWarning.value || cheatWarningCount.value >= MAX_WARNING_COUNT) return
  
  cheatWarningCount.value++
  cheatWarningMessage.value = message
  
  console.log(`防作弊提醒 ${cheatWarningCount.value}:`, message, '时间:', new Date().toLocaleString())
  
  if (cheatWarningCount.value >= MAX_WARNING_COUNT) {
    // 超过三次提醒，直接提交试卷
    ElMessage.warning('已累计3次离开考试页面，系统将自动提交试卷')
    setTimeout(() => {
      confirmSubmit()
    }, 1000)
  } else {
    showCheatWarning.value = true
  }
}

// 确认防作弊警告
const confirmCheatWarning = () => {
  showCheatWarning.value = false
}

// 切屏警告
const handleVisibilityChange = () => {
  if (document.hidden && !showResultDialog.value) {
    showCheatWarningDialog('检测到您离开了考试页面，请专注答题！')
  }
}

// 失焦警告
const handleBlur = () => {
  if (!showResultDialog.value) {
    showCheatWarningDialog('检测到考试页面失去焦点，请专注答题！')
  }
}

// 关闭页面时提交成绩
const handleBeforeUnload = async (e) => {
  if (showResultDialog.value || isLoading.value) return
  
  // 阻止默认提示，我们将自动提交成绩
  e.preventDefault()
  e.returnValue = ''
  
  // 如果没有答题，直接返回
  if (answeredCount.value === 0) return
  
  // 调用通用自动交卷函数
  autoSubmitExam()
}

// 自动交卷并保存成绩（通用函数）
const autoSubmitExam = async () => {
  // 如果结果弹窗已显示（考试已完成），不重复提交
  if (showResultDialog.value || isLoading.value) return
  
  try {
    // 计算考试用时（秒）
    const duration = Math.floor((Date.now() - startTimestamp.value) / 1000)
    
    // 构建答案列表（直接传递给 save_result）
    const roundAnswers = questions.value.map((q, index) => ({
      round_no: index + 1,
      question_id: q.id,
      answer: answers.value[index] || ''
    }))
    
    const data = {
      exam_date: examStartTime.value || new Date().toISOString().replace('T', ' ').substring(0, 19),
      duration: duration,
      exam_mode: 'comprehensive',
      round_answers: roundAnswers
    }
    
    // 使用 fetch keepalive 确保页面关闭时请求能完成
    await fetch('/api/exam/save_result', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(data),
      keepalive: true
    })
    
    console.log('成绩已自动提交')
  } catch (error) {
    console.error('自动提交成绩失败:', error)
  }
}

// 键盘快捷键
const handleKeydown = (e) => {
  if (isLoading.value || showSubmitDialog.value || showResultDialog.value) {
    return
  }
  
  const key = e.key.toUpperCase()
  
  // A/B/C/D 选择答案
  if (['A', 'B', 'C', 'D'].includes(key)) {
    e.preventDefault()
    const index = ['A', 'B', 'C', 'D'].indexOf(key)
    if (currentQuestion.value && currentQuestion.value.type !== 'judge') {
      selectOption(index)
    }
  }
  
  // 左右箭头切题
  if (e.key === 'ArrowLeft') {
    e.preventDefault()
    prevQuestion()
  }
  if (e.key === 'ArrowRight') {
    e.preventDefault()
    nextQuestion()
  }
  
  // 判断题快捷键
  if (key === '1' || key === 'ENTER') {
    if (currentQuestion.value && currentQuestion.value.type === 'judge') {
      e.preventDefault()
      selectJudge('正确')
    }
  }
  if (key === '0') {
    if (currentQuestion.value && currentQuestion.value.type === 'judge') {
      e.preventDefault()
      selectJudge('错误')
    }
  }
}

const formatTime = (milliseconds) => {
  const totalSeconds = Math.floor(milliseconds / 1000)
  const h = Math.floor(totalSeconds / 3600)
  const m = Math.floor((totalSeconds % 3600) / 60)
  const s = totalSeconds % 60
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

const getTypeName = (type) => {
  const types = {
    single: '单选题',
    multiple: '多选题',
    judge: '判断题'
  }
  return types[type] || '未知类型'
}

const getQuestionTypeClass = (type) => {
  const classes = {
    single: 'type-single',
    multiple: 'type-multiple',
    judge: 'type-judge'
  }
  return classes[type] || ''
}

const isSelected = (optIndex) => {
  const answer = answers.value[currentIndex.value]
  if (!answer) return false
  const label = ['A', 'B', 'C', 'D'][optIndex]
  return answer.includes(label)
}

const selectOption = (optIndex) => {
  const label = ['A', 'B', 'C', 'D'][optIndex]
  const current = answers.value[currentIndex.value] || ''
  
  if (currentQuestion.value.type === 'single') {
    // 单选题：直接替换答案
    answers.value[currentIndex.value] = label
  } else {
    // 多选题：添加或移除选项
    const selectedOptions = current.split('')
    const optionIndex = selectedOptions.indexOf(label)
    
    if (optionIndex !== -1) {
      // 已选中，取消选择
      selectedOptions.splice(optionIndex, 1)
      answers.value[currentIndex.value] = selectedOptions.sort().join('')
    } else {
      // 未选中，添加选项并排序
      selectedOptions.push(label)
      answers.value[currentIndex.value] = selectedOptions.sort().join('')
    }
  }
}

const selectJudge = (value) => {
  answers.value[currentIndex.value] = value
}

const goToQuestion = (index) => {
  currentIndex.value = index
}

const jumpToUnanswered = (index) => {
  currentIndex.value = index
  showSubmitDialog.value = false
}

const toggleSideNav = () => {
  sideNavExpanded.value = !sideNavExpanded.value
}

const prevQuestion = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

const nextQuestion = () => {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value++
  }
}

const submitExam = () => {
  showSubmitDialog.value = true
}

const confirmSubmit = async () => {
  showSubmitDialog.value = false
  
  // 计算考试用时（秒）- 使用真实耗时
  const duration = Math.floor((Date.now() - startTimestamp.value) / 1000)
  
  // 构建答案列表（直接传递给 save_result）
  const roundAnswers = questions.value.map((q, index) => ({
    round_no: index + 1,
    question_id: q.id,
    answer: answers.value[index] || ''
  }))
  
  try {
    // 直接提交到结果表（后端计算分数和统计数据，不使用 coach_exam_session）
    const saveRes = await saveExamResult({
      exam_date: examStartTime.value || new Date().toISOString().replace('T', ' ').substring(0, 19),
      duration: duration,
      exam_mode: 'comprehensive',
      round_answers: roundAnswers  // 直接传递答案，后端计算
    })
    
    // 使用后端计算的统计数据
    examResult.value.correctCount = saveRes.correct_count || 0
    examResult.value.wrongCount = saveRes.wrong_count || 0
    examResult.value.unansweredCount = saveRes.unanswered_count || 0
    examResult.value.accuracy = saveRes.accuracy || 0
    examResult.value.totalScore = saveRes.total_score || 0
    console.log('考试结果保存成功:', saveRes)
  } catch (error) {
    console.error('保存结果失败，使用前端计算:', error)
    // 降级使用前端计算（仅在后端失败时使用）
    calculateScore()
  }
  
  // 显示结果弹窗
  showResultDialog.value = true
}

const calculateScore = () => {
  let totalScore = 0
  let correctCount = 0
  let wrongCount = 0
  let unansweredCount = 0

  // 使用整数分值（乘以100）避免浮点精度问题
  const scoreMap = {
    multiple: 278,  // 2.78 * 100
    judge: 130,     // 1.30 * 100
    single: 186     // 1.86 * 100
  }

  questions.value.forEach((q, index) => {
    const userAnswer = answers.value[index]
    if (!userAnswer) {
      unansweredCount++
    } else {
      // 多选题答案排序后比较
      const userAns = userAnswer.toUpperCase().trim()
      const correctAns = q.answer ? q.answer.toUpperCase().trim() : ''
      
      // 防御性检查：如果正确答案为空，跳过此题
      if (!correctAns) {
        unansweredCount++
        return
      }
      
      const userSorted = userAns ? userAns.split('').sort().join('') : ''
      const correctSorted = correctAns.split('').sort().join('')
      
      if (userSorted === correctSorted) {
        // 根据题目类型确定分值
        totalScore += scoreMap[q.type] || scoreMap.single
        correctCount++
      } else {
        wrongCount++
      }
    }
  })

  // 转换为小数并限制范围（0-100，保留一位小数）
  totalScore = totalScore / 100
  totalScore = Math.round(totalScore * 10) / 10
  totalScore = Math.max(0, Math.min(100, totalScore))

  examResult.value = {
    totalScore,
    correctCount,
    wrongCount,
    unansweredCount,
    accuracy: questions.value.length > 0 ? Math.round((correctCount / questions.value.length) * 100) : 0
  }
}

const closeResultDialog = () => {
  showResultDialog.value = false
  router.push('/exam-center')
}

const goBack = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要退出考试吗？退出后系统将自动提交您的当前答案并结算成绩。',
      '确认退出考试',
      {
        confirmButtonText: '确认退出',
        cancelButtonText: '继续答题',
        type: 'warning',
        closeOnClickModal: false,
        closeOnPressEscape: false
      }
    )
    
    // 用户确认退出，如果有答题则自动交卷
    if (answeredCount.value > 0) {
      await autoSubmitExam()
    }
    
    if (timer) {
      cancelAnimationFrame(timer)
    }
    
    ElMessage.success('成绩已保存')
    router.push('/exam-center')
  } catch {
    // 用户取消退出，继续答题
    ElMessage.info('继续答题')
  }
}
</script>

<style scoped>
.exam-test-page {
  min-height: 100vh;
}

/* 加载状态样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
  gap: 20px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-size: 16px;
  color: #666;
}

.header {
  height: 80px;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
  box-shadow: 0 4px 20px rgba(141, 193, 73, 0.3);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  flex: 1;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  color: white;
  font-size: 15px;
  font-weight: 500;
}

.header-title h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
}

.header-right {
  flex: 1;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 20px;
  font-size: 15px;
}

.timer {
  background: rgba(255, 255, 255, 0.2);
  padding: 6px 16px;
  border-radius: 20px;
  font-weight: 600;
}

.content {
  padding: 30px 40px;
}

.exam-container {
  max-width: 1000px;
  margin: 0 auto;
}

.exam-info {
  display: flex;
  gap: 40px;
  margin-bottom: 30px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item .label {
  font-size: 14px;
  color: #666;
}

.info-item .value {
  font-size: 24px;
  font-weight: 700;
  color: #228b22;
}

/* 侧边浮窗题目导航 */
.side-nav-wrapper {
  position: fixed;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  z-index: 100;
}

.side-nav-inner {
  position: relative;
  width: 200px;
  background: white;
  border-radius: 12px 0 0 12px;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.15);
  padding: 16px;
  overflow: hidden;
}

.side-nav {
  position: relative;
  width: 200px;
  overflow: hidden;
  padding: 16px;
  transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.side-nav.collapsed {
  width: 0;
  padding: 0;
  opacity: 0;
  pointer-events: none;
}

.side-nav-toggle {
  width: 32px;
  height: 60px;
  background: white;
  border: none;
  border-radius: 8px 0 0 8px;
  box-shadow: -2px 0 12px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.side-nav-toggle:hover {
  background: #f0f0f0;
}

.toggle-icon {
  font-size: 20px;
  color: #666;
  font-weight: bold;
}

.side-nav-header {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  text-align: center;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.side-nav-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 4px;
}

.side-nav-btn {
  width: 36px;
  height: 32px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 2px;
}

.question-badge {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.question-badge.type-single {
  background: #1890ff;
}

.question-badge.type-multiple {
  background: #52c41a;
}

.question-badge.type-judge {
  background: #faad14;
}

.side-nav-btn:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
  transform: scale(1.05);
}

.side-nav-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.side-nav-btn.answered:not(.active) {
  background: #e6f7ee;
  border-color: var(--primary-color);
  color: #228b22;
}

.side-nav-legend {
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid #eee;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.legend-item {
  font-size: 11px;
  color: #666;
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-item .dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.legend-item .dot.answered {
  background: #e6f7ee;
  border: 1px solid var(--primary-color);
}

.legend-item .dot.current {
  background: var(--primary-color);
}

.legend-item .dot.unanswered {
  background: white;
  border: 1px solid #ddd;
}

.legend-item .dot.type-single {
  background: #1890ff;
}

.legend-item .dot.type-multiple {
  background: #52c41a;
}

.legend-item .dot.type-judge {
  background: #faad14;
}

.question-content {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.question-type {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.question-type.type-single {
  background: #e6f0ff;
  color: #1890ff;
}

.question-type.type-multiple {
  background: #e6f7ee;
  color: #52c41a;
}

.question-type.type-judge {
  background: #fff7e6;
  color: #faad14;
}

.question-number {
  font-size: 14px;
  color: #666;
}

.question-text {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  line-height: 1.6;
  margin-bottom: 30px;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.option-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 20px;
  border: 2px solid #e8e8e8;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.option-item:hover {
  border-color: var(--primary-color);
  background: #f6fff3;
}

.option-item.selected {
  border-color: var(--primary-color);
  background: #e6f7ee;
}

.option-label {
  width: 28px;
  height: 28px;
  background: #f0f0f0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  color: #666;
  flex-shrink: 0;
}

.option-item.selected .option-label {
  background: var(--primary-color);
  color: white;
}

.option-text {
  font-size: 16px;
  color: #333;
  line-height: 1.5;
}

.judge-options {
  display: flex;
  gap: 20px;
}

.judge-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 24px;
  border: 2px solid #e8e8e8;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 18px;
  font-weight: 500;
}

.judge-item:hover {
  border-color: var(--primary-color);
}

.judge-item.selected {
  border-color: var(--primary-color);
  background: #e6f7ee;
}

.judge-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
}

.judge-icon.correct {
  background: #52c41a;
  color: white;
}

.judge-icon.wrong {
  background: #ff4d4f;
  color: white;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.action-buttons button {
  padding: 12px 40px;
  font-size: 16px;
  font-weight: 500;
}

.warning {
  color: #faad14;
}

.unanswered-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 12px 0;
}

.unanswered-btn {
  width: 36px;
  height: 36px;
  border: 1px solid #ffccc7;
  border-radius: 6px;
  background: #fff7f6;
  color: #ff4d4f;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.unanswered-btn:hover {
  background: #ff4d4f;
  color: white;
  border-color: #ff4d4f;
}

.hint {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}

/* 分数结算弹框样式 */
.result-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 5px 20px 5px;
  background: linear-gradient(180deg, #f8fff5 5%, #ffffff 20%);
}

.score-circle {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background: linear-gradient(145deg, var(--primary-color), var(--primary-dark));
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 35px;
  box-shadow: 
    0 8px 32px rgba(141, 193, 73, 0.35),
    0 4px 12px rgba(141, 193, 73, 0.2),
    inset 0 2px 4px rgba(255, 255, 255, 0.3);
  position: relative;
}

.score-circle::before {
  content: '';
  position: absolute;
  top: -5px;
  left: -5px;
  right: -5px;
  bottom: -5px;
  border-radius: 50%;
  background: linear-gradient(145deg, rgba(141, 193, 73, 0.2), rgba(106, 184, 42, 0.1));
  z-index: -1;
}

.score-number {
  font-size: 56px;
  font-weight: 800;
  line-height: 1;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}

.score-label {
  font-size: 14px;
  margin-top: 6px;
  opacity: 0.95;
  letter-spacing: 2px;
}

.result-stats {
  display: flex;
  gap: 50px;
  margin-bottom: 35px;
  padding: 20px 30px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  position: relative;
}

.stat-item:not(:last-child)::after {
  content: '';
  position: absolute;
  right: -25px;
  top: 50%;
  transform: translateY(-50%);
  width: 1px;
  height: 40px;
  background: linear-gradient(180deg, transparent, #e0e0e0, transparent);
}

.stat-label {
  font-size: 13px;
  color: #888;
  font-weight: 500;
}

.stat-value {
  font-size: 32px;
  font-weight: 800;
}

.stat-value.correct {
  color: #52c41a;
}

.stat-value.wrong {
  color: #ff4d4f;
}

.stat-value.unanswered {
  color: #bbb;
}

.accuracy-section {
  width: 100%;
  background: white;
  padding: 20px 25px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.accuracy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.accuracy-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.accuracy-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary-color);
}

.accuracy-progress {
  width: 100%;
  height: 10px;
  background: #f0f0f0;
  border-radius: 5px;
  overflow: hidden;
  position: relative;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary-color), var(--primary-light), var(--primary-color));
  background-size: 200% 100%;
  border-radius: 5px;
  transition: width 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
}

.progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.result-dialog {
  display: flex !important;
  align-items: center;
  justify-content: center;
}

.result-dialog .el-dialog__wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden !important;
  margin: 0 !important;
  padding: 0 !important;
}

.result-dialog .el-dialog {
  margin: 0 !important;
  overflow: visible !important;
  padding: 0 !important;
  border-radius: 0 !important;
}

.result-dialog .el-dialog__body {
  overflow: hidden !important;
  padding: 0 !important;
  margin: 0 !important;
}

.result-footer {
  display: flex;
  justify-content: center;
  padding:5px 0 20px 0;
  background: white;
}

.result-btn {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark)) !important;
  border: none !important;
  color: white !important;
  padding: 12px 48px !important;
  font-size: 16px !important;
  font-weight: 600 !important;
  border-radius: 30px !important;
  box-shadow: 0 4px 16px rgba(141, 193, 73, 0.35) !important;
  transition: all 0.3s ease !important;
}

.result-btn:hover {
  background: linear-gradient(135deg, #7ab838, #6ab82a) !important;
  box-shadow: 0 6px 20px rgba(141, 193, 73, 0.45) !important;
  transform: translateY(-2px);
}

.result-btn:active {
  transform: translateY(0);
}

@media (max-width: 768px) {
  .header {
    padding: 0 20px;
  }

  .header-title h2 {
    font-size: 20px;
  }

  .content {
    padding: 20px;
  }

  .exam-info {
    flex-direction: column;
    gap: 16px;
  }

  .judge-options {
    flex-direction: column;
  }
}
</style>
