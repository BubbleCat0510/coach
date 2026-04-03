<template>
  <div class="train-layout">
    <!-- ========== 左侧 Session 侧边栏 ========== -->
    <aside v-if="sidebarVisible" class="sidebar">
      <div class="sidebar-header">
        <h2>🎯 AI 教练训练</h2>
        <el-button
          link
          class="collapse-btn"
          @click="toggleSidebar"
        >
          ⬅
        </el-button>
      </div>

      <!-- 新建训练 -->
      <div class="new-session">
        <el-button
          type="success"
          plain
          class="new-session-btn"
          @click="createNewSession"
        >
          ➕ 新建训练
        </el-button>
      </div>

      <!-- 历史训练列表 -->
      <div class="session-list">
        <div
          v-for="session in sessions"
          :key="session.id"
          class="session-item"
          :class="{ active: session.id === currentSessionId }"
          @click="switchSession(session)"
        >
          <div class="session-title">
            {{ session.title }}
          </div>
          <div class="session-meta">最近训练：{{ session.update_time }}</div>
        </div>
      </div>

      <!-- 更多历史按钮 -->
      <div v-if="allSessions.length > 10" class="more-history">
        <el-button
          link
          type="primary"
          @click="showHistoryDialog = true"
        >
          📚 查看更多历史 ({{ allSessions.length - 10 }})
        </el-button>
      </div>
    </aside>

    <!-- ========== 右侧主区域 ========== -->
    <div class="main-area">
      <!-- 顶部固定栏 -->
      <div class="fixed-header">
        <el-button
          v-if="!sidebarVisible"
          link
          class="collapse-btn"
          @click="toggleSidebar"
        >
          ➡
        </el-button>

        <!-- 训练进度可视化 -->
        <div class="progress-section">
          <div class="progress-info">
            <span class="progress-label">训练进度</span>
            <span class="progress-stats">
              第 {{ completedRounds }} / {{ totalRounds }} 轮
              <span v-if="averageScore > 0" class="score-display">
                平均得分: {{ averageScore }}/100
              </span>
            </span>
          </div>
          <el-progress
            :percentage="progressPercentage"
            :stroke-width="8"
            :show-text="false"
            color="#34d399"
            class="progress-bar"
          />
        </div>

        <div class="header-actions">
          <el-button
            link
            @click="refreshData"
            :loading="isRefreshing"
            title="刷新数据"
          >
            🔄
          </el-button>
          <p>当前岗位：{{ roleName }}</p>
          <el-button
            text
            @click="backToDashboard"
            title="返回主页"
            class="back-btn-train"
          >
            返回主页
          </el-button>
        </div>
      </div>

      <!-- ========== 对话区域（你原来的 rounds） ========== -->
      <div class="chat-box" ref="chatBox" @scroll="handleChatScroll">
        <!-- 加载更多指示器 -->
        <div v-if="roundsLoading" class="loading-more">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载更多历史记录...</span>
        </div>
        <div v-if="questionLoading" class="chat-item ai">
          <div class="bubble loading-bubble">
            <el-icon class="is-loading"><Loading /></el-icon>
            <div class="loading-content">
              <p class="loading-text">题目生成中，请稍候...</p>
              <el-skeleton :loading="true" animated>
                <template #template>
                  <el-skeleton-item variant="text" style="width: 200px;" />
                  <el-skeleton-item variant="text" style="width: 150px;" />
                </template>
              </el-skeleton>
            </div>
          </div>
        </div>

        <!-- 问题生成错误提示 -->
        <div v-if="questionError && !questionLoading" class="chat-item ai">
          <div class="bubble error-bubble">
            <p>❌ 生成问题时遇到问题</p>
            <el-button size="small" type="primary" @click="retryGenerateQuestion" :loading="questionLoading">
              重试
            </el-button>
          </div>
        </div>

        <div
          v-for="(round, index) in rounds"
          :key="index"
          class="round"
        >
          <!-- AI 提问 -->
          <div class="chat-item ai">
            <div class="bubble">
              {{ round.aiQuestion }}
            </div>
          </div>

          <!-- 用户回答 -->
          <div v-if="round.userAnswer" class="chat-item user">
            <div class="bubble user-bubble">
              {{ round.userAnswer }}
            </div>
          </div>

          <!-- AI 回复 -->
          <div v-if="round.aiReply" class="chat-item ai">
            <div class="bubble">
              {{ round.aiReply }}
            </div>
          </div>

          <!-- 教练评分 -->
          <div v-if="round.score" class="chat-item ai">
            <el-card class="score-card">
              <h4>🧠 教练评分</h4>
              <p>得分：<b>{{ round.score.value }}</b> 分</p>
              <p>建议：{{ round.score.feedback }}</p>
            </el-card>
          </div>
        </div>

        <!-- 发送错误提示 -->
        <div v-if="sendError" class="chat-item ai">
          <div class="bubble error-bubble">
            <p>❌ AI 回复生成失败</p>
            <el-button size="small" type="primary" @click="retrySend" :loading="sending">
              重试发送
            </el-button>
          </div>
        </div>
      </div>

      <!-- ========== 输入区域（保留） ========== -->
      <div class="input-box">
        <el-input
          v-model="input"
          placeholder="请输入你的回答..."
          @keyup.enter="send"
          :disabled="creatingSession || saving || sending || questionLoading"
        />
        <el-button type="success" @click="send" :loading="creatingSession || saving || sending || questionLoading" :disabled="creatingSession || saving || sending || questionLoading">
          发送
        </el-button>
      </div>
    </div>
  </div>

  <!-- 历史记录弹窗 -->
  <el-dialog
    v-model="showHistoryDialog"
    title="📚 完整历史记录"
    width="600px"
    :before-close="handleHistoryDialogClose"
  >
    <div class="history-dialog-content">
      <div
        v-for="session in allSessions"
        :key="session.id"
        class="history-item"
        :class="{ active: session.id === currentSessionId }"
        @click="switchSessionFromDialog(session)"
      >
        <div class="history-title">
          {{ session.title }}
        </div>
        <div class="history-meta">
          <span>岗位：{{ session.roleName }}</span>
          <span>最近训练：{{ formatTime(session.update_time) }}</span>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  createSession,
  getSessionList,
  getSessionRounds,
  saveTrainRound
} from '../api/train'
import { getUserRole } from '../api/user'
import { 
  chatWithCoach, 
  chatWithCoachQuestion 
} from '../api/aiCoach'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'

