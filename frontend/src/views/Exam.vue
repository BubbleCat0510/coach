<template>
	<div class="exam-container">
		<!-- 加载状态 -->
		<div v-if="loading" class="loading-overlay">
			<div class="loading-content">
				<div class="loading-icon">🎯</div>
				<h2 class="loading-title">正在准备测试</h2>
				<p class="loading-message">{{ loadingMessage }}</p>
				<div class="loading-progress">
					<div class="progress-bar">
						<div class="progress-fill" :style="{ width: loadingProgress + '%' }"></div>
					</div>
					<span class="progress-text">{{ loadingProgress }}%</span>
				</div>
			</div>
		</div>

		<!-- ========== 顶部导航 ========== -->
		<header class="exam-header">
			<div class="header-background">
				<div class="header-pattern"></div>
				<div class="header-gradient"></div>
			</div>
			<div class="header-content">
				<div class="header-main">
					<div class="header-icon">🎯</div>
					<div class="header-text">
						<h1 class="header-title">能力评估中心</h1>
						<p class="header-subtitle">检验学习成果 · 提升专业能力 · 成就卓越表现</p>
					</div>
				</div>
				<div class="header-actions">
					<el-button
						type="primary"
						size="large"
						@click="startNewExam"
						:disabled="!hasAvailableExams"
						class="action-btn primary"
					>
						<el-icon><VideoPlay /></el-icon>
						开始测试
					</el-button>
					<el-button
						size="large"
						@click="viewHistory"
						class="action-btn secondary"
					>
						<el-icon><DataAnalysis /></el-icon>
						历史成绩
					</el-button>
					<el-button
						size="large"
						@click="backToDashboard"
						class="action-btn back-btn"
					>
						<el-icon><ArrowLeft /></el-icon>
						返回主页
					</el-button>
				</div>
			</div>
		</header>

		<!-- ========== 主要内容区域 ========== -->
		<main class="exam-main">
			<!-- 测试模式选择 -->
			<section class="exam-section mode-selection" v-if="!examStarted && !showHistory">
				<div class="section-container">
					<div class="section-header">
						<div class="section-title">
							<el-icon class="title-icon"><Aim /></el-icon>
							<h2>选择测试模式</h2>
						</div>
						<p class="section-desc">根据你的需求选择合适的测试类型，开启能力提升之旅</p>
					</div>

					<div class="mode-grid">
						<!-- 专项能力测试 -->
						<div class="mode-card premium" @click="selectExamMode('specialized')">
							<div class="card-background">
								<div class="card-pattern"></div>
							</div>
							<div class="card-content">
								<div class="card-header">
									<div class="card-icon">🎯</div>
									<div class="card-badge recommended">推荐</div>
								</div>
								<div class="card-body">
									<h3 class="card-title">专项能力测试</h3>
									<p class="card-desc">针对特定岗位技能进行深度评估，精准定位能力短板</p>
									<div class="card-features">
										<span class="feature-tag"><el-icon><DocumentChecked /></el-icon>理论知识</span>
										<span class="feature-tag"><el-icon><Search /></el-icon>案例分析</span>
										<span class="feature-tag"><el-icon><Setting /></el-icon>技能操作</span>
									</div>
								</div>
								<div class="card-footer">
									<span class="card-action">开始测试 <el-icon><ArrowRight /></el-icon></span>
								</div>
							</div>
						</div>

						<!-- 综合能力测试 -->
						<div class="mode-card standard" @click="selectExamMode('comprehensive')">
							<div class="card-background">
								<div class="card-pattern"></div>
							</div>
							<div class="card-content">
								<div class="card-header">
									<div class="card-icon">🏆</div>
									<div class="card-badge popular">热门</div>
								</div>
								<div class="card-body">
									<h3 class="card-title">综合能力测试</h3>
									<p class="card-desc">全方位业务能力综合评估，绘制完整能力画像</p>
									<div class="card-features">
										<span class="feature-tag"><el-icon><DataLine /></el-icon>多维度评估</span>
										<span class="feature-tag"><el-icon><PieChart /></el-icon>能力画像</span>
										<span class="feature-tag"><el-icon><MagicStick /></el-icon>学习建议</span>
									</div>
								</div>
								<div class="card-footer">
									<span class="card-action">开始测试 <el-icon><ArrowRight /></el-icon></span>
								</div>
							</div>
						</div>

						<!-- 模拟实战测试 -->
						<div class="mode-card challenge" @click="selectExamMode('simulation')">
							<div class="card-background">
								<div class="card-pattern"></div>
							</div>
							<div class="card-content">
								<div class="card-header">
									<div class="card-icon">🎭</div>
									<div class="card-badge challenge">挑战</div>
								</div>
								<div class="card-body">
									<h3 class="card-title">模拟实战测试</h3>
									<p class="card-desc">真实业务场景实战模拟，检验实际工作能力</p>
									<div class="card-features">
										<span class="feature-tag"><el-icon><Monitor /></el-icon>场景模拟</span>
										<span class="feature-tag"><el-icon><Management /></el-icon>决策能力</span>
										<span class="feature-tag"><el-icon><Lightning /></el-icon>应变能力</span>
									</div>
								</div>
								<div class="card-footer">
									<span class="card-action">开始测试 <el-icon><ArrowRight /></el-icon></span>
								</div>
							</div>
						</div>
					</div>
				</div>
			</section>

			<!-- 测试进行中 -->
			<section class="exam-section exam-process" v-if="examStarted && !examCompleted">
				<div class="exam-wrapper">
					<!-- 进度条 -->
					<div class="exam-progress">
						<div class="progress-header">
							<div class="progress-info">
								<h3 class="exam-title">{{ currentExam.title }}</h3>
								<div class="progress-stats">
									<span class="progress-current">{{ currentQuestionIndex + 1 }}</span>
									<span class="progress-separator">/</span>
									<span class="progress-total">{{ currentExam.questions.length }}</span>
									<span class="progress-score">(总分：{{ SCORE_CONFIG.total }})</span>
								</div>
							</div>
							<div class="progress-percentage">{{ progressPercentage }}%</div>
						</div>
						<div class="progress-bar">
							<div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
						</div>
					</div>

					<!-- 题目内容 -->
					<div class="exam-content">
						<!-- 单选题 -->
						<div v-if="currentQuestion.type === 'single'" class="question-container">
							<div class="question-header">
								<div class="question-type">
									<el-icon><Select /></el-icon>
									单选题（{{ SCORE_CONFIG.single }}分）
								</div>
								<div class="question-number">第 {{ currentQuestionIndex + 1 }} 题</div>
							</div>
							<div class="question-content">
								<div class="question-text">{{ currentQuestion.question }}</div>
								<div class="question-options">
									<div
										v-for="(option, index) in currentQuestion.options"
										:key="index"
										class="option-item"
										:class="{ selected: selectedAnswer === option.id }"
										@click="selectAnswer(option.id)"
									>
                                        <div class="radio-outer">
                                            <div class="radio-inner" v-if="selectedAnswer === option.id"></div>
                                        </div>
										<div class="option-content">
											<div class="option-label">{{ String.fromCharCode(65 + index) }}</div>
											<div class="option-text">{{ option.text }}</div>
										</div>
									</div>
								</div>
							</div>
						</div>

						<!-- 多选题 -->
						<div v-else-if="currentQuestion.type === 'multiple'" class="question-container">
							<div class="question-header">
								<div class="question-type">
									<el-icon><Check /></el-icon>
									多选题（{{ SCORE_CONFIG.multiple }}分）
								</div>
								<div class="question-number">第 {{ currentQuestionIndex + 1 }} 题</div>
							</div>
							<div class="question-content">
								<div class="question-text">{{ currentQuestion.question }}</div>
								<div class="question-options">
									<div
										v-for="(option, index) in currentQuestion.options"
										:key="index"
										class="option-item multiple"
										:class="{ selected: selectedAnswers.includes(option.id) }"
										@click="toggleMultipleAnswer(option.id)"
									>
                                        <div class="checkbox-outer">
                                            <el-icon v-if="selectedAnswers.includes(option.id)" class="checkbox-check"><Check /></el-icon>
                                        </div>
										<div class="option-content">
											<div class="option-label">{{ String.fromCharCode(65 + index) }}</div>
											<div class="option-text">{{ option.text }}</div>
										</div>
									</div>
								</div>
							</div>
						</div>

						<!-- 判断题 -->
						<div v-else-if="currentQuestion.type === 'truefalse'" class="question-container">
							<div class="question-header">
								<div class="question-type">
									<el-icon><QuestionFilled /></el-icon>
									判断题（{{ SCORE_CONFIG.truefalse }}分）
								</div>
								<div class="question-number">第 {{ currentQuestionIndex + 1 }} 题</div>
							</div>
							<div class="question-content">
								<div class="question-text">{{ currentQuestion.question }}</div>
								<div class="question-options truefalse">
									<div
										class="option-item truefalse-option"
										:class="{ selected: selectedAnswer === 'true' }"
										@click="selectAnswer('true')"
									>
										<div class="option-icon correct">
											<el-icon><CircleCheck /></el-icon>
										</div>
										<div class="option-text">正确</div>
									</div>
									<div
										class="option-item truefalse-option"
										:class="{ selected: selectedAnswer === 'false' }"
										@click="selectAnswer('false')"
									>
										<div class="option-icon incorrect">
											<el-icon><CircleClose /></el-icon>
										</div>
										<div class="option-text">错误</div>
									</div>
								</div>
							</div>
						</div>

						<!-- 案例分析题 -->
						<div v-else-if="currentQuestion.type === 'case'" class="question-container">
							<div class="question-header">
								<div class="question-type">
									<el-icon><DocumentCopy /></el-icon>
									案例分析（{{ SCORE_CONFIG.case }}分）
								</div>
								<div class="question-number">第 {{ currentQuestionIndex + 1 }} 题</div>
							</div>
							<div class="question-content">
								<div class="question-text">{{ currentQuestion.question }}</div>
								<div v-if="currentQuestion.scenario" class="case-scenario">
									<div class="scenario-header">
										<el-icon><Document /></el-icon>
										<span>案例背景</span>
									</div>
									<div class="scenario-content">{{ currentQuestion.scenario }}</div>
								</div>
								<div class="case-answer">
									<div class="answer-header">
										<el-icon><EditPen /></el-icon>
										<span>你的分析</span>
									</div>
									<el-input
										v-model="caseAnswer"
										type="textarea"
										:rows="8"
										placeholder="请详细分析这个案例，并给出你的解决方案..."
										maxlength="2000"
										show-word-limit
										class="answer-input"
									/>
								</div>
							</div>
						</div>
					</div>

					<!-- 操作按钮 -->
					<div class="exam-actions">
						<el-button
							v-if="currentQuestionIndex > 0"
							@click="previousQuestion"
							:disabled="submitting"
							class="nav-btn prev"
						>
							<el-icon><ArrowLeft /></el-icon>
							上一题
						</el-button>
						<div class="spacer"></div>
						<el-button
							type="primary"
							@click="nextQuestion"
							:loading="submitting || batchSubmitting"
							:disabled="!hasSelectedAnswer"
							class="submit-btn"
						>
							{{ isLastQuestion ? '提交答案' : '下一题' }}
							<el-icon><ArrowRight /></el-icon>
						</el-button>
					</div>
				</div>
			</section>

			<!-- 测试结果 -->
			<section class="exam-section exam-result" v-if="examCompleted">
				<div class="result-container">
					<!-- 成绩总览 -->
					<div class="result-header">
						<div class="result-celebration">
							<div class="celebration-icon">🎉</div>
							<h2 class="result-title">测试完成！</h2>
							<p class="result-desc">恭喜你完成了本次能力评估</p>
						</div>
					</div>

					<!-- 成绩卡片 -->
					<div class="score-card">
						<div class="score-main">
							<div class="score-circle">
								<div class="score-number">{{ examResult.totalScore }}</div>
								<div class="score-label">总分</div>
							</div>
							<div class="score-details">
								<div class="score-item">
									<div class="score-value">{{ examResult.accuracy }}%</div>
									<div class="score-label">正确率</div>
								</div>
								<div class="score-item">
									<div class="score-value">{{ formatTime(examResult.timeSpent) }}</div>
									<div class="score-label">用时</div>
								</div>
								<div class="score-item">
									<div class="score-value level" :class="examResult.level">{{ examResult.level }}</div>
									<div class="score-label">等级</div>
								</div>
							</div>
						</div>
					</div>

					<!-- 能力分析 -->
					<div class="abilities-section">
						<div class="section-title">
							<el-icon><PieChart /></el-icon>
							<h3>能力分析</h3>
						</div>
						<div class="abilities-grid">
							<div
								v-for="ability in examResult.abilities"
								:key="ability.name"
								class="ability-item"
							>
								<div class="ability-header">
									<span class="ability-name">{{ ability.name }}</span>
									<span class="ability-score">{{ ability.score }}%</span>
								</div>
								<div class="ability-bar">
									<div
										class="ability-fill"
										:style="{
											width: ability.score + '%',
											backgroundColor: getAbilityColor(ability.score)
										}"
									></div>
								</div>
							</div>
						</div>
					</div>

					<!-- 学习建议 -->
					<div class="suggestions-section">
						<div class="section-title">
							<el-icon><Comment /></el-icon>
							<h3>学习建议</h3>
						</div>
						<div class="suggestions-list">
							<div
								v-for="(suggestion, index) in examResult.suggestions"
								:key="index"
								class="suggestion-item"
							>
								<div class="suggestion-icon">{{ suggestion.icon }}</div>
								<div class="suggestion-content">
									<h4 class="suggestion-title">{{ suggestion.title }}</h4>
									<p class="suggestion-desc">{{ suggestion.description }}</p>
								</div>
							</div>
						</div>
					</div>

					<!-- 行动按钮 -->
					<div class="result-actions">
						<el-button type="primary" @click="reviewAnswers" class="action-btn primary">
							<el-icon><View /></el-icon>
							查看解析
						</el-button>
						<el-button @click="retakeExam" :disabled="!canRetake" class="action-btn secondary">
							<el-icon><Refresh /></el-icon>
							重新测试
						</el-button>
						<el-button @click="continueLearning" class="action-btn outline">
							<el-icon><Reading /></el-icon>
							继续学习
						</el-button>
					</div>
				</div>
			</section>

			<!-- 测试历史 -->
			<section class="exam-section history-section" v-if="showHistory">
				<div class="history-container">
					<div class="history-header">
						<div class="section-title">
							<el-icon><DataAnalysis /></el-icon>
							<h2>测试历史</h2>
						</div>
						<p class="section-desc">查看你的学习进步轨迹</p>
					</div>

					<div class="history-filters">
						<el-select v-model="historyFilter" placeholder="选择时间范围" size="large">
							<el-option label="全部" value="all" />
							<el-option label="最近7天" value="week" />
							<el-option label="最近30天" value="month" />
						</el-select>
					</div>

					<div class="history-list">
						<div
							v-for="record in filteredHistory"
							:key="record.id"
							class="history-item"
							@click="viewHistoryDetail(record)"
						>
							<div class="history-icon">
								<el-icon><Trophy /></el-icon>
							</div>
							<div class="history-content">
								<div class="history-title">{{ record.title }}</div>
								<div class="history-meta">
									<span class="history-date">{{ record.date }}</span>
									<span class="history-time">{{ record.timeSpent }}</span>
								</div>
							</div>
							<div class="history-score">
								<div class="score-display">{{ record.score }}</div>
								<div class="score-level" :class="record.level">{{ record.level }}</div>
							</div>
						</div>
					</div>

					<div v-if="filteredHistory.length === 0" class="no-history">
						<div class="empty-state">
							<el-icon class="empty-icon"><Document /></el-icon>
							<h3>暂无测试记录</h3>
							<p>开始你的第一次测试，开启学习之旅吧！</p>
							<el-button type="primary" size="large" @click="startNewExam">
								<el-icon><VideoPlay /></el-icon>
								开始第一次测试
							</el-button>
						</div>
					</div>
				</div>
			</section>
		</main>

		<!-- ========== 答案解析弹窗 ========== -->
		<el-dialog
			v-model="reviewDialog.visible"
			title="📖 答案解析"
			width="900px"
			:before-close="closeReviewDialog"
			class="review-dialog"
		>
			<div class="review-content">
				<div
					v-for="(question, index) in currentExam.questions"
					:key="index"
					class="review-question"
				>
					<div class="question-header">
						<span class="question-number">Q{{ index + 1 }}</span>
						<span class="question-type">{{ getQuestionTypeText(question.type) }}</span>
						<span class="question-status" :class="getAnswerStatus(question, examAnswers[index])">
							{{ getAnswerStatusText(question, examAnswers[index]) }}
						</span>
					</div>

					<div class="question-content">{{ question.question }}</div>

					<div v-if="question.scenario" class="question-scenario">
						<strong>📋 案例背景：</strong>{{ question.scenario }}
					</div>

					<div class="answer-analysis">
						<div class="user-answer">
							<strong>👤 你的答案：</strong>
							<span v-if="question.type === 'case'">{{ examAnswers[index] || '未作答' }}</span>
							<span v-else>{{ formatAnswer(examAnswers[index], question) }}</span>
						</div>

						<div class="correct-answer">
							<strong>✅ 正确答案：</strong>
							<span>{{ formatAnswer(question.correctAnswer, question) }}</span>
						</div>

						<div class="explanation">
							<strong>💡 解析：</strong>
							<p>{{ question.explanation }}</p>
						</div>
					</div>
				</div>
			</div>
		</el-dialog>
	</div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
	startExam as apiStartExam,
	submitExamAnswer,
	finishExam,
	getExamResult
} from '../api/exam'
import { 
  chatWithCoachQuestion,
  getCaseExamScore
} from '../api/aiCoach'
import { getUserRole } from '../api/user'

const router = useRouter()

// ========== 分值配置常量（确认的100分标准） ==========
const SCORE_CONFIG = {
  // 单题分值
  single: 2,        // 单选题：2分/题
  multiple: 4,      // 多选题：4分/题
  truefalse: 2,     // 判断题：2分/题
  case: 10,         // 案例分析题：10分/题
  // 总分
  total: 100,
  // 等级判定阈值
  levels: {
    expert: 90,     // 专家：≥90分
    advanced: 80,   // 高级：80-89分
    intermediate: 70,// 中级：70-79分
    primary: 60,    // 初级：60-69分
    beginner: 0     // 入门：<60分
  },
  // 各模式题目数量配置
  modeQuestions: {
    specialized: [  // 专项能力测试：总分2*10 + 10*8 = 100
      { qtype: 'single', count: 10 },
      { qtype: 'case', count: 8 }
    ],
    comprehensive: [ // 综合能力测试：2*9 + 4*3 + 2*5 + 10*6 = 100
      { qtype: 'single', count: 9 },
      { qtype: 'multiple', count: 3 },
      { qtype: 'truefalse', count: 5 },
      { qtype: 'case', count: 6 }
    ],
    simulation: [   // 模拟实战测试：10*10 = 100
      { qtype: 'case', count: 10 }
    ]
  }
}

