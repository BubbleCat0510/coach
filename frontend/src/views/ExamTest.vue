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
      <div class="exam-container">
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
        <div class="question-content" v-if="currentQuestion">
          <div class="question-header">
            <span class="question-type">{{ getTypeName(currentQuestion.type) }}</span>
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
              {{ index + 1 }}
            </button>
          </div>
          <div class="side-nav-legend">
            <div class="legend-item"><span class="dot answered"></span>已答</div>
            <div class="legend-item"><span class="dot current"></span>当前</div>
            <div class="legend-item"><span class="dot unanswered"></span>未答</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 提交确认弹窗 -->
    <el-dialog title="确认提交" v-model="showSubmitDialog" width="400px">
      <p>您已完成 {{ answeredCount }}/{{ questions.length }} 道题目</p>
      <p v-if="questions.length - answeredCount > 0" class="warning">
        还有 {{ questions.length - answeredCount }} 道题目未作答，确定要提交吗？
      </p>
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
          <div class="score-number">{{ examResult.totalScore }}</div>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { getNickname } from '../api/user'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'

const router = useRouter()

const username = ref('')
const currentIndex = ref(0)
const answers = ref({})
const remainingTime = ref(60 * 60) // 60分钟
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
let timer = null

// 模拟题目数据（共25题：10单选、10判断、5多选）
const questions = ref([
  // ========== 单选题（10题，每题3分）==========
  {
    id: 1,
    question: '以下哪个是Vue3的响应式API？',
    options: ['ref', 'useState', 'createSignal', 'observable'],
    answer: 'A',
    type: 'single',
    score: 3
  },
  {
    id: 2,
    question: 'HTTP状态码404表示什么？',
    options: ['服务器错误', '未找到资源', '请求超时', '重定向'],
    answer: 'B',
    type: 'single',
    score: 3
  },
  {
    id: 3,
    question: 'JavaScript中，哪个方法可以将字符串转换为整数？',
    options: ['parseInt()', 'toInteger()', 'int()', 'Number.parseInt()'],
    answer: 'A',
    type: 'single',
    score: 3
  },
  {
    id: 4,
    question: 'CSS中，用于设置元素相对于其父元素定位的属性是？',
    options: ['position', 'display', 'float', 'overflow'],
    answer: 'A',
    type: 'single',
    score: 3
  },
  {
    id: 5,
    question: '以下哪个HTML标签用于创建无序列表？',
    options: ['<ul>', '<ol>', '<li>', '<dl>'],
    answer: 'A',
    type: 'single',
    score: 3
  },
  {
    id: 6,
    question: 'Git中，哪个命令用于查看当前仓库的提交历史？',
    options: ['git log', 'git history', 'git commit log', 'git show'],
    answer: 'A',
    type: 'single',
    score: 3
  },
  {
    id: 7,
    question: 'JavaScript中，哪个关键字用于声明一个常量？',
    options: ['const', 'let', 'var', 'constant'],
    answer: 'A',
    type: 'single',
    score: 3
  },
  {
    id: 8,
    question: 'MySQL中，用于删除表的命令是？',
    options: ['DROP TABLE', 'DELETE TABLE', 'REMOVE TABLE', 'DROP DATABASE'],
    answer: 'A',
    type: 'single',
    score: 3
  },
  {
    id: 9,
    question: 'Vue组件中，props选项用于？',
    options: ['定义组件属性', '定义组件方法', '定义组件数据', '定义组件样式'],
    answer: 'A',
    type: 'single',
    score: 3
  },
  {
    id: 10,
    question: 'CSS中，哪个属性用于控制元素的透明度？',
    options: ['opacity', 'transparent', 'visibility', 'alpha'],
    answer: 'A',
    type: 'single',
    score: 3
  },
  // ========== 判断题（10题，每题3分）==========
  {
    id: 11,
    question: 'JavaScript中，const声明的变量不能被重新赋值。',
    answer: '正确',
    type: 'judge',
    score: 3
  },
  {
    id: 12,
    question: 'CSS中，margin可以设置为负值。',
    answer: '正确',
    type: 'judge',
    score: 3
  },
  {
    id: 13,
    question: 'Git reset --hard 会保留工作区的修改。',
    answer: '错误',
    type: 'judge',
    score: 3
  },
  {
    id: 14,
    question: 'Vue3中，可以使用Options API和Composition API两种方式编写组件。',
    answer: '正确',
    type: 'judge',
    score: 3
  },
  {
    id: 15,
    question: 'HTML中，<br>标签不需要闭合。',
    answer: '正确',
    type: 'judge',
    score: 3
  },
  {
    id: 16,
    question: 'JavaScript中的数组索引从0开始。',
    answer: '正确',
    type: 'judge',
    score: 3
  },
  {
    id: 17,
    question: 'CSS选择器的优先级：ID选择器 > 类选择器 > 标签选择器。',
    answer: '正确',
    type: 'judge',
    score: 3
  },
  {
    id: 18,
    question: 'HTTP协议是无状态的。',
    answer: '正确',
    type: 'judge',
    score: 3
  },
  {
    id: 19,
    question: 'Vue组件中的data必须是一个函数。',
    answer: '正确',
    type: 'judge',
    score: 3
  },
  {
    id: 20,
    question: 'JavaScript中，typeof null返回"null"。',
    answer: '错误',
    type: 'judge',
    score: 3
  },
  // ========== 多选题（5题，每题8分）==========
  {
    id: 21,
    question: 'CSS中，以下哪些是Flexbox的属性？',
    options: ['display: flex', 'justify-content', 'align-items', 'grid-template'],
    answer: 'ABC',
    type: 'multiple',
    score: 8
  },
  {
    id: 22,
    question: 'Git中，以下哪些操作可以撤销提交？',
    options: ['git revert', 'git reset', 'git checkout', 'git pull'],
    answer: 'AB',
    type: 'multiple',
    score: 8
  },
  {
    id: 23,
    question: 'JavaScript中，以下哪些是数据类型？',
    options: ['string', 'number', 'boolean', 'symbol', 'undefined', 'null'],
    answer: 'ABCDEF',
    type: 'multiple',
    score: 8
  },
  {
    id: 24,
    question: 'Vue3中，以下哪些是组合式API的钩子函数？',
    options: ['onMounted', 'onUpdated', 'onUnmounted', 'onLoad', 'onInit'],
    answer: 'ABC',
    type: 'multiple',
    score: 8
  },
  {
    id: 25,
    question: 'HTML5中，以下哪些是新增的语义化标签？',
    options: ['<header>', '<nav>', '<article>', '<div>', '<section>'],
    answer: 'ABCE',
    type: 'multiple',
    score: 8
  }
])

const currentQuestion = computed(() => questions.value[currentIndex.value])
const answeredCount = computed(() => Object.keys(answers.value).length)

onMounted(async () => {
  try {
    const nicknameRes = await getNickname()
    username.value = nicknameRes.nickname || '用户'
  } catch (error) {
    console.error('获取用户信息失败:', error)
    username.value = '用户'
  }

  // 开始倒计时
  timer = setInterval(() => {
    if (remainingTime.value > 0) {
      remainingTime.value--
    } else {
      clearInterval(timer)
      submitExam()
    }
  }, 1000)
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})

const formatTime = (seconds) => {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
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
    answers.value[currentIndex.value] = label
  } else {
    if (current.includes(label)) {
      answers.value[currentIndex.value] = current.replace(label, '')
    } else {
      answers.value[currentIndex.value] = (current + label).split('').sort().join('')
    }
  }
}

const selectJudge = (value) => {
  answers.value[currentIndex.value] = value
}

const goToQuestion = (index) => {
  currentIndex.value = index
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

const confirmSubmit = () => {
  showSubmitDialog.value = false
  calculateScore()
  showResultDialog.value = true
}

const calculateScore = () => {
  let totalScore = 0
  let correctCount = 0
  let wrongCount = 0
  let unansweredCount = 0

  questions.value.forEach((q, index) => {
    const userAnswer = answers.value[index]
    if (!userAnswer) {
      unansweredCount++
    } else if (userAnswer === q.answer) {
      totalScore += q.score
      correctCount++
    } else {
      wrongCount++
    }
  })

  examResult.value = {
    totalScore,
    correctCount,
    wrongCount,
    unansweredCount,
    accuracy: Math.round((correctCount / questions.value.length) * 100)
  }
}

const closeResultDialog = () => {
  showResultDialog.value = false
  router.push('/exam-center')
}

const goBack = () => {
  if (timer) {
    clearInterval(timer)
  }
  router.back()
}
</script>

<style scoped>
.exam-test-page {
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
  transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
  transform-origin: right center;
}

.side-nav.collapsed {
  width: 0;
  transform: scaleX(0);
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
  width: 28px;
  height: 28px;
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
}

.side-nav-btn:hover {
  border-color: #8DC149;
  color: #8DC149;
  transform: scale(1.05);
}

.side-nav-btn.active {
  background: #8DC149;
  color: white;
  border-color: #8DC149;
}

.side-nav-btn.answered:not(.active) {
  background: #e6f7ee;
  border-color: #8DC149;
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
  border: 1px solid #8DC149;
}

.legend-item .dot.current {
  background: #8DC149;
}

.legend-item .dot.unanswered {
  background: white;
  border: 1px solid #ddd;
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
  background: #e6f7ee;
  color: #228b22;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
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
  border-color: #8DC149;
  background: #f6fff3;
}

.option-item.selected {
  border-color: #8DC149;
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
  background: #8DC149;
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
  border-color: #8DC149;
}

.judge-item.selected {
  border-color: #8DC149;
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
  background: linear-gradient(145deg, #8DC149, #6ab82a);
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
  color: #8DC149;
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
  background: linear-gradient(90deg, #8DC149, #a8d46e, #8DC149);
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
  background: linear-gradient(135deg, #8DC149, #7ab838) !important;
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
