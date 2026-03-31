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