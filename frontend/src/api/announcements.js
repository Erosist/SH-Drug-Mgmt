/**
 * 公告与资讯 API
 */
import { getToken } from '@/utils/authSession'

const BASE = '/api/announcements'

function buildQuery(params = {}) {
  const q = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => {
    if (v === undefined || v === null || v === '') return
    q.append(k, v)
  })
  const qs = q.toString()
  return qs ? `?${qs}` : ''
}

async function request(path, { method = 'GET', body, params } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  const token = getToken()
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(`${BASE}${path}${buildQuery(params)}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data?.msg || '请求失败')
  return data
}

/**
 * 获取公告列表
 * @param {Object} params - { type, status, page, perPage }
 */
export function fetchAnnouncements({ type, status, page = 1, perPage = 10 } = {}) {
  return request('', { params: { type, status, page, per_page: perPage } })
}

/**
 * 获取单个公告详情
 */
export function getAnnouncement(id) {
  return request(`/${id}`)
}

/**
 * 创建公告（管理员）
 */
export function createAnnouncement(data) {
  return request('', { method: 'POST', body: data })
}

/**
 * 更新公告（管理员）
 */
export function updateAnnouncement(id, data) {
  return request(`/${id}`, { method: 'PUT', body: data })
}

/**
 * 删除公告（管理员）
 */
export function deleteAnnouncement(id) {
  return request(`/${id}`, { method: 'DELETE' })
}

/**
 * 切换公告状态（管理员）
 */
export function toggleAnnouncement(id) {
  return request(`/${id}/toggle`, { method: 'POST' })
}

export default {
  fetchAnnouncements,
  getAnnouncement,
  createAnnouncement,
  updateAnnouncement,
  deleteAnnouncement,
  toggleAnnouncement,
}