const router = useRouter()


// 侧边栏是否显示
const sidebarVisible = ref(true)

// 当前岗位
const roleName = ref('') 

// 输入框
const input = ref('')

// 当前 session
const currentSessionId = ref(null)

// 监听输入框变化，自动保存草稿
watch(input, (newValue) => {
  if (currentSessionId.value) {
    localStorage.setItem(`draft_${currentSessionId.value}`, newValue)
  }
})

// 恢复当前会话的草稿
const restoreDraft = () => {
  if (currentSessionId.value) {
    const draft = localStorage.getItem(`draft_${currentSessionId.value}`)
    if (draft) {
      input.value = draft
    } else {
      input.value = ''
    }
  }
}

// 重试生成开场问题
const retryGenerateQuestion = async () => {
  questionError.value = false
  questionLoading.value = true

  const fallback = `你好，我是你的 AI 冠军教练，请介绍一下你如何进行${roleName.value}相关的工作？`

  try {
    const oq = await chatWithCoachQuestion({ role: roleName.value, last_question: '', type: 'opening' })
    const q = oq.nextQuestion || oq.next_question || oq.reply || ''
    // 更新最后一个round的问题
    if (rounds.value.length > 0) {
      rounds.value[0].aiQuestion = q || fallback
    }
  } catch (e) {
    console.error('重试生成开场问题失败', e)
    questionError.value = true
    // 保持fallback文案
  } finally {
    questionLoading.value = false
  }
}

// 重试发送消息
const retrySend = async () => {
  if (sending.value) return
  sendError.value = false

  // 重新执行发送逻辑（需要重新获取用户输入，因为input已经被清空了）
  const lastRound = rounds.value[rounds.value.length - 1]
  if (lastRound && lastRound.userAnswer && !lastRound.aiReply) {
    // 恢复输入框内容用于重试
    input.value = lastRound.userAnswer
    // 移除未完成的round
    rounds.value.pop()
    // 重新发送
    await send()
  }
}

// 处理历史弹窗关闭
const handleHistoryDialogClose = () => {
  showHistoryDialog.value = false
}

// 刷新所有数据
const refreshData = async () => {
  if (isRefreshing.value) return

  const now = Date.now()
  const timeSinceLastRefresh = now - lastRefreshTime.value
  const shouldShowMessage = timeSinceLastRefresh > 5000 // 5秒内不重复显示提示

  isRefreshing.value = true

  try {
    // 刷新历史会话列表
    await loadSessionList()

    // 如果当前有选中的会话，刷新对话内容
    if (currentSessionId.value) {
      const currentSession = sessions.value.find(s => s.id === currentSessionId.value)
      if (currentSession) {
        await switchSession(currentSession)
      }
    }

    // 只有在距离上次刷新超过5秒时才显示提示
    if (shouldShowMessage) {
      ElMessage.success('数据已刷新')
      lastRefreshTime.value = now
    }
  } catch (e) {
    console.error('刷新数据失败', e)
    // 错误时总是显示提示
    ElMessage.error('刷新失败，请稍后重试')
  } finally {
    isRefreshing.value = false
  }
}

// 处理页面可见性变化
const handleVisibilityChange = () => {
  if (!document.hidden) {
    // 页面重新获得焦点时，自动刷新数据
    // 添加一个小延迟，避免快速切换时的多次触发
    setTimeout(() => {
      refreshData()
    }, 100)
  }
}

// 从弹窗中切换会话
const switchSessionFromDialog = async (session) => {
  showHistoryDialog.value = false
  await switchSession(session)
}

// 加载更多历史对话记录
const loadMoreRounds = async () => {
  if (roundsLoading.value || roundsCurrentPage.value * roundsPageSize >= roundsTotal.value) {
    return
  }

  roundsLoading.value = true

  try {
    // 重新获取所有记录（实际上应该从缓存或后端分页获取，这里简化处理）
    const res = await getSessionRounds(currentSessionId.value)

    const allRounds = res.map((round, index) => {
      return {
        aiQuestion: round.ai_question || round.aiQuestion || '',
        userAnswer: round.user_text || round.userAnswer || '',
        aiReply: round.ai_reply || round.aiReply || '',
        score: round.score ? {
          value: round.score.value || round.score || 0,
          feedback: round.feedback || round.score.feedback || ''
        } : null
      }
    })

    roundsCurrentPage.value++

    // 计算要显示的记录范围
    const endIndex = allRounds.length
    const startIndex = Math.max(0, endIndex - (roundsCurrentPage.value * roundsPageSize))

    rounds.value = allRounds.slice(startIndex)

    // 滚动到新加载内容的顶部
    await nextTick()
    if (chatBox.value) {
      chatBox.value.scrollTop = 100 // 稍微向下滚动一点，让用户看到新内容
    }

  } catch (e) {
    console.error('加载更多对话记录失败', e)
  } finally {
    roundsLoading.value = false
  }
}

// 处理聊天框滚动事件
const handleChatScroll = () => {
  if (!chatBox.value) return

  const { scrollTop, scrollHeight, clientHeight } = chatBox.value

  // 当滚动到顶部附近时（距离顶部50px内），加载更多记录
  if (scrollTop <= 50 && !roundsLoading.value) {
    loadMoreRounds()
  }
}

// 历史 session 列表（后端返回）
const sessions = ref([])

// 完整的历史记录（用于弹窗）
const allSessions = ref([])

// 更多历史弹窗显示状态
const showHistoryDialog = ref(false)

// 页面刷新状态
const isRefreshing = ref(false)

// 上次刷新时间戳
const lastRefreshTime = ref(0)

// 聊天区域 DOM 引用，用于滚动到底部
const chatBox = ref(null)

// 会话创建中状态，防止重复点击创建/发送
const creatingSession = ref(false)
const saving = ref(false)
const sending = ref(false)
// 生成问题的加载状态（开场/跟进问题生成中）
const questionLoading = ref(false)

// 错误状态管理
const questionError = ref(false) // 开场问题生成失败
const sendError = ref(false)     // 发送时AI调用失败

// 训练轮次（你原来的结构）
// 初始问题会在加载岗位时由 AI 生成（或使用兜底文案）
const rounds = ref([])

// 分页相关状态
const roundsPageSize = 20 // 每页显示的对话轮次数量
const roundsCurrentPage = ref(1) // 当前页码
const roundsTotal = ref(0) // 总对话轮次数量
const roundsLoading = ref(false) // 加载更多状态

// 训练进度计算属性
const completedRounds = computed(() => {
  return rounds.value.filter(round => round.score && round.score.value > 0).length
})

const totalRounds = computed(() => {
  return rounds.value.length
})

