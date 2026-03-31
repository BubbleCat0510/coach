import axios from 'axios'

// 创建 axios 实例
const request = axios.create({
  baseURL: 'http://localhost:8001', // FastAPI 地址
  timeout: 10000                   // 超时时间
})

// 请求拦截器（每次请求前）
request.interceptors.request.use(
  config => {
    // 从本地存储中读取 token
    const token = localStorage.getItem('token')

    // 如果有 token，就带到请求头里
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器（每次响应后）
request.interceptors.response.use(
  response => {
    // 直接返回后端数据
    return response.data
  },
  error => {
    return Promise.reject(error)
  }
)

export default request
