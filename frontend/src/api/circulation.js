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

export function fetchDashboard(params = {}) {
  return apiClient.get('/api/circulation/dashboard', { params })
}

export default { fetchDashboard }