// 状态
const examStarted = ref(false)
const examCompleted = ref(false)
const showHistory = ref(false)
const submitting = ref(false)
const batchSubmitting = ref(false) // 新增：批量提交加载状态
const answerCache = ref({}) // 新增：本地缓存所有题目答案（key: 题目索引，value: 答案）
const currentScore = ref(0)	// 当前得分
const loading = ref(false) // 新增：加载状态
const loadingProgress = ref(0) // 新增：加载进度
const loadingMessage = ref('') // 新增：加载提示信息

const currentExam = reactive({
	session_id: null,
	title: '',
	type: '',
	questions: [],
	startTime: null,
	endTime: null,
  dimensions: [] // 新增：能力维度列表
})

// 答题状态
const currentQuestionIndex = ref(0)
const selectedAnswer = ref('')
const selectedAnswers = ref([])
const caseAnswer = ref('')

const examResult = reactive({
	totalScore: 0,
	accuracy: 0,
	timeSpent: 0,
	level: '',
	abilities: [],
	suggestions: []
})

const examAnswers = ref([])

const examHistory = ref([])
const historyFilter = ref('all')

const reviewDialog = reactive({
	visible: false
})

const confirmExitTest = async () => {
	try{
		await ElMessageBox.confirm(
			'当前测试尚未完成，确定要退出吗？未提交的答案将不会被保存。',
			'确认退出测试',
			{
				confirmButtonText: '退出测试',
				cancelButtonText: '继续答题',
				type: 'warning',
				closeOnClickModal: false,
				closeOnPressEscape: false
			}
		)
		return true
	} catch {
		// 用户点击取消退出，提示+阻止操作
		ElMessage.info('继续答题')
		return false
	}
}

const currentQuestion = computed(() => {
	return currentExam.questions[currentQuestionIndex.value] || {}
})

const progressPercentage = computed(() => {
	if (currentExam.questions.length === 0) return 0
	return Math.round(((currentQuestionIndex.value + 1) / currentExam.questions.length) * 100)
})

const isLastQuestion = computed(() => {
	return currentQuestionIndex.value === currentExam.questions.length - 1
})

const hasSelectedAnswer = computed(() => {
	if (currentQuestion.value.type === 'multiple') {
		return selectedAnswers.value.length > 0
	}
	if (currentQuestion.value.type === 'case') {
		return !!caseAnswer.value.trim()
	}
	return selectedAnswer.value !== ''
})

const hasAvailableExams = computed(() => true)
const canRetake = computed(() => true)

const filteredHistory = computed(() => {
	const now = new Date()
	let filterDate = new Date()
	switch (historyFilter.value) {
		case 'week':
			filterDate.setDate(now.getDate() - 7)
			break
		case 'month':
			filterDate.setDate(now.getDate() - 30)
			break
		default:
			return examHistory.value
	}
	return examHistory.value.filter(record => new Date(record.date) >= filterDate)
})

// 工具函数
const getQuestionTypeText = (type) => {
	const typeMap = {
		single: '单选题',
		multiple: '多选题',
		truefalse: '判断题',
		case: '案例分析'
	}
	return typeMap[type] || '未知类型'
}

const getAnswerStatus = (question, answer) => {
	if (!answer) return 'unanswered'
	if (question.type === 'case') return 'answered'
	if (question.type === 'multiple') {
		const correctAnswers = Array.isArray(question.correctAnswer) ? question.correctAnswer : [question.correctAnswer]
		const isCorrect = JSON.stringify(answer.sort()) === JSON.stringify(correctAnswers.sort())
		return isCorrect ? 'correct' : 'incorrect'
	} else {
		return answer === question.correctAnswer ? 'correct' : 'incorrect'
	}
}

const getAnswerStatusText = (question, answer) => {
	const status = getAnswerStatus(question, answer)
	const statusMap = {
		correct: '✓ 正确',
		incorrect: '✗ 错误',
		unanswered: '未作答',
		answered: '已作答'
	}
	return statusMap[status] || '未知'
}

const formatAnswer = (answer, question) => {
	if (!answer) return '未作答'
	if (question.type === 'truefalse') {
		return answer === 'true' ? '正确' : '错误'
	}
	if (question.type === 'multiple') {
		if (Array.isArray(answer)) {
			return answer.map(id => {
				const option = question.options?.find(opt => opt.id === id)
				return option ? `${String.fromCharCode(65 + question.options.indexOf(option))}. ${option.text}` : id
			}).join('；')
		}
	}
	if (question.type === 'single') {
		const option = question.options?.find(opt => opt.id === answer)
		if (option) {
			const index = question.options.indexOf(option)
			return `${String.fromCharCode(65 + index)}. ${option.text}`
		}
	}
	return answer
}

