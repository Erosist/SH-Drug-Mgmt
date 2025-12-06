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

// 主页相关API
export const homeApi = {
  /**
   * 获取平台统计数据
   */
  getPlatformStats: () => {
    return apiClient.get('/api/home/stats')
  },

  /**
   * 获取健康资讯列表
   */
  getHealthNews: (params = {}) => {
    return apiClient.get('/api/home/health-news', { params })
  },

  /**
   * 获取紧急通知列表
   */
  getUrgentNotices: (params = {}) => {
    return apiClient.get('/api/home/urgent-notices', { params })
  },

  /**
   * 获取用户个性化统计数据（需要登录）
   */
  getUserStats: () => {
    return apiClient.get('/api/home/user-stats')
  },

  /**
   * 获取最近活动记录（需要登录）
   */
  getRecentActivities: (params = {}) => {
    return apiClient.get('/api/home/recent-activities', { params })
  },

  /**
   * 药品搜索
   */
  searchDrugs: (keyword, page = 1, perPage = 5) => {
    return apiClient.get('/api/catalog/drugs/search', {
      params: { q: keyword, page, per_page: perPage }
    })
  },

  /**
   * 获取药品详情
   */
  getDrugDetail: (drugId) => {
    return apiClient.get(`/api/catalog/drugs/${drugId}`)
  }
}

export default apiClient
