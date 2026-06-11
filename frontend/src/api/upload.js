import request from './request'

// 上传文件
export function uploadFile(file, category = 'other', role = 1) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('category', category)
  formData.append('role', role)
  return request.post('/upload/file', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取文件列表
export function getFileList(page = 1, pageSize = 10, search = '', role = null) {
  return request.get('/upload/list', {
    params: {
      page,
      pageSize,
      search,
      role
    }
  })
}

// 删除文件
export function deleteFile(id) {
  return request.post('/upload/delete', { id })
}

// 更新学习进度
export function updateProgress(id, progress, learningTime = 0, role = 1) {
  return request.post('/upload/progress', {
    id,
    progress,
    learningTime,
    role
  })
}

// 获取学习进度
export function getProgress(fileId, role = 1) {
  return request.get(`/upload/progress/${fileId}`, {
    params: {
      role
    }
  })
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

export function getMyLearningRecords() {
  return request.get('/upload/my-learning-records')
}