const formatTime = (seconds) => {
	const mins = Math.floor(seconds / 60)
	const secs = seconds % 60
	return `${mins}分${secs}秒`
}

const getAbilityColor = (score) => {
	if (score >= 80) return '#67C23A'
	if (score >= 60) return '#E6A23C'
	return '#F56C6C'
}

// 新增：计算单题得分
const calculateQuestionScore = (question, answer) => {
  if (!question || !answer) return 0
  // 获取该题型分值
  const questionScore = SCORE_CONFIG[question.type] || 0
  
  // 判断答案是否正确
  let isCorrect = false
  if (question.type === 'multiple') {
    const correctAnswers = Array.isArray(question.correctAnswer) ? question.correctAnswer : [question.correctAnswer]
    isCorrect = JSON.stringify(answer.sort()) === JSON.stringify(correctAnswers.sort())
  } else if (question.type === 'truefalse' || question.type === 'single') {
    isCorrect = answer === question.correctAnswer
  } else if (question.type === 'case') {
    // 案例题暂按“已作答即得分”（可后续对接后端评分）
    isCorrect = answer.trim() ? SCORE_CONFIG.case : 0
  }
  
  return isCorrect ? questionScore : 0
}

// 新增：计算当前总得分
const calculateTotalScore = () => {
  let total = 0
  Object.keys(answerCache.value).forEach(index => {
    const question = currentExam.questions[Number(index)]
    const answer = answerCache.value[index]
    total += calculateQuestionScore(question, answer)
  })
  currentScore.value = total
  return total
}

const getExamTitle = (mode) => {
	const titleMap = {
		specialized: '专项能力测试',
		comprehensive: '综合能力测试',
		simulation: '模拟实战测试'
	}
	return titleMap[mode] || '能力测试'
}

// 1️⃣ 开始考试（调用后端，保存 session_id，不再本地生成题目）
const selectExamMode = async (mode) => {
	const modeConfig = {
		specialized: {
			title: '专项能力测试',
			description: '针对特定岗位技能进行深度评估'
		},
		comprehensive: {
			title: '综合能力测试',
			description: '全方位业务能力综合评估'
		},
		simulation: {
			title: '模拟实战测试',
			description: '真实业务场景实战模拟'
		}
	}

	try {
		const config = modeConfig[mode]
		const confirm = await ElMessageBox.confirm(
			`确定开始"${config.title}"吗？\n\n${config.description}`,
			'确认开始测试',
			{
				confirmButtonText: '开始测试',
				cancelButtonText: '取消',
				type: 'info'
			}
		)
		if (confirm === 'confirm') {
			await startExam(mode)
		}
	} catch (error) {
		// 用户取消或出错
		ElMessage.info('取消开始测试')
	}
}

const startExam = async (mode) => {
	try {
		// 显示加载状态
		loading.value = true
		loadingProgress.value = 0
		loadingMessage.value = '准备测试环境...'
		
		// 获取岗位
		const userRoleRes = await getUserRole()
		const role = userRoleRes.role
		
		// 调用后端创建考试会话
		const res = await apiStartExam(mode)
		currentExam.session_id = res.session_id
    currentExam.dimensions = res.dimensions || [] // 新增：能力维度列表
		currentExam.title = getExamTitle(mode)
		currentExam.type = mode
		currentExam.questions = []
		currentExam.startTime = new Date()
		examAnswers.value = []
		currentQuestionIndex.value = 0
		selectedAnswer.value = ''
		selectedAnswers.value = []
		caseAnswer.value = ''
		examCompleted.value = false
		showHistory.value = false

		// 根据分值配置生成对应数量的题目
		let questionsToGenerate = SCORE_CONFIG.modeQuestions[mode] || []
		
		// 计算总题目数量
		const totalQuestions = questionsToGenerate.reduce((total, config) => total + config.count, 0)
		let generatedQuestions = 0

		// 并行生成题目
		loadingMessage.value = '生成题目中...'
		const questionPromises = []
		
		for (let i = 0; i < questionsToGenerate.length; i++) {
			const { qtype, count } = questionsToGenerate[i]
			
			for (let j = 0; j < count; j++) {
				// 创建题目生成Promise
				const questionPromise = chatWithCoachQuestion({
					role,
					qtype,
					question_index: j + 1 // 传递题目序号，便于AI生成差异化题目
				}).then(aiRes => {
					// 标准化题目结构
					let questionObj = {}
					if (qtype === 'single' || qtype === 'multiple') {
						questionObj = {
							type: aiRes.type,
							question: aiRes.question,
							options: aiRes.options,
							correctAnswer: aiRes.correctAnswer,
							explanation: aiRes.explanation || ''
						}
					} else if (qtype === 'truefalse') {
						questionObj = {
							type: aiRes.type,
							question: aiRes.question,
							correctAnswer: aiRes.correctAnswer,
							explanation: aiRes.explanation || ''
						}
					} else if (qtype === 'case') {
						questionObj = {
							type: aiRes.type,
							question: aiRes.question,
							scenario: aiRes.scenario || '',
							correctAnswer: aiRes.correctAnswer || '',
							explanation: aiRes.explanation || ''
						}
					}
					
					// 更新进度
					generatedQuestions++
					loadingProgress.value = Math.round((generatedQuestions / totalQuestions) * 100)
					
					return questionObj
				})
				
				questionPromises.push(questionPromise)
			}
		}

		// 等待所有题目生成完成
		const questions = await Promise.all(questionPromises)
		currentExam.questions = questions
		examAnswers.value = new Array(questions.length).fill(null)

		// 题目生成成功后才开始测试
		loadingMessage.value = '准备就绪...'
		loadingProgress.value = 100
		
		// 短暂延迟确保用户看到完成状态
		await new Promise(resolve => setTimeout(resolve, 500))
		
		loading.value = false
		examStarted.value = true
		ElMessage.success('测试开始！')
	} catch (error) {
		console.error('开始测试失败:', error)
		ElMessage.error('开始测试失败，请重试')
		loading.value = false
	} finally {
		submitting.value = false
	}
}

const startNewExam = () => {
	if (examStarted.value) {
		confirmExitTest().then(confirmed => {
			if (confirmed) {
				examStarted.value = false
				examCompleted.value = false
				showHistory.value = false
			}
		})
		return
	}

	if (!hasAvailableExams.value) {
		ElMessage.warning('暂无可用的测试，请先完成相关培训')
		return
	}
	examStarted.value = false
	examCompleted.value = false
	showHistory.value = false
}

// 3️⃣ 答题时提交答案到后端
const selectAnswer = (answerId) => {
	selectedAnswer.value = answerId
	// 新增：暂存答案到本地缓存
	answerCache.value[currentQuestionIndex.value] = answerId
	// 新增：实时计算得分
	calculateTotalScore() 
}

const toggleMultipleAnswer = (answerId) => {
	const index = selectedAnswers.value.indexOf(answerId)
	if (index > -1) {
		selectedAnswers.value.splice(index, 1)
	} else {
		selectedAnswers.value.push(answerId)
	}
	// 新增：暂存多选题答案到本地缓存
	answerCache.value[currentQuestionIndex.value] = [...selectedAnswers.value]
	// 新增：实时计算得分
	calculateTotalScore() 
}

const nextQuestion = async () => {
	if (!hasSelectedAnswer.value) return
	try {
		// 保存答案到后端
		let answer = null
        // 步骤1：缓存当前题的答案（核心！切换前先存答案）
		if (currentQuestion.value.type === 'multiple') {
            // 多选题：缓存选中的答案数组
			answer = [...selectedAnswers.value]
		} else if (currentQuestion.value.type === 'case') {
            // 案例题：缓存文本框输入的答案
			answer = caseAnswer.value
		} else {
            // 单选/判断题：缓存选中的答案
			answer = selectedAnswer.value
		}
		// await submitExamAnswer({
		// 	session_id: currentExam.session_id,
		// 	round_no: currentQuestionIndex.value + 1,
		// 	answer,
		// 	thinking_time: currentQuestion.value.type === 'case' ? 60 : 30
		// })
		examAnswers.value[currentQuestionIndex.value] = answer
		answerCache.value[currentQuestionIndex.value] = answer

		// 清空选择
		selectedAnswer.value = ''
		selectedAnswers.value = []
		caseAnswer.value = ''

		if (isLastQuestion.value) {
			// 最后一题时，调用批量提交 + 提交整卷
			await batchSubmitAnswers() 
		} else {
			currentQuestionIndex.value++
		}
	} catch (error) {
		ElMessage.error('提交答案失败，请重试')
	}
}

