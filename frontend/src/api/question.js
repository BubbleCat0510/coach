import request from './request'

// 获取题目列表
export function getQuestionList(params) {
  return request.get('/question/list', { params })
}

// 获取单个题目
export function getQuestion(id) {
  return request.get(`/question/${id}`)
}

// 添加题目
export function addQuestion(data) {
  return request.post('/question/add', data)
}

// 更新题目
export function updateQuestion(id, data) {
  return request.post(`/question/update/${id}`, data)
}

// 删除题目
export function deleteQuestion(id) {
  return request.post(`/question/delete/${id}`)
}

// 获取分类列表
export function getCategories() {
  return request.get('/question/categories')
}