const averageScore = computed(() => {
  const scoredRounds = rounds.value.filter(round => round.score && round.score.value > 0)
  if (scoredRounds.length === 0) return 0
  const totalScore = scoredRounds.reduce((sum, round) => sum + (round.score.value || 0), 0)
  return Math.round(totalScore / scoredRounds.length)
})

const progressPercentage = computed(() => {
  if (totalRounds.value === 0) return 0
  // 假设目标是完成10轮训练作为100%
  const targetRounds = 10
  const actualProgress = Math.min(completedRounds.value / targetRounds, 1) * 100
  return Math.round(actualProgress)
})

// 加载用户岗位
const loadUserRole = async () => {
  try {
    const res = await getUserRole()
    // 覆盖默认值，使用接口返回的岗位
    roleName.value = res.role
    // 使用 AI 生成开场问题（fallback 到同步文案）
    const fallback = `你好，我是你的 AI 冠军教练，请介绍一下你如何进行${roleName.value}相关的工作？`
    questionLoading.value = true
    try {
      const oq = await chatWithCoachQuestion({ role: roleName.value, last_question: '', type: 'opening' })
      const q = oq.nextQuestion || oq.next_question || oq.reply || ''
      rounds.value.push({
        aiQuestion: q || fallback,
        userAnswer: '',
        aiReply: '',
        score: null
      })
    } catch (e) {
      console.error('生成开场问题失败，使用兜底文案', e)
      questionError.value = true
      rounds.value.push({
        aiQuestion: fallback,
        userAnswer: '',
        aiReply: '',
        score: null
      })
    } finally {
      questionLoading.value = false
    }
  } catch (err) {
    console.error('加载用户岗位失败', err)
    // 兜底
    roleName.value = '品牌选址'
  }
}

onMounted(async () => {
  await loadUserRole()
  await loadSessionList()

  // 添加页面可见性监听
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

// 组件卸载时清理事件监听器
onUnmounted(() => {
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})

/**
 * 从后端加载 session 列表
 * 用于左侧「历史训练」
 */
const loadSessionList = async () => {
  try {
    const res = await getSessionList()

    // 保存完整的历史记录
    allSessions.value = (res || []).map(item => ({
      id: item.id,
      title: item.title,
      roleName: item.role_name || item.roleName,
      create_time: item.create_time,
      update_time: item.update_time || item.uodate_time || item.updateTime
    }))

    // 只显示前10个记录
    sessions.value = allSessions.value.slice(0, 10)
  } catch (err) {
    console.error('加载训练列表失败', err)
  }
}

// 格式化时间（后端通常返回 ISO 字符串或数据库时间字符串）
const formatTime = (timeStr) => {
  if (!timeStr) return '--'
  try {
    const d = new Date(timeStr)
    if (isNaN(d)) return timeStr
    return d.toLocaleString()
  } catch (e) {
    return timeStr
  }
}

const toggleSidebar = () => {
  sidebarVisible.value = !sidebarVisible.value
}

const send = async () => {
  if (sending.value) return
  sending.value = true
  sendError.value = false  // 重置错误状态

  if (!input.value.trim()) {
    ElMessage.warning('请输入内容后发送')
    sending.value = false
    return
  }

  // 1️⃣ 取出当前轮次（最后一轮）
  // 校验2：确保 rounds 数组有元素，且最后一个元素存在
  if (!rounds.value.length || !rounds.value[rounds.value.length - 1]) {
    // 兜底：重新初始化最后一个元素
    // 尝试使用 AI 生成开场/引导问题
    let opening = `你好，我是你的 AI 冠军教练，请介绍一下你如何进行${roleName.value}相关的工作？`
    questionLoading.value = true
    try {
      const oq = await chatWithCoachQuestion({ role: roleName.value, last_question: '', type: 'opening', session_id: currentSessionId.value })
      opening = oq.nextQuestion || oq.next_question || oq.reply || opening
    } catch (e) {
      console.error('生成兜底问题失败，使用默认文案', e)
    } finally {
      questionLoading.value = false
    }

    rounds.value.push({
      aiQuestion: opening,
      aiQuestionTime: new Date().toISOString(),
      userAnswer: '',
      aiReply: '',
      score: null
    })
  }

  // 2️⃣ 记录用户回答
  const currentRound = rounds.value[rounds.value.length - 1]
  currentRound.userAnswer = input.value
  input.value = ''      // 清空输入框

  // 3️⃣ 调用 AI 教练接口
  let aiResponse
  try {
    aiResponse = await chatWithCoach({
      role: roleName.value,
      question: currentRound.userAnswer
    })
  } catch (e) {
    console.error('AI 教练接口调用失败', e)
    sendError.value = true
    ElMessage.error('AI 回复生成失败，请重试')
    sending.value = false
    return
  }

  // 4️⃣ 填充 AI 回复和评分
  currentRound.aiReply = aiResponse.reply
  currentRound.score = {
    value: aiResponse.score,
    feedback: aiResponse.feedback
  }

  // 保存训练轮次到后端
  // 如果没有当前 session，先创建（确保首次回答能入库）
  if (!currentSessionId.value) {
    if (!creatingSession.value) {
      creatingSession.value = true
      try {
        const s = await createSession(roleName.value)
        const created = {
          id: s.id || s.session_id,
          title: s.title,
          roleName: s.role_name || s.roleName || roleName.value,
          create_time: s.create_time || new Date().toISOString(),
          update_time: s.update_time || s.updateTime || new Date().toISOString()
        }
        sessions.value.unshift(created)
        currentSessionId.value = created.id
      } catch (e) {
        console.error('首次创建训练会话失败，无法保存本轮记录', e)
        ElMessage.error('创建训练会话失败，请稍后重试')
      } finally {
        creatingSession.value = false
      }
    }
  }

  if (currentSessionId.value) {
    saving.value = true
    try {
      await saveTrainRound({
        session_id: currentSessionId.value,
        ai_question: currentRound.aiQuestion,
        user_text: currentRound.userAnswer,
        ai_reply: currentRound.aiReply,
        score: aiResponse.score,
        feedback: aiResponse.feedback
      })
    } catch (e) {
      console.error('保存训练轮次失败', e)
      ElMessage.error('保存训练记录失败')
    } finally {
      saving.value = false
    }
  }

  // 请求 AI 生成下一轮提问（优先使用后端/模型生成的问题）
  let nextQuestion = '请继续补充你对商圈成熟度的判断。'
  questionLoading.value = true
  try {
    const nqRes = await chatWithCoachQuestion({
      role: roleName.value,
      last_question: currentRound.aiQuestion,
      type: 'followup',
      session_id: currentSessionId.value
    })

    nextQuestion = nqRes.nextQuestion || nqRes.next_question || nqRes.reply || nextQuestion
  } catch (e) {
    console.error('获取下一轮提问失败', e)
  } finally {
    questionLoading.value = false
  }

  rounds.value.push({
    aiQuestion: nextQuestion,
    userAnswer: '',
    aiReply: '',
    score: null
  })

  // 新消息加入后，滚动到底部
  await nextTick()
  if (chatBox.value) {
    try {
      chatBox.value.scrollTop = chatBox.value.scrollHeight
    } catch (e) {
      // ignore
    }
  }

  // 发送成功后清空草稿
  if (currentSessionId.value) {
    localStorage.removeItem(`draft_${currentSessionId.value}`)
  }

  sending.value = false
}

/**
 * 新建训练 session
 * 点击左侧「新建训练」按钮时触发
 */
const createNewSession = async () => {
  try {
    // 1️⃣ 调用后端接口，创建 session
    // 这里的 roleName.value 会传给后端，存入数据库
    const res = await createSession(roleName.value)

    const newSession = {
      id: res.id || res.session_id,
      title: res.title,
      roleName: res.role_name || res.roleName || roleName.value,
      create_time: res.create_time || new Date().toISOString(),
      update_time: res.update_time || res.updateTime || new Date().toISOString()
    }

    // 2️⃣ 把新 session 插入到左侧列表最前面（后端已按 update_time 排序，前端直接插入）
    sessions.value.unshift(newSession)

    // 3️⃣ 设置为当前 session
    currentSessionId.value = newSession.id

    // 4️⃣ 生成开场问题（由 AI 随机生成开场句），若失败则使用默认
    let opening = '你好，我是你的 AI 冠军教练，请开始你的训练。'
    questionLoading.value = true
    try {
      const oq = await chatWithCoachQuestion({ role: roleName.value, last_question: '', type: 'opening', session_id: newSession.id })
      opening = oq.nextQuestion || oq.next_question || oq.reply || opening
    } catch (e) {
      console.error('获取开场问题失败', e)
    } finally {
      questionLoading.value = false
    }

    // 5️⃣ 重置右侧聊天内容（开始新训练）
    rounds.value = [
      {
        aiQuestion: opening,
        userAnswer: '',
        aiReply: '',
        score: null
      }
    ]

    // 6️⃣ 清空输入框，新会话从头开始
    input.value = ''
  } catch (err) {
    console.error('创建训练失败', err)
  }
}

const switchSession = async (session) => {
  currentSessionId.value = session.id

  // 重置分页状态
  roundsCurrentPage.value = 1
  roundsLoading.value = false

  // 先前端模拟
  questionLoading.value = true
  try {
    // 1️⃣ 调用后端接口，获取历史训练轮次
    const res = await getSessionRounds(session.id)

    // 2️⃣ 保存所有记录并设置总数
    const allRounds = res.map((round, index) => {
      return {
        aiQuestion: round.ai_question || round.aiQuestion || '',
        userAnswer: round.user_text || round.userAnswer || '',
        aiReply: round.ai_reply || round.aiReply || '',
        score: round.score ? {
          value: round.score.value || round.score || 0,
          feedback: round.feedback || round.score.feedback || ''
        } : null
      }
    })

    roundsTotal.value = allRounds.length

    // 3️⃣ 只显示第一页的记录（最新的记录）
    const startIndex = Math.max(0, allRounds.length - roundsPageSize)
    rounds.value = allRounds.slice(startIndex)

    // 切换会话并加载完历史消息后滚动到底部
    await nextTick()
    if (chatBox.value) {
      try {
        chatBox.value.scrollTop = chatBox.value.scrollHeight
      } catch (e) {}
    } else {
      // 兜底：初始化空会话的轮次
      rounds.value = [
        {
          aiQuestion: `欢迎回到${roleName.value}训练会话，请继续提问。`,
          userAnswer: '',
          aiReply: '',
          score: null
        }
      ]
    }
  } catch (e) {
    console.error('加载训练记录失败', e)
    // 异常兜底
    rounds.value = [
      {
        aiQuestion: `加载记录失败，请重新开始${roleName.value}训练。`,
        userAnswer: '',
        aiReply: '',
        score: null
      }
    ]
    // 出错时也尝试滚动到底部
    await nextTick()
    if (chatBox.value) {
      try { chatBox.value.scrollTop = chatBox.value.scrollHeight } catch (e) {}
    }
  } finally {
    questionLoading.value = false
  }

  // 恢复当前会话的草稿
  restoreDraft()
}

// 返回主页
const backToDashboard = () => {
  router.push('/dashboard')
}
</script>

<style scoped>
/* ======================
   整体布局
====================== */

.train-layout {
  display: flex;
  height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #f1f3f6 100%);
}

/* ======================
   左侧侧边栏
====================== */

.sidebar {
  width: 260px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fdfb 100%);
  border-right: 1px solid #e8eef3;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
}

.sidebar-header {
  padding: 20px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid #f0f5f9;
}

.sidebar-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #1e5e4a 0%, #2f5d50 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 新建训练按钮 */
.new-session {
  padding: 16px;
  background: linear-gradient(135deg, #34d399 0%, #2ec999 100%);
  margin: 12px 12px 0;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(52, 211, 153, 0.25);
}

.new-session-btn {
  width: 100%;
  background: white !important;
  color: #2f5d50 !important;
  font-weight: 600;
  border: none !important;
  box-shadow: none !important;
  transition: all 0.3s ease;
}

.new-session-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15) !important;
}