const previousQuestion = () => {
	if (currentQuestionIndex.value > 0) {
		currentQuestionIndex.value--
		// 优先读取本地缓存的答案（批量提交核心）
		const cachedAnswer = answerCache.value[currentQuestionIndex.value]
		const prevAnswer = examAnswers.value[currentQuestionIndex.value]
		const targetAnswer = cachedAnswer || prevAnswer

		if (currentQuestion.value.type === 'multiple' && Array.isArray(targetAnswer)) {
			selectedAnswers.value = [...targetAnswer]
			selectedAnswer.value = ''
			caseAnswer.value = ''
		} else if (currentQuestion.value.type === 'case') {
			caseAnswer.value = targetAnswer || ''
			selectedAnswer.value = ''
			selectedAnswers.value = []
		} else {
			selectedAnswer.value = targetAnswer || ''
			selectedAnswers.value = []
			caseAnswer.value = ''
		}
	}
}

// 新增：批量提交所有答案
const batchSubmitAnswers = async () => {
	if (Object.keys(answerCache.value).length === 0) {
		ElMessage.warning('暂无已答题目，无需提交！')
		return
	}

	try {
		batchSubmitting.value = true
		// 1. 构造 submitExamAnswer 要求的参数结构
		// console.log("currentExam.questions: ", currentExam.questions)
		const submitData = {
	  session_id: currentExam.session_id,
	  round_answers: Object.keys(answerCache.value).map(index => {
	    const q = currentExam.questions[Number(index)]
    
    // 检查q是否存在
    if (!q) {
      return {
        round_no: Number(index) + 1,
        ai_question: '',
        answer_analysis: '',
        scenario: '',
        ai_reply: '',
        answer: answerCache.value[index],
        dimension: Array.isArray(currentExam.dimensions)
          ? currentExam.dimensions.join(',')
          : currentExam.dimensions || '未知维度',
        round_score: 0
      }
    }

	    return {
	      round_no: Number(index) + 1,
	      ai_question: q.question || '',
	      answer_analysis: q.explanation || '',
	      scenario: q.scenario || '',
	      ai_reply: Array.isArray(q.correctAnswer)
	        ? JSON.stringify(q.correctAnswer)
	        : (q.correctAnswer ?? ''),
	      answer: answerCache.value[index],
	      dimension: Array.isArray(currentExam.dimensions)
	        ? currentExam.dimensions.join(',')
	        : currentExam.dimensions || '未知维度',
	      round_score: calculateQuestionScore(q, answerCache.value[index])
	    }
	  })
	  }
	  // console.log('批量提交答案数据:', submitData)
	  // 2. 直接调用原有 submitExamAnswer 函数
	  const res = await submitExamAnswer(submitData) 
	  if (res.success) {
	    ElMessage.success('批量提交答案成功！')
	    examAnswers.value = Object.values(answerCache.value)
	    calculateTotalScore() // 重新计算总分
	  }
	  await submitExam() // 提交整卷结果
	} catch (error) {
		console.error('批量提交答案失败:', error)
		ElMessage.error('批量提交答案失败，请重试！')
	} finally {
		batchSubmitting.value = false
	}
}

// 4️⃣ 结束与评分（调用后端接口）
const submitExam = async () => {
	submitting.value = true
	try {
		// 先结束考试会话
		await finishExam(currentExam.session_id)
		// 获取最终结果（优先用后端计算的分数）
		const res = await getExamResult(currentExam.session_id)
		
		// 兼容后端返回结构
		const finalScore = res.total_score || currentScore.value // 用本地计算的总分兜底
		examResult.totalScore = finalScore
		examResult.abilities = (res.scores || []).map(s => ({
			name: s.dimension,
			score: s.score
		}))
		examResult.suggestions = res.scores?.map(s => ({
			icon: '💡',
			title: s.dimension,
			description: s.comment
		})) || []

		// 等级判定
		if (finalScore >= SCORE_CONFIG.levels.expert) {
			examResult.level = '专家'
		} else if (finalScore >= SCORE_CONFIG.levels.advanced) {
			examResult.level = '高级'
		} else if (finalScore >= SCORE_CONFIG.levels.intermediate) {
			examResult.level = '中级'
		} else if (finalScore >= SCORE_CONFIG.levels.primary) {
			examResult.level = '初级'
		} else {
			examResult.level = '入门'
		}

		// 准确率计算（仅后端未返回时）
		if (!examResult.accuracy && examAnswers.value.length > 0) {
			const correctCount = examAnswers.value.filter((answer, index) => {
				const question = currentExam.questions[index]
				if (!question) return false
				if (question.type === 'multiple') {
					const correctAnswers = Array.isArray(question.correctAnswer) ? question.correctAnswer : [question.correctAnswer]
					return JSON.stringify(answer.sort()) === JSON.stringify(correctAnswers.sort())
				} else if (question.type === 'truefalse' || question.type === 'single') {
					return answer === question.correctAnswer
				} else if (question.type === 'case') {
					return false // 案例题暂不计算准确率
				}
			}).length
			examResult.accuracy = Math.round((correctCount / examAnswers.value.length) * 100)
		}
		
		// 计算用时
		examResult.timeSpent = Math.floor((new Date() - currentExam.startTime) / 1000)
		
		// 保存历史记录
		examHistory.value.unshift({
			id: currentExam.session_id,
			title: currentExam.title,
			date: new Date().toLocaleDateString(),
			timeSpent: formatTime(examResult.timeSpent),
			score: examResult.totalScore,
			level: examResult.level
		})
		
		// 更新状态
		examCompleted.value = true
		examStarted.value = false
		ElMessage.success('测试完成！')
	} catch (error) {
		console.error('提交考试结果失败:', error)
		ElMessage.error('提交考试结果失败，请重试')
	} finally {
		submitting.value = false
	}
}

// 历史相关
const viewHistory = () => {
	if (examStarted.value) {
		confirmExitTest().then(confirmed => {
			if (confirmed) {
				examStarted.value = false
				examCompleted.value = false
				showHistory.value = false
			}
		})
		return
	}

	examStarted.value = false
	examCompleted.value = false
	showHistory.value = true
}

const viewHistoryDetail = (record) => {
	ElMessage.info(`查看 ${record.title} 的详细结果`)
}

const retakeExam = () => {
	if (!canRetake.value) {
		ElMessage.warning('暂时无法重新测试，请稍后再试')
		return
	}
	startExam(currentExam.type)
}

const continueLearning = () => {
	ElMessage.info('跳转到训练页面继续学习...')
}

const reviewAnswers = () => {
	reviewDialog.visible = true
}

onMounted(() => {
	loadExamHistory()

	window.addEventListener('beforeunload', handleBeforeUnload)
})

onUnmounted(() => {
	window.removeEventListener('beforeunload', handleBeforeUnload)
})

const handleBeforeUnload = (event) => {
	if (examStarted.value) {
		event.preventDefault()
		event.returnValue = '您当前正在进行测试，退出后进度将无法保存！'
		return event.returnValue
	}
}

const loadExamHistory = () => {
	// 这里应该从API加载历史记录，暂时使用模拟数据
	examHistory.value = [
		{
			id: '1',
			title: '专项能力测试',
			date: new Date().toLocaleDateString(),
			timeSpent: '15分30秒',
			score: 85,
			level: '高级'
		}
	]
}

