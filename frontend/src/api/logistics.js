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

// 物流相关API
export const logisticsApi = {
  /**
   * 获取物流订单列表
   * @param {Object} params - 查询参数
   * @param {string} params.order_no - 订单号（模糊查询）
   * @param {string} params.tracking_number - 运单号（模糊查询）
   * @param {string} params.status - 订单状态（SHIPPED/IN_TRANSIT/DELIVERED）
   * @param {string} params.start_date - 开始日期（ISO格式）
   * @param {string} params.end_date - 结束日期（ISO格式）
   * @returns {Promise<AxiosResponse>}
   */
  getOrders: (params = {}) => {
    return apiClient.get('/api/logistics/orders', { params })
  },

  /**
   * 获取物流公司列表
   * @returns {Promise<AxiosResponse>}
   */
  getCompanies: () => {
    return apiClient.get('/api/logistics/companies')
  },

  /**
   * 更新订单物流状态（预留接口）
   * @param {number} orderId - 订单ID
   * @param {Object} data - 更新数据
   * @param {string} data.status - 新状态
   * @param {string} data.tracking_number - 运单号
   * @returns {Promise<AxiosResponse>}
   */
  updateOrderStatus: (orderId, data) => {
    return apiClient.put(`/api/logistics/orders/${orderId}/status`, data)
  },

  /**
   * 获取订单详情（预留接口）
   * @param {number} orderId - 订单ID
   * @returns {Promise<AxiosResponse>}
   */
  getOrderDetail: (orderId) => {
    return apiClient.get(`/api/logistics/orders/${orderId}`)
  }
}

export default logisticsApi
