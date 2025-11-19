import { getToken } from '@/utils/authSession'

const BASE = '/api/admin'

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

export function fetchUsers({ keyword, role, status, page = 1, perPage = 10 } = {}) {
  return request('/users', { params: { keyword, role, status, page, per_page: perPage } })
}

export function updateUserStatus(userId, action) {
  return request(`/users/${userId}/status`, { method: 'POST', body: { action } })
}

export default { fetchUsers, updateUserStatus }
