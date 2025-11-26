import { getToken } from '@/utils/authSession'

const BASE = '/api/enterprise'

function buildQuery(params = {}) {
  const query = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return
    query.append(key, value)
  })
  const qs = query.toString()
  return qs ? `?${qs}` : ''
}

async function request(path, { method = 'GET', body, formData = false, params } = {}) {
  const headers = {}
  const token = getToken()
  if (token) headers['Authorization'] = `Bearer ${token}`
  if (!formData) headers['Content-Type'] = 'application/json'

  const res = await fetch(`${BASE}${path}${buildQuery(params)}`, {
    method,
    headers,
    body: formData ? body : body ? JSON.stringify(body) : undefined,
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(data?.msg || res.statusText || '请求失败')
  }
  return data
}

export function fetchRequirements() {
  return request('/requirements')
}

export function fetchMyApplication() {
  return request('/me')
}

export function submitApplication({ role, form, files = [] }) {
  const fd = new FormData()
  fd.append('role', role)
  Object.entries(form || {}).forEach(([key, value]) => fd.append(key, value ?? ''))
  files.forEach((file) => {
    if (file) fd.append('files', file.raw || file)
  })
  return request('/submit', { method: 'POST', body: fd, formData: true })
}

export function fetchApplications({ status = 'pending', role } = {}) {
  return request('/applications', { params: { status, role } })
}

export function fetchApplicationDetail(id) {
  return request(`/applications/${id}`)
}

export function reviewCertificationByCert({ certId, decision, reasonCode, remark }) {
  return request(`/review/${certId}`, {
    method: 'POST',
    body: { decision, reason_code: reasonCode, remark },
  })
}

export default {
  fetchRequirements,
  fetchMyApplication,
  submitApplication,
  fetchApplications,
  fetchApplicationDetail,
  reviewCertificationByCert,
}
