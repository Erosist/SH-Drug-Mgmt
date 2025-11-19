import axios from 'axios'
import { getToken } from '@/utils/authSession'

// 创建axios实例
const apiClient = axios.create({
  baseURL: 'http://localhost:5000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token过期或无效，跳转到登录页
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 库存预警相关API
export const inventoryWarningApi = {
  /**
   * 获取库存预警列表
   */
  getWarnings: (params = {}) => {
    return apiClient.get('/api/v1/inventory/warnings', { params })
  },

  /**
   * 获取预警统计摘要
   */
  getWarningSummary: () => {
    return apiClient.get('/api/v1/inventory/warning-summary')
  },

  /**
   * 手动触发预警扫描（管理员功能）
   */
  scanWarnings: () => {
    return apiClient.post('/api/v1/inventory/scan-warnings')
  }
}

export default apiClient
