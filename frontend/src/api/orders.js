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

// 订单相关API
export const orderApi = {
  /**
   * 创建订单（下单）
   */
  createOrder: (data) => {
    return apiClient.post('/api/orders', data)
  },

  /**
   * 获取订单列表
   */
  getOrders: (params = {}) => {
    return apiClient.get('/api/orders', { params })
  },

  /**
   * 获取订单详情
   */
  getOrderDetail: (orderId) => {
    return apiClient.get(`/api/orders/${orderId}`)
  },

  /**
   * 供应商确认/拒绝订单
   * action: 'accept' | 'reject'
   */
  confirmOrder: (orderId, data) => {
    return apiClient.post(`/api/orders/${orderId}/confirm`, data)
  },

  /**
   * 药店取消订单
   */
  cancelOrder: (orderId, data) => {
    return apiClient.post(`/api/orders/${orderId}/cancel`, data)
  },

  /**
   * 供应商发货
   */
  shipOrder: (orderId, data) => {
    return apiClient.post(`/api/orders/${orderId}/ship`, data)
  },

  /**
   * 药店确认收货
   */
  receiveOrder: (orderId, data) => {
    return apiClient.post(`/api/orders/${orderId}/receive`, data)
  },

  /**
   * 获取订单统计信息
   */
  getOrderStats: () => {
    return apiClient.get('/api/orders/stats')
  },

  /**
   * 更新订单状态（物流公司和管理员功能）
   */
  updateOrderStatus: (orderId, status) => {
    return apiClient.patch(`/api/orders/status/${orderId}`, { status })
  },

  /**
   * 获取物流公司列表
   */
  getLogisticsCompanies: () => {
    return apiClient.get('/api/logistics/companies')
  },

  /**
   * 获取物流公司的订单列表
   */
  getLogisticsOrders: (params = {}) => {
    return apiClient.get('/api/logistics/orders', { params })
  }
}

export default apiClient