/* 历史 session 列表 */
.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.session-item {
  padding: 12px 14px;
  border-radius: 10px;
  cursor: pointer;
  margin-bottom: 8px;
  background: transparent;
  border: 2px solid transparent;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  margin-left: 8px;
  margin-right: 8px;
}

.session-item:hover {
  background: rgba(52, 211, 153, 0.08);
  border-color: rgba(52, 211, 153, 0.3);
}

.session-item.active {
  border-color: #34d399;
  background: linear-gradient(135deg, rgba(52, 211, 153, 0.15) 0%, rgba(52, 211, 153, 0.05) 100%);
  box-shadow: 0 2px 8px rgba(52, 211, 153, 0.2);
}

.session-title {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  transition: color 0.3s ease;
}

.session-item:hover .session-title {
  color: #2f5d50;
}

.session-meta {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 6px;
  transition: color 0.3s ease;
}

.session-item:hover .session-meta {
  color: #6b7280;
}

/* ======================
   右侧主区域
====================== */

.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* 顶部固定栏 */
.fixed-header {
  height: 64px;
  background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
  border-bottom: 2px solid #f0f5f9;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 20px;
  position: sticky;
  top: 0;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: auto;
}

.fixed-header p {
  margin: 0;
  color: #2f5d50;
  font-weight: 500;
}

.back-btn-train {
  color: #2f5d50;
  font-weight: 500;
  padding: 8px 12px;
  transition: all 0.3s ease;
}

.back-btn-train:hover {
  color: #1a3a34;
  background: rgba(47, 93, 80, 0.1);
  border-radius: 4px;
}

/* 训练进度样式 */
.progress-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 0 24px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: #6b7280;
}

.progress-label {
  font-weight: 600;
  color: #1f2937;
  background: linear-gradient(135deg, #34d399 0%, #2ec999 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.progress-stats {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-display {
  color: #059669;
  font-weight: 500;
  background: #ecfdf5;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
}

.progress-bar {
  width: 100%;
}

/* ======================
   聊天区
====================== */

.chat-box {
  flex: 1;
  padding: 28px;
  overflow-y: auto;
  background: linear-gradient(135deg, #f5f7fa 0%, #f8fdfb 100%);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.chat-item {
  display: flex;
}

.chat-item.user {
  justify-content: flex-end;
}

.chat-item.ai {
  justify-content: flex-start;
}

.round {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.bubble {
  max-width: 65%;
  padding: 14px 18px;
  border-radius: 16px;
  background: #ffffff;
  line-height: 1.7;
  position: relative;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  word-break: break-word;
}

.user-bubble {
  background: linear-gradient(135deg, #34d399 0%, #2ec999 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(52, 211, 153, 0.3);
}

.loading-bubble {
  background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
  color: #6b7280;
  font-style: italic;
  opacity: 1;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
  padding: 16px 20px;
}

.loading-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.loading-text {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: #065f46;
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-bubble .el-icon {
  font-size: 20px;
  color: #34d399;
  margin-top: 2px;
  animation: spin 1.5s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-bubble {
  background: linear-gradient(135deg, #fef2f2 0%, #ffe5e5 100%);
  color: #dc2626;
  border: 2px solid #fca5a5;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
  box-shadow: 0 4px 15px rgba(220, 38, 38, 0.15);
}

/* ======================
   输入区
====================== */

.input-box {
  padding: 20px;
  border-top: 2px solid #f0f5f9;
  display: flex;
  gap: 12px;
  background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.04);
}

/* ======================
   评分卡片
====================== */

.score-card {
  width: 320px;
  background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
  border-left: 5px solid #34d399;
  box-shadow: 0 4px 15px rgba(52, 211, 153, 0.2);
  border-radius: 12px !important;
  transition: all 0.3s ease;
}

.score-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(52, 211, 153, 0.25);
}

.score-card h4 {
  margin-top: 0;
  color: #065f46;
  font-weight: 700;
}

/* 更多历史按钮 */
.more-history {
  padding: 12px 16px;
  border-top: 2px solid #f0f5f9;
  margin-top: auto;
}

.more-history .el-button {
  width: 100%;
  justify-content: center;
}

/* 历史记录弹窗 */
.history-dialog-content {
  max-height: 400px;
  overflow-y: auto;
}

.history-item {
  padding: 14px 16px;
  border-radius: 10px;
  cursor: pointer;
  margin-bottom: 10px;
  background: #ffffff;
  border: 2px solid transparent;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.history-item:hover {
  background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
  border-color: #34d399;
  box-shadow: 0 4px 12px rgba(52, 211, 153, 0.15);
  transform: translateX(4px);
}

.history-item.active {
  border-color: #34d399;
  background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
  box-shadow: 0 4px 15px rgba(52, 211, 153, 0.2);
}

.history-title {
  font-size: 14px;
  font-weight: 500;
  color: #065f46;
  margin-bottom: 4px;
}

.history-meta {
  font-size: 12px;
  color: #6b7280;
  display: flex;
  justify-content: space-between;
}

.history-meta span {
  flex: 1;
}

/* 加载更多指示器 */
.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 20px;
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
  background: linear-gradient(135deg, rgba(52, 211, 153, 0.05) 0%, rgba(52, 211, 153, 0.02) 100%);
  border-radius: 10px;
  margin-bottom: 12px;
}

.loading-more .el-icon {
  font-size: 18px;
  color: #34d399;
}
</style>
