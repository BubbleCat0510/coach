import request from './request'

// 开始测试
export function startExam(mode) {
  return request.post('/exam/start', {
    exam_mode: mode
  })
}

// 提交答案
export function submitExamAnswer(data) {
  /**
   * 批量提交整轮答案
   * @param {Object} data - 提交参数
   * @param {number} data.session_id - 考试会话ID
   * @param {Array} data.round_answers - 每轮答案列表（含耗时）
   */
  return request.post('/exam/answer', data)
}

// 结束测试
export function finishExam(sessionId) {
  return request.post('/exam/finish', {
    session_id: sessionId
  })
}

// 获取测试结果
export function getExamResult(sessionId) {
  return request.get('/exam/result', {
    params: { session_id: sessionId }
  })
}

// 保存考试结果
export function saveExamResult(data) {
  return request.post('/exam/save_result', data)
}