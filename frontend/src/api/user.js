import request from './request'

// 获取员工昵称
export function getNickname() {
  return request.post('/user/nickname')
}

// 获取员工的个人信息
export function getProfile() {
  return request.get('/user/profile')
}

// 获取员工的岗位
export function getUserRole() {
  return request.get('/user/role')
}

// 获取用户列表（管理员权限）
export function getUserList() {
  return request.get('/user/list')
}

// 更新用户角色
export function updateRole(role) {
  return request.post('/user/update-role', null, {
    params: { role }
  })
}

// 添加用户
export function createUser(userData) {
  return request.post('/user/create', userData)
}

// 更新用户
export function updateUser(userData) {
  return request.post('/user/update', userData)
}

// 删除用户
export function deleteUser(userId) {
  return request.post('/user/delete', { id: userId })
}