import request from './request'

// 新建训练 session
export function createSession(role) {
  if (!role) role = 'no'
  return request.post('/train/session', {
    role
  })
}

// 获取 session 列表（侧边栏）
export function getSessionList() {
  return request.get('/train/session/list')
}

// 获取某个 session 的历史轮次
export function getSessionRounds(sessionId) {
  return request.get('/train/rounds', {
    params: {
      session_id: sessionId
    }
  })
}

// 保存一轮训练对话
export function saveTrainRound(data) {
  return request.post('/train/round', data)
}