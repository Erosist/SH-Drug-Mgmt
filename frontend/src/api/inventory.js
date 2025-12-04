import axios from 'axios'
import { getToken } from '@/utils/authSession'

// 创建axios实例
const apiClient = axios.create({
  baseURL: '', // 使用相对路径，让Vite代理处理/api请求
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
      localStorage.removeItem('access_token')
      localStorage.removeItem('current_user')
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

// 库存明细手工管理相关API
export const inventoryItemApi = {
  /**
   * 查询当前企业的库存批次
   */
  list: (params = {}) => {
    return apiClient.get('/api/v1/inventory/items', { params })
  },

  /**
   * 查看单个库存批次
   */
  getDetail: (itemId) => {
    return apiClient.get(`/api/v1/inventory/items/${itemId}`)
  },

  /**
   * 手工新增库存批次
   */
  create: (payload) => {
    return apiClient.post('/api/v1/inventory/items', payload)
  },

  /**
   * 调整现有库存批次（数量改动、备注等）
   */
  update: (itemId, payload) => {
    return apiClient.put(`/api/v1/inventory/items/${itemId}`, payload)
  }
}

export default apiClient