const closeReviewDialog = () => {
	reviewDialog.visible = false
}

const backToDashboard = () => {
	if (examStarted.value) {
		confirmExitTest().then(confirmed => {
			if (confirmed) {
				examStarted.value = false
				examCompleted.value = false
				showHistory.value = false
			}
		})
		return
	}

	router.push('/dashboard')
}
</script>

<style scoped>
/* ========== 全局样式 ========== */
.exam-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: 'PingFang SC', 'Helvetica Neue', STHeiti, 'Microsoft Yahei', sans-serif;
}

/* 加载状态 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-content {
  text-align: center;
  color: white;
  max-width: 400px;
  padding: 40px;
  background: rgba(150, 102, 199, 0.3);
  border-radius: 20px;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.loading-icon {
  font-size: 64px;
  margin-bottom: 20px;
  animation: pulse 2s infinite;
}

.loading-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 12px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.loading-message {
  font-size: 16px;
  margin-bottom: 30px;
  opacity: 0.9;
}

.loading-progress {
  margin-top: 20px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 14px;
  opacity: 0.8;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

/* ========== 顶部导航 ========== */
.exam-header {
  position: relative;
  padding: 60px 20px 40px;
  color: white;
  overflow: hidden;
}

.header-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
}

.header-pattern {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    radial-gradient(circle at 25% 25%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 75% 75%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
  background-size: 100px 100px;
}

.header-gradient {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%);
}

.header-content {
  position: relative;
  z-index: 2;
  max-width: 1200px;
  margin: 0 auto;
}

.header-main {
  text-align: center;
  margin-bottom: 40px;
}

.header-icon {
  font-size: 64px;
  margin-bottom: 20px;
  display: block;
}

.header-title {
  font-size: 42px;
  font-weight: 700;
  margin-bottom: 12px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  letter-spacing: 1px;
}

.header-subtitle {
  font-size: 18px;
  opacity: 0.9;
  font-weight: 300;
  letter-spacing: 0.5px;
}

.header-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.action-btn {
  padding: 14px 32px !important;
  border-radius: 50px !important;
  font-weight: 600;
  font-size: 16px;
  transition: all 0.3s ease;
  border: 2px solid rgba(255, 255, 255, 0.2) !important;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.15) !important;
  color: white !important;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  white-space: nowrap;
}

.action-btn :deep(.el-icon) {
  display: none !important;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  background: rgba(255, 255, 255, 0.2) !important;
}

