import request from './request'

// 上传文件
export function uploadFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/upload/file', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取文件列表
export function getFileList(page = 1, pageSize = 10, search = '') {
  return request.get('/upload/list', {
    params: {
      page,
      pageSize,
      search
    }
  })
}

// 删除文件
export function deleteFile(fileId) {
  return request.post('/upload/delete', { file_id: fileId })
}

// 更新学习进度
export function updateProgress(fileId, progress, learningTime = 0) {
  return request.post('/upload/progress', {
    file_id: fileId,
    progress,
    learning_time: learningTime
  })
}

// 获取学习进度
export function getProgress(fileId) {
  return request.get(`/upload/progress/${fileId}`)
}

// 获取学习情况（管理员用）
export function getLearningStatus(page = 1, pageSize = 10, search = '') {
  return request.get('/upload/learning-status', {
    params: {
      page,
      pageSize,
      search
    }
  })
}
