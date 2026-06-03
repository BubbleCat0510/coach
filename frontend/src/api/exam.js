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

// 获取随机题目（正式考试用）
export function getRandomQuestions() {
  return request.get('/exam/random_questions')
}

// 获取历史成绩列表
export function getExamHistory(page = 1, pageSize = 10) {
  return request.get('/exam/history', {
    params: { page, page_size: pageSize }
  })
}

// 获取所有员工成绩（管理员专用）
export function getAllExamResults(page = 1, pageSize = 10, keyword = '', role = '') {
  return request.get('/exam/all_exam_results', {
    params: { page, page_size: pageSize, keyword, role }
  })
}