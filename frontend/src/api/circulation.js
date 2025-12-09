import axios from 'axios'
import { getToken } from '@/utils/authSession'

const apiClient = axios.create({
  baseURL: '',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

apiClient.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.msg || error.message || '请求失败'
    return Promise.reject(new Error(message))
  }
)

/**
 * 上报流通数据
 * @param {Object} payload - 上报数据
 * @param {string} payload.tracking_number - 运单号（必填）
 * @param {string} payload.transport_status - 运输状态：SHIPPED|IN_TRANSIT|DELIVERED（必填）
 * @param {string} payload.timestamp - 时间戳，ISO格式（必填）
 * @param {string} [payload.current_location] - 当前位置文字描述（可选）
 * @param {number} [payload.latitude] - 纬度（可选）
 * @param {number} [payload.longitude] - 经度（可选）
 * @param {string} [payload.remarks] - 备注信息（可选）
 * @returns {Promise<Object>} 返回上报结果
 */
export function reportCirculation(payload) {
  return apiClient.post('/api/circulation/report', payload)
}

/**
 * 获取指定运单号的流通记录列表
 * @param {string} tracking_number - 运单号
 * @returns {Promise<Object>} 返回流通记录列表
 */
export function getCirculationRecords(tracking_number) {
  return apiClient.get(`/api/circulation/records/${tracking_number}`)
}

/**
 * 药品全生命周期追溯
 * @param {Object} params - 查询参数
 * @param {string} params.tracking_number - 运单号（必填）
 * @param {string} [params.start_date] - 开始日期，ISO格式（可选）
 * @param {string} [params.end_date] - 结束日期，ISO格式（可选）
 * @returns {Promise<Object>} 返回追溯结果，包含时间轴和流向图数据
 */
export function traceDrug({ tracking_number, start_date, end_date }) {
  const params = new URLSearchParams()
  params.append('tracking_number', tracking_number)
  if (start_date) params.append('start_date', start_date)
  if (end_date) params.append('end_date', end_date)
  
  return apiClient.get(`/api/circulation/trace?${params.toString()}`)
}

/**
 * 获取监管看板数据
 * @param {Object} params - 查询参数
 * @param {string} params.range - 时间范围（7d, 30d, 90d）
 * @param {string} params.region - 区域范围（省份或 all）
 * @param {string} [params.start_date] - 自定义开始时间（ISO）
 * @param {string} [params.end_date] - 自定义结束时间（ISO）
 */
export function getDashboard(params = {}) {
  return apiClient.get('/api/circulation/dashboard', { params })
}

export default { reportCirculation, getCirculationRecords, traceDrug, getDashboard }
