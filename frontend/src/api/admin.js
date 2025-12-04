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

export function getUserDetail(userId) {
  return request(`/users/${userId}`)
}

export function deleteUser(userId) {
  return request(`/users/${userId}`, { method: 'DELETE' })
}

export function updateUserRole(userId, { role, markAuthenticated }) {
  const body = { role }
  if (markAuthenticated !== undefined) {
    body.mark_authenticated = markAuthenticated
  }
  return request(`/users/${userId}/role`, { method: 'POST', body })
}

export function fetchSystemStatus() {
  return request('/system/status')
}

export async function exportUsersFile(format = 'csv') {
  const token = getToken()
  const headers = {}
  if (token) headers['Authorization'] = `Bearer ${token}`

  const params = buildQuery({ format })
  const res = await fetch(`${BASE}/users/export${params}`, { headers })
  if (!res.ok) {
    let message = '导出用户失败'
    try {
      const data = await res.json()
      if (data?.msg) message = data.msg
    } catch {
      const text = await res.text()
      if (text) message = text
    }
    throw new Error(message)
  }
  return res
}

export function fetchAdminAuditLogs({
  adminId,
  action,
  targetUserId,
  start,
  end,
  page = 1,
  perPage = 20,
} = {}) {
  return request('/audit-logs', {
    params: {
      admin_id: adminId,
      action,
      target_user_id: targetUserId,
      start,
      end,
      page,
      per_page: perPage,
    },
  })
}

export default {
  fetchUsers,
  updateUserStatus,
  getUserDetail,
  deleteUser,
  updateUserRole,
  fetchSystemStatus,
  fetchAdminAuditLogs,
  exportUsersFile,
}