.action-btn:active {
  transform: translateY(0);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  background: linear-gradient(135deg, #3584ff, #0f7edb) !important;
}

.action-btn:focus {
  outline: none;
  box-shadow: 0 0 0 4px rgba(64, 158, 255, 0.5), 0 8px 25px rgba(0, 0, 0, 0.15) !important;
}

.action-btn.primary {
  background: linear-gradient(135deg, #409eff, #1890ff) !important;
  border-color: transparent !important;
}

.action-btn.secondary {
  background: linear-gradient(135deg, #409eff, #1890ff) !important;
  border-color: transparent !important;
}

.action-btn.back-btn {
  background: linear-gradient(135deg, #409eff, #1890ff) !important;
  border-color: transparent !important;
}

.action-btn.back-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* ========== 主要内容区域 ========== */
.exam-main {
  max-width: 1200px;
  margin: 40px auto 0;
  padding: 0 20px 40px;
  position: relative;
  z-index: 3;
}

.exam-section {
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
  overflow: hidden;
}

.section-container {
  padding: 40px;
}

.section-header {
  margin-bottom: 40px;
  margin-left: -30px;
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 12px;
}

.title-icon {
  color: #667eea;
  font-size: 32px;
}

.section-desc {
  font-size: 16px;
  color: #7f8c8d;
  font-weight: 400;
  text-align: center;
  margin-left: 40px;
}

/* ========== 模式选择 ========== */
.mode-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 30px;
}

.mode-card {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.4s ease;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  background: white;
  border: 2px solid transparent;
}

.mode-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.card-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
}

.card-pattern {
  position: absolute;
  top: -50%;
  left: -50%;
  right: -50%;
  bottom: -50%;
  background: repeating-conic-gradient(
    from 0deg at 50% 50%,
    transparent 0deg,
    rgba(102, 126, 234, 0.03) 10deg,
    transparent 20deg
  );
  animation: rotate 20s linear infinite;
}

@keyframes rotate {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.card-content {
  position: relative;
  z-index: 2;
  padding: 32px 28px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.card-icon {
  font-size: 48px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.card-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.card-badge.recommended {
  background: linear-gradient(135deg, #ff6b6b, #ee5a24);
  color: white;
}

.card-badge.popular {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.card-badge.challenge {
  background: linear-gradient(135deg, #f093fb, #f5576c);
  color: white;
}

.card-body {
  flex: 1;
  margin-bottom: 24px;
}

.card-title {
  font-size: 22px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 12px;
}

.card-desc {
  font-size: 14px;
  color: #7f8c8d;
  line-height: 1.6;
  margin-bottom: 20px;
}

.card-features {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.feature-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.card-footer {
  margin-top: auto;
}

.card-action {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #667eea;
  font-weight: 600;
  font-size: 14px;
}

/* ========== 测试进行中 ========== */
.exam-wrapper {
  padding: 40px;
}

.exam-progress {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 16px;
  padding: 24px 32px;
  margin-bottom: 40px;
}

.progress-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.progress-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.exam-title {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
}

.progress-stats {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #495057;
}

.progress-separator {
  color: #adb5bd;
  margin: 0 4px;
}

.progress-percentage {
  font-size: 24px;
  font-weight: 700;
  color: #667eea;
}

.progress-bar {
  height: 8px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 4px;
  transition: width 0.3s ease;
}

/* 题目样式 */
.question-container {
  background: #f8f9fa;
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 32px;
}

.question-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.question-type {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border-radius: 20px;
  font-weight: 600;
  color: #495057;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.question-number {
  font-size: 18px;
  font-weight: 700;
  color: #3ddb42;
}

.question-content {
  margin-bottom: 24px;
}

.question-text {
  font-size: 18px;
  line-height: 1.7;
  color: #2c3e50;
  margin-bottom: 24px;
}

/* 选项样式 */
.question-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-item {
  display: flex;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.option-item:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.option-item.selected {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
}

.radio-outer {
  /* 原样式保留 + 新增间距（替代原option-radio的margin） */
  margin-right: 16px; /* 原option-radio的间距移到这里 */
  width: 24px;
  height: 24px;
  border: 2px solid #dee2e6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  background: white;
  box-sizing: border-box;
}

/* 选中态样式（补充，避免样式缺失） */
.option-item.selected .radio-outer {
  border-color: #626aef; /* 紫色主题色，可自定义 */
  background: #626aef;
}

.radio-inner {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: white;
}

.option-content {
  flex: 1;
}

.option-label {
  display: inline-block;
  width: 32px;
  height: 32px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  text-align: center;
  line-height: 32px;
  font-weight: 700;
  margin-right: 16px;
  flex-shrink: 0;
}

.option-text {
  font-size: 16px;
  color: #495057;
  line-height: 1.5;
}

/* 多选题样式 */
.option-item.multiple {
  margin-right: 16px;
  /* 新增：清除默认样式，避免出现多余圆形 */
  width: auto;
  height: auto;
  border: none;
  border-radius: 0;
  background: transparent;
  /* 保证radio-outer居中对齐 */
  display: flex;
  align-items: center;
  justify-content: center;
}

.checkbox-outer {
  /* 原样式保留 + 新增间距（替代原option-checkbox的margin） */
  margin-right: 16px; /* 原option-checkbox的间距移到这里 */
  width: 24px;
  height: 24px;
  border: 2px solid #dee2e6;
  border-radius: 4px; /* 复选框用圆角矩形，区别单选 */
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  background: white;
  box-sizing: border-box;
}

/* 选中态样式（补充，避免对号重叠） */
.option-item.selected .checkbox-outer {
  border-color: #626aef;
  background: #626aef;
}

/* 对号图标样式（统一大小+颜色，避免重叠） */
.checkbox-check {
  color: white; /* 对号白色，和背景对比 */
  font-size: 16px; /* 固定大小，避免el-icon默认大小不一致 */
  /* 关键：清除图标自身的冗余样式，避免叠加 */
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 判断题样式 */
.question-options.truefalse {
  flex-direction: row;
  gap: 20px;
}

.option-item.truefalse-option {
  flex: 1;
  justify-content: center;
  padding: 24px;
}

.option-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.option-icon.correct {
  color: #52c41a;
}

.option-icon.incorrect {
  color: #ff4d4f;
}

/* 案例分析样式 */
.case-scenario {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  border-left: 4px solid #667eea;
}

.scenario-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: #667eea;
  font-weight: 600;
}

.scenario-content {
  color: #495057;
  line-height: 1.6;
}

.case-answer {
  background: white;
  border-radius: 12px;
  padding: 24px;
}

.answer-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  color: #667eea;
  font-weight: 600;
}

.answer-input :deep(.el-textarea__inner) {
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-family: inherit;
}

.answer-input :deep(.el-textarea__inner):focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* 操作按钮 */
.exam-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 0;
}

.nav-btn {
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
}

.nav-btn.prev {
  background: #f8f9fa;
  color: #6c757d;
  border: 1px solid #dee2e6;
}

.nav-btn.prev:hover {
  background: #e9ecef;
}

.submit-btn {
  padding: 14px 32px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
}

.spacer {
  flex: 1;
}

/* ========== 测试结果 ========== */
.result-container {
  padding: 60px 40px;
  text-align: center;
}

.result-header {
  margin-bottom: 50px;
}

.result-celebration {
  margin-bottom: 30px;
}

.celebration-icon {
  font-size: 80px;
  margin-bottom: 20px;
  display: block;
}

.result-title {
  font-size: 36px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 12px;
}

.result-desc {
  font-size: 18px;
  color: #7f8c8d;
  font-weight: 400;
}

.score-card {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 20px;
  padding: 40px;
  margin-bottom: 50px;
  color: white;
}

.score-main {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 60px;
  margin-bottom: 30px;
}

.score-circle {
  text-align: center;
}

.score-number {
  font-size: 72px;
  font-weight: 900;
  display: block;
  margin-bottom: 8px;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.score-label {
  font-size: 18px;
  opacity: 0.9;
  font-weight: 500;
}

.score-details {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.score-item {
  text-align: left;
}

.score-item .score-value {
  font-size: 28px;
  font-weight: 700;
  display: block;
  margin-bottom: 4px;
}

.score-item .score-label {
  font-size: 14px;
  opacity: 0.8;
}

.score-item .score-value.level.excellent {
  color: #ffd700;
}

.score-item .score-value.level.good {
  color: #52c41a;
}

.score-item .score-value.level.average {
  color: #faad14;
}

.score-item .score-value.level.needs_improvement {
  color: #ff4d4f;
}

/* 能力分析 */
.abilities-section {
  margin-bottom: 50px;
}

.abilities-section .section-title {
  justify-content: center;
  margin-bottom: 30px;
}

.abilities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.ability-item {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

.ability-header {
  display: flex;
  align-items: center;
  padding-left: 24px;
  justify-content: space-between;
  margin-bottom: 16px;
  margin-top: 16px;
}

.ability-name {
  width: 90px;
  font-weight: 600;
  color: #2c3e50;
}

.ability-score {
  font-weight: 700;
  color: #667eea;
}

.ability-bar {
  height: 8px;
  background: #f1f3f4;
  border-radius: 4px;
  overflow: hidden;
}

.ability-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.8s ease;
}

/* 学习建议 */
.suggestions-section {
  margin-bottom: 50px;
}

.suggestions-section .section-title {
  justify-content: center;
  margin-bottom: 30px;
}

.suggestions-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.suggestion-item {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #667eea;
}

.suggestion-icon {
  font-size: 24px;
  margin-bottom: 12px;
  display: block;
}

.suggestion-title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

.suggestion-desc {
  color: #7f8c8d;
  line-height: 1.6;
}

/* 结果操作按钮 */
.result-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.result-actions .action-btn {
  padding: 14px 32px;
  border-radius: 50px;
  font-weight: 600;
  font-size: 16px;
  transition: all 0.3s ease;
}

.result-actions .action-btn.primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  color: white;
}

.result-actions .action-btn.secondary {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  border: 2px solid #667eea;
}

.result-actions .action-btn.outline {
  background: transparent;
  color: #6c757d;
  border: 2px solid #dee2e6;
}

.result-actions .action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

/* ========== 测试历史 ========== */
.history-container {
  padding: 40px;
}

.history-header {
  text-align: center;
  margin-bottom: 40px;
}

.history-filters {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 24px;
  background: white;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #e9ecef;
}

.history-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.history-icon {
  font-size: 32px;
  color: #667eea;
  margin-right: 20px;
  flex-shrink: 0;
}

.history-content {
  flex: 1;
}

.history-title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

.history-meta {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #7f8c8d;
}

.history-score {
  text-align: right;
  flex-shrink: 0;
}

.score-display {
  font-size: 24px;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 4px;
}

.score-level {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.score-level.excellent {
  background: #fff7e6;
  color: #d46b08;
}

.score-level.good {
  background: #f6ffed;
  color: #52c41a;
}

.score-level.average {
  background: #fffbe9;
  color: #faad14;
}

.score-level.needs_improvement {
  background: #fff2f0;
  color: #ff4d4f;
}

.no-history {
  text-align: center;
  padding: 60px 20px;
}

.empty-state {
  max-width: 400px;
  margin: 0 auto;
}

.empty-icon {
  font-size: 64px;
  color: #d9d9d9;
  margin-bottom: 20px;
}

.empty-state h3 {
  font-size: 24px;
  color: #2c3e50;
  margin-bottom: 12px;
}

.empty-state p {
  color: #7f8c8d;
  margin-bottom: 24px;
}

/* ========== 答案解析弹窗 ========== */
.review-dialog :deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

.review-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  margin: 0;
  padding: 24px 32px;
}

.review-dialog :deep(.el-dialog__title) {
  font-size: 20px;
  font-weight: 600;
}

.review-dialog :deep(.el-dialog__body) {
  padding: 32px;
  max-height: 70vh;
  overflow-y: auto;
}

.review-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.review-question {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 24px;
  border-left: 4px solid #667eea;
}

.review-question .question-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.question-number {
  background: #667eea;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 600;
}

.question-type {
  background: white;
  color: #495057;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 14px;
}

.question-status.correct {
  color: #52c41a;
  font-weight: 600;
}

.question-status.incorrect {
  color: #ff4d4f;
  font-weight: 600;
}

.question-status.unanswered {
  color: #faad14;
  font-weight: 600;
}

.question-content {
  font-size: 16px;
  color: #2c3e50;
  margin-bottom: 16px;
  line-height: 1.6;
}

.question-scenario {
  background: white;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  border-left: 3px solid #faad14;
}

.answer-analysis {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.user-answer,
.correct-answer,
.explanation {
  background: white;
  padding: 16px;
  border-radius: 8px;
}

.user-answer {
  border-left: 3px solid #667eea;
}

.correct-answer {
  border-left: 3px solid #52c41a;
}

.explanation {
  border-left: 3px solid #faad14;
}

.explanation p {
  margin: 0;
  line-height: 1.6;
  color: #495057;
}

/* ========== 响应式设计 ========== */
@media (max-width: 768px) {
  .exam-container {
    padding: 10px;
  }

  .exam-header {
    padding: 40px 20px 30px;
  }

  .header-title {
    font-size: 32px;
  }

  .header-subtitle {
    font-size: 16px;
  }

  .header-actions {
    flex-direction: column;
    gap: 12px;
  }

  .exam-main {
    margin-top: -20px;
    padding: 0 10px 20px;
  }

  .section-container {
    padding: 24px 20px;
  }

  .mode-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .score-main {
    flex-direction: column;
    gap: 30px;
  }

  .score-number {
    font-size: 48px;
  }

  .abilities-grid,
  .suggestions-list {
    grid-template-columns: 1fr;
  }

  .result-actions {
    flex-direction: column;
    gap: 12px;
  }

  .exam-actions {
    flex-direction: column;
    gap: 12px;
  }

  .exam-actions .spacer {
    display: none;
  }

  .question-options.truefalse {
    flex-direction: column;
    gap: 12px;
  }

  .history-item {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }

  .history-meta {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .exam-header {
    padding: 30px 15px 20px;
  }

  .header-title {
    font-size: 28px;
  }

  .celebration-icon {
    font-size: 60px;
  }

  .result-title {
    font-size: 28px;
  }

  .score-card {
    padding: 24px;
  }

  .score-number {
    font-size: 36px;
  }

  .exam-wrapper,
  .section-container,
  .history-container {
    padding: 20px 16px;
  }
}

/* ========== 动画效果 ========== */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.exam-section {
  animation: fadeInUp 0.6s ease-out;
}

.mode-card:nth-child(1) { animation-delay: 0.1s; }
.mode-card:nth-child(2) { animation-delay: 0.2s; }
.mode-card:nth-child(3) { animation-delay: 0.3s; }

.ability-item,
.suggestion-item {
  animation: fadeInUp 0.6s ease-out;
  animation-fill-mode: both;
}

.ability-item:nth-child(odd) { animation-delay: 0.1s; }
.ability-item:nth-child(even) { animation-delay: 0.2s; }

.suggestion-item:nth-child(odd) { animation-delay: 0.1s; }
.suggestion-item:nth-child(even) { animation-delay: 0.2s; }

/* Loading 动画 */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

:deep(.el-loading-mask) .el-loading-spinner .el-icon {
  animation: spin 1s linear infinite;
}

.exam-interface {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.exam-progress {
  background: #f5f7fa;
  padding: 16px 24px;
  border-bottom: 1px solid #ebeef5;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.progress-time {
  color: #909399;
  font-size: 14px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #409eff, #67c23a);
  transition: width 0.3s ease;
}

.exam-content {
  padding: 24px;
}

.question-card {
  margin-bottom: 24px;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.question-type {
  background: #e1f3d8;
  color: #67c23a;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.question-number {
  color: #fff;
  font-size: 14px;
}

.question-text {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 20px;
  line-height: 1.6;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  margin-bottom: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.option-item:hover {
  background: #f5f7fa;
}

.option-item.selected {
  background: rgba(98, 106, 239, 0.1); /* 选中态浅背景 */
}

.option-content {
  display: flex;
  align-items: center;
}

.option-label {
  margin-right: 8px;
  font-weight: 600;
}

.option-radio {
  width: 20px;
  height: 20px;
  border: 2px solid #c0c4cc;
  border-radius: 50%;
  position: relative;
  flex-shrink: 0;
  margin-top: 2px;
}

.option-item.selected .option-radio {
  border-color: #409eff;
  background: #409eff;
}

.option-item.selected .option-radio::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 6px;
  height: 6px;
  background: white;
  border-radius: 50%;
  transform: translate(-50%, -50%);
}

.option-checkbox {
  width: 20px;
  height: 20px;
  border: 2px solid #c0c4cc;
  border-radius: 4px;
  position: relative;
  flex-shrink: 0;
  margin-top: 2px;
}

.option-item.selected .option-checkbox {
  border-color: #409eff;
  background: #409eff;
}

.option-item.selected .option-checkbox::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  color: white;
  font-size: 12px;
  font-weight: bold;
  transform: translate(-50%, -50%);
}

.option-text {
  flex: 1;
  font-size: 16px;
  color: #303133;
  line-height: 1.5;
}

.truefalse-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-top: 16px;
}

.truefalse-btn {
  padding: 16px 24px;
  border: 2px solid #ebeef5;
  border-radius: 8px;
  background: white;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.truefalse-btn:hover {
  border-color: #c0c4cc;
  background: #f5f7fa;
}

.truefalse-btn.selected {
  border-color: #409eff;
  background: #ecf5ff;
  color: #409eff;
  font-weight: bold;
}

.case-scenario {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.case-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 12px;
}

.case-content {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 16px;
}

.case-textarea {
  width: 100%;
  min-height: 120px;
  padding: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-family: inherit;
  resize: vertical;
}

.case-textarea:focus {
  outline: none;
  border-color: #409eff;
}

.navigation-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #ebeef5;
}

.nav-btn {
  padding: 12px 24px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  background: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.nav-btn:hover:not(:disabled) {
  border-color: #c0c4cc;
  background: #f5f7fa;
}

.nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nav-btn.primary {
  background: #409eff;
  border-color: #409eff;
  color: white;
}

.nav-btn.primary:hover:not(:disabled) {
  background: #66b1ff;
  border-color: #66b1ff;
}

/* 结果界面 */
.results-container {
  max-width: 800px;
  margin: 0 auto;
}

.results-header {
  text-align: center;
  margin-bottom: 32px;
}

.results-score {
  font-size: 48px;
  font-weight: bold;
  color: #67c23a;
  margin-bottom: 8px;
}

.results-level {
  font-size: 20px;
  color: #303133;
  margin-bottom: 16px;
}

.results-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  display: block;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  margin-top: 4px;
}

.abilities-analysis {
  margin-bottom: 32px;
}

.analysis-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 16px;
}

.ability-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.ability-name {
  font-weight: bold;
  color: #303133;
}

.ability-score {
  font-weight: bold;
}

.ability-bar {
  width: 80%;
  height: 8px;
  background: #ebeef5;
  border-radius: 4px;
  overflow: hidden;
  margin-left: 16px;
  margin-right: 40px;
}

.ability-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.suggestions-list {
  margin-bottom: 32px;
}

.suggestion-item {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 16px;
}

.suggestion-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.suggestion-content h4 {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
}

.suggestion-content p {
  color: #606266;
  line-height: 1.5;
  margin: 0;
}

.results-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 12px 24px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  background: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn:hover {
  border-color: #c0c4cc;
  background: #f5f7fa;
}

.action-btn.primary {
  background: #409eff;
  border-color: #409eff;
  color: white;
}

.action-btn.primary:hover {
  background: #66b1ff;
  border-color: #66b1ff;
}

/* 历史记录 */
.history-container {
  max-width: 1000px;
  margin: 0 auto;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.history-title {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.history-filters {
  display: flex;
  gap: 12px;
}

.filter-btn {
  padding: 8px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-btn.active {
  background: #409eff;
  border-color: #409eff;
  color: white;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: white;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.history-info h4 {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
}

.history-meta {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: #909399;
}

.history-score {
  text-align: right;
}

.history-score-value {
  font-size: 24px;
  font-weight: bold;
  color: #67c23a;
  display: block;
}

.history-level {
  font-size: 14px;
  color: #606266;
  margin-top: 4px;
}

.history-actions {
  display: flex;
  gap: 8px;
}

.history-btn {
  padding: 6px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: white;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.history-btn:hover {
  border-color: #c0c4cc;
  background: #f5f7fa;
}

.history-btn.primary {
  background: #409eff;
  border-color: #409eff;
  color: white;
}

.history-btn.primary:hover {
  background: #66b1ff;
  border-color: #66b1ff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .exam-container {
    padding: 16px;
  }

  .exam-title {
    font-size: 24px;
  }

  .mode-selection {
    grid-template-columns: 1fr;
  }

  .progress-info {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }

  .results-stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .truefalse-options {
    grid-template-columns: 1fr;
  }

  .navigation-buttons {
    flex-direction: column;
    gap: 12px;
  }

  .results-actions {
    flex-direction: column;
  }

  .history-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .history-score {
    text-align: left;
  }
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.question-card,
.mode-card,
.results-container,
.history-item {
  animation: fadeIn 0.3s ease-out;
}

/* 加载状态 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-content {
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>