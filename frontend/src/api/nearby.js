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

// 就近供应商推荐相关API
export const nearbyApi = {
  /**
   * 获取就近供应商列表
   * @param {Object} params - 查询参数
   * @param {Number} params.longitude - 药店经度
   * @param {Number} params.latitude - 药店纬度
   * @param {String} params.address - 或提供地址（会自动转换为坐标）
   * @param {String} params.city - 城市名称（配合address使用）
   * @param {Number} params.max_distance - 最大搜索半径（米）
   * @param {Number} params.limit - 返回结果数量
   * @param {Boolean} params.use_api - 是否使用高德API计算驾车距离
   */
  getNearbySuppliers: (params) => {
    return apiClient.post('/api/nearby/suppliers', params)
  },

  /**
   * 地理编码：将地址转换为经纬度
   * @param {String} address - 地址
   * @param {String} city - 城市名称（可选）
   */
  geocodeAddress: (address, city = null) => {
    return apiClient.post('/api/nearby/geocode', { address, city })
  },

  /**
   * 计算两点之间的距离
   * @param {Object} origin - 起点 {longitude, latitude}
   * @param {Object} destination - 终点 {longitude, latitude}
   * @param {Boolean} use_api - 是否使用高德API（驾车距离）
   */
  calculateDistance: (origin, destination, use_api = false) => {
    return apiClient.post('/api/nearby/distance', {
      origin,
      destination,
      use_api
    })
  },

  /**
   * 获取当前用户的位置信息
   */
  getMyLocation: () => {
    return apiClient.get('/api/nearby/my-location')
  },

  /**
   * 更新当前用户的位置信息
   * @param {Object} data - 位置数据
   * @param {Number} data.longitude - 经度
   * @param {Number} data.latitude - 纬度
   * 或
   * @param {String} data.address - 地址
   * @param {String} data.city - 城市
   */
  updateMyLocation: (data) => {
    return apiClient.put('/api/nearby/update-location', data)
  }
}

export default nearbyApi
