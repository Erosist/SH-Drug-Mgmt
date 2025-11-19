import axios from 'axios'
import { getToken } from '@/utils/authSession'

// 创建axios实例
const apiClient = axios.create({
  baseURL: '',
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

// 供应信息相关API
export const supplyApi = {
  /**
   * 发布供应信息
   */
  createSupplyInfo: (data) => {
    return apiClient.post('/api/supply/info', data)
  },

  /**
   * 获取供应信息列表
   */
  getSupplyList: (params = {}) => {
    return apiClient.get('/api/supply/info', { params })
  },

  /**
   * 获取供应信息详情
   */
  getSupplyInfo: (id) => {
    return apiClient.get(`/api/supply/info/${id}`)
  },

  /**
   * 更新供应信息
   */
  updateSupplyInfo: (id, data) => {
    return apiClient.put(`/api/supply/info/${id}`, data)
  },

  /**
   * 删除供应信息
   */
  deleteSupplyInfo: (id) => {
    return apiClient.delete(`/api/supply/info/${id}`)
  }
}

// 药品相关API
export const drugApi = {
  /**
   * 获取药品列表
   */
  getDrugList: (params = {}) => {
    return apiClient.get('/api/supply/drugs', { params })
  }
}

export default apiClient
