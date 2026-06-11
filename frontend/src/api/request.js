import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

// 创建 axios 实例
const request = axios.create({
  baseURL: 'http://localhost:8001', // FastAPI 地址
  timeout: 60000                   // 超时时间
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

// 检查是否包含敏感信息（异常堆栈）
const containsSensitiveInfo = (message) => {
  if (!message || typeof message !== 'string') return false
  const sensitivePatterns = [
    'Traceback',
    'Stack trace',
    'File "/',
    'line \\d+',
    'Exception:',
    'Error:',
    'at ',
    '\\.py:',
    '\\.js:'
  ]
  return sensitivePatterns.some(pattern => new RegExp(pattern).test(message))
}

// 处理错误消息，过滤敏感信息
const handleErrorMessage = (message, defaultMessage) => {
  if (!message || typeof message !== 'string') {
    return defaultMessage
  }
  // 如果包含敏感信息，使用默认消息
  if (containsSensitiveInfo(message)) {
    console.warn('检测到敏感错误信息，已过滤:', message)
    return defaultMessage
  }
  // 截取过长的消息
  if (message.length > 200) {
    return message.substring(0, 200) + '...'
  }
  return message
}

// 响应拦截器（每次响应后）
request.interceptors.response.use(
  response => {
    const res = response.data
    
    // 如果返回的是标准格式（包含 success 字段）
    if (res !== null && typeof res === 'object' && 'success' in res) {
      // 业务逻辑失败
      if (!res.success) {
        // 显示错误消息（过滤敏感信息）
        const errorMessage = handleErrorMessage(res.message, '操作失败')
        ElMessage.error(errorMessage)
        // 返回 Promise reject，让调用方可以 catch
        return Promise.reject({
          ...res,
          message: errorMessage
        })
      }
    }
    
    // 成功则直接返回数据
    return res
  },
  error => {
    // 处理错误消息
    const handleError = (message) => {
      ElMessage.error(message)
    }
    
    // HTTP 错误处理
    if (error.response) {
      const status = error.response.status
      const data = error.response.data
      const responseMessage = data && data.message ? data.message : null
      
      switch (status) {
        case 401:
          // Token 失效或未登录
          ElMessageBox.confirm(
            '登录已失效，请重新登录',
            '提示',
            {
              confirmButtonText: '重新登录',
              cancelButtonText: '取消',
              type: 'warning'
            }
          ).then(() => {
            // 清除本地存储
            localStorage.removeItem('token')
            localStorage.removeItem('user')
            // 跳转到登录页面
            window.location.href = '/login'
          }).catch(() => {
            // 用户取消，不做操作
          })
          break
          
        case 403:
          // 无权限
          handleError('暂无权限，请联系管理员')
          break
          
        case 404:
          // 资源不存在
          handleError('请求的资源不存在')
          break
          
        case 400:
          // 请求参数错误
          const badRequestMsg = handleErrorMessage(responseMessage, '请求参数错误')
          handleError(badRequestMsg)
          break
          
        case 500:
          // 服务器内部错误（过滤敏感信息）
          const serverMsg = handleErrorMessage(responseMessage, '服务器内部错误，请稍后重试')
          handleError(serverMsg)
          break
          
        default:
          // 其他错误
          if (responseMessage) {
            const msg = handleErrorMessage(responseMessage, `请求失败，状态码: ${status}`)
            handleError(msg)
          } else {
            handleError(`请求失败，状态码: ${status}`)
          }
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应（网络问题）
      handleError('网络请求超时，请检查网络连接')
    } else {
      // 请求配置错误
      handleError('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)

export default request
