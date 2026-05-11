<template>
  <div class="mock-test-page">
    <!-- 顶部标题栏 -->
    <div class="header">
      <div class="header-left">
        <el-button link @click="goBack" class="back-btn">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
      </div>
      <div class="header-title">
        <h2>AI 冠军教练 · 模拟测试</h2>
      </div>
      <div class="header-right">
        <span class="username">{{ username }}</span>
        <span class="mode-tag">练习模式</span>
      </div>
    </div>

    <!-- 主体内容区域 -->
    <div class="content">
      <div class="exam-container">
        <!-- 加载状态 -->
        <div v-if="isLoading" class="loading-container">
          <el-icon class="loading-spinner"><Loading /></el-icon>
          <p>题目加载中...</p>
        </div>
        
        <template v-else>
        <!-- 模式说明 -->
        <div class="mode-info">
          <el-icon class="info-icon"><HelpFilled /></el-icon>
          <div class="info-text">
            <h3>练习模式说明</h3>
            <p>模拟测试为练习模式，答题后可即时查看答案和解析，不计入正式成绩。</p>
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
              :class="['option-item', { 
                selected: isSelected(optIndex), 
                correct: showResult[currentIndex] && isCorrectOption(optIndex),
                wrong: showResult[currentIndex] && isSelected(optIndex) && !isCorrectOption(optIndex)
              }]"
              @click="selectOption(optIndex)"
            >
              <span class="option-label">{{ ['A', 'B', 'C', 'D'][optIndex] }}</span>
              <span class="option-text">{{ opt }}</span>
              <span v-if="showResult[currentIndex] && isCorrectOption(optIndex)" class="result-icon correct">✓</span>
              <span v-if="showResult[currentIndex] && isSelected(optIndex) && !isCorrectOption(optIndex)" class="result-icon wrong">✗</span>
            </div>
          </div>

          <!-- 判断题选项 -->
          <div class="judge-options" v-else>
            <div
              :class="['judge-item', { 
                selected: answers[currentIndex] === '正确',
                correct: showResult[currentIndex] && currentQuestion.answer === '正确',
                wrong: showResult[currentIndex] && answers[currentIndex] === '正确' && currentQuestion.answer !== '正确'
              }]"
              @click="selectJudge('正确')"
            >
              <span class="judge-icon correct">✓</span>
              <span>正确</span>
              <span v-if="showResult[currentIndex] && currentQuestion.answer === '正确'" class="result-text">正确答案</span>
            </div>
            <div
              :class="['judge-item', { 
                selected: answers[currentIndex] === '错误',
                correct: showResult[currentIndex] && currentQuestion.answer === '错误',
                wrong: showResult[currentIndex] && answers[currentIndex] === '错误' && currentQuestion.answer !== '错误'
              }]"
              @click="selectJudge('错误')"
            >
              <span class="judge-icon wrong">✗</span>
              <span>错误</span>
              <span v-if="showResult[currentIndex] && currentQuestion.answer === '错误'" class="result-text">正确答案</span>
            </div>
          </div>

          <!-- 答案解析 -->
          <div v-if="showResult[currentIndex]" class="answer-analysis">
            <h4>答案解析</h4>
            <p><strong>正确答案：</strong>{{ currentQuestion.answer }}</p>
            <p><strong>解析：</strong>{{ currentQuestion.analysis }}</p>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button :disabled="currentIndex === 0" @click="prevQuestion">上一题</el-button>
          <template v-if="!showResult[currentIndex]">
            <el-button type="primary" @click="checkAnswer">查看答案</el-button>
          </template>
          <template v-else-if="currentIndex < questions.length - 1">
            <el-button type="primary" @click="nextQuestion">下一题</el-button>
          </template>
          <template v-else>
            <el-button type="primary" @click="resetExam">重新开始</el-button>
          </template>
        </div>
        </template>
      </div>
    </div>

    <!-- 侧边浮窗题目导航 -->
    <div class="side-nav">
      <div class="side-nav-header">
        <span>题目导航</span>
      </div>
      <div class="side-nav-grid">
        <button
          v-for="(q, index) in questions"
          :key="index"
          :class="['side-nav-btn', { 
            active: currentIndex === index, 
            answered: answers[index],
            correct: showResult[index] && answers[index] === getCorrectAnswer(index), 
            wrong: showResult[index] && answers[index] && answers[index] !== getCorrectAnswer(index) 
          }]"
          @click="goToQuestion(index)"
        >
          {{ index + 1 }}
        </button>
      </div>
      <div class="side-nav-legend">
        <div class="legend-item"><span class="dot correct"></span>答对</div>
        <div class="legend-item"><span class="dot wrong"></span>答错</div>
        <div class="legend-item"><span class="dot current"></span>当前</div>
        <div class="legend-item"><span class="dot unanswered"></span>未答</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getNickname } from '../api/user'
import { getQuestionList } from '../api/question'
import { ElMessage } from 'element-plus'
import { ArrowLeft, HelpFilled, Loading } from '@element-plus/icons-vue'

const router = useRouter()

const username = ref('')
const currentIndex = ref(0)
const answers = ref({})
const showResult = ref({})
const isLoading = ref(true)
const questions = ref([])

const currentQuestion = computed(() => questions.value[currentIndex.value])

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
    }
  }
  return options
}

onMounted(async () => {
  try {
    const nicknameRes = await getNickname()
    username.value = nicknameRes.nickname || '用户'
    
    const res = await getQuestionList({ page: 1, page_size: 100 })
    if (res.success && res.questions) {
      questions.value = res.questions.map(q => ({
        id: q.id,
        question: q.question,
        options: parseOptions(q.options),
        answer: q.answer,
        type: q.type,
        category: q.category,
        analysis: q.analysis || ''
      }))
    }
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    isLoading.value = false
  }
})

const getTypeName = (type) => {
  const types = {
    single: '单选题',
    multiple: '多选题',
    judge: '判断题'
  }
  return types[type] || '未知类型'
}

const getCorrectAnswer = (index) => {
  return questions.value[index].answer
}

const isSelected = (optIndex) => {
  const answer = answers.value[currentIndex.value]
  if (!answer) return false
  const label = ['A', 'B', 'C', 'D'][optIndex]
  return answer.includes(label)
}

const isCorrectOption = (optIndex) => {
  const correctAnswer = currentQuestion.value.answer
  const label = ['A', 'B', 'C', 'D'][optIndex]
  return correctAnswer.includes(label)
}

const selectOption = (optIndex) => {
  if (showResult.value[currentIndex.value]) return
  
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
  if (showResult.value[currentIndex.value]) return
  answers.value[currentIndex.value] = value
}

const goToQuestion = (index) => {
  currentIndex.value = index
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

const checkAnswer = () => {
  if (!answers.value[currentIndex.value]) {
    ElMessage.warning('请先选择答案')
    return
  }
  showResult.value[currentIndex.value] = true
}

const resetExam = () => {
  currentIndex.value = 0
  answers.value = {}
  showResult.value = {}
}

const goBack = () => {
  router.back()
}
</script>

<style scoped>
.mock-test-page {
  min-height: 100vh;
  background: #e8f5e9;
}

.header {
  height: 80px;
  background: linear-gradient(135deg, #FFD700, #FFA500);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
  box-shadow: 0 4px 20px rgba(255, 215, 0, 0.3);
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

.mode-tag {
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

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: #666;
}

.loading-spinner {
  font-size: 40px;
  color: var(--primary-color);
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-container p {
  margin-top: 16px;
  font-size: 16px;
}

.mode-info {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(135deg, #fff9c4, #fff59d);
  border-radius: 12px;
  margin-bottom: 30px;
  border: 1px solid #ffe082;
}

.info-icon {
  font-size: 28px;
  color: #ff9800;
  flex-shrink: 0;
}

.info-text h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #e65100;
}

.info-text p {
  margin: 0;
  font-size: 14px;
  color: #bf360c;
  line-height: 1.5;
}

/* 侧边浮窗题目导航 */
.side-nav {
  position: fixed;
  right: 30px;
  top: 50%;
  transform: translateY(-50%);
  width: 200px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  padding: 16px;
  z-index: 100;
  overflow: hidden;
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
  border-color: #FFD700;
  color: #FFD700;
  transform: scale(1.05);
}

.side-nav-btn.active {
  background: #FFD700;
  color: #8B4513;
  border-color: #FFD700;
}

.side-nav-btn.answered:not(.active) {
  background: #fff9c4;
  border-color: #FFD700;
  color: #8B4513;
}

.side-nav-btn.correct {
  background: #81c784;
  color: white;
  border-color: #81c784;
}

.side-nav-btn.wrong {
  background: #ef5350;
  color: white;
  border-color: #ef5350;
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

.legend-item .dot.correct {
  background: #81c784;
}

.legend-item .dot.wrong {
  background: #ef5350;
}

.legend-item .dot.current {
  background: #FFD700;
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
  background: #fff9c4;
  color: #8B4513;
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

.option-item:hover:not(.correct):not(.wrong) {
  border-color: #FFD700;
  background: #fffde7;
}

.option-item.selected {
  border-color: #FFD700;
  background: #fffde7;
}

.option-item.correct {
  border-color: #81c784;
  background: #e8f5e9;
}

.option-item.wrong {
  border-color: #ef5350;
  background: #ffebee;
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
  background: #FFD700;
  color: #8B4513;
}

.option-item.correct .option-label {
  background: #81c784;
  color: white;
}

.option-item.wrong .option-label {
  background: #ef5350;
  color: white;
}

.option-text {
  font-size: 16px;
  color: #333;
  line-height: 1.5;
  flex: 1;
}

.result-icon {
  font-size: 20px;
  font-weight: 700;
  flex-shrink: 0;
}

.result-icon.correct {
  color: #81c784;
}

.result-icon.wrong {
  color: #ef5350;
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

.judge-item:hover:not(.correct):not(.wrong) {
  border-color: #FFD700;
}

.judge-item.selected {
  border-color: #FFD700;
  background: #fffde7;
}

.judge-item.correct {
  border-color: #81c784;
  background: #e8f5e9;
}

.judge-item.wrong {
  border-color: #ef5350;
  background: #ffebee;
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

.result-text {
  font-size: 12px;
  color: #52c41a;
  font-weight: 500;
}

.answer-analysis {
  margin-top: 30px;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 10px;
}

.answer-analysis h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.answer-analysis p {
  margin: 8px 0;
  font-size: 14px;
  line-height: 1.6;
  color: #555;
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

  .judge-options {
    flex-direction: column;
  }
}
</style>
