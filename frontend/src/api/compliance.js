import { getToken } from '@/utils/authSession'

const BASE = '/api/compliance'

function buildQuery(params = {}) {
  const q = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => {
    if (v === undefined || v === null || v === '') return
    q.append(k, v)
  })
  const qs = q.toString()
  return qs ? `?${qs}` : ''
}

export async function fetchCompliancePreview({ start, end, region } = {}) {
  const token = getToken()
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers.Authorization = `Bearer ${token}`

  const res = await fetch(`${BASE}/report/preview${buildQuery({ start, end, region })}`, {
    method: 'GET',
    headers,
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(data?.msg || '获取合规分析报告失败')
  }
  return data
}

export async function exportComplianceReport({ start, end, region, format = 'pdf' } = {}) {
  const token = getToken()
  const headers = {}
  if (token) headers.Authorization = `Bearer ${token}`

  const params = buildQuery({ start, end, region, format })
  const res = await fetch(`${BASE}/report/export${params}`, {
    method: 'GET',
    headers,
  })

  if (!res.ok) {
    let message = '导出合规分析报告失败'
    try {
      const data = await res.json()
      if (data?.msg) message = data.msg
    } catch {
      const text = await res.text()
      if (text) message = text
    }
    throw new Error(message)
  }

  const blob = await res.blob()
  return blob
}

export default {
  fetchCompliancePreview,
  exportComplianceReport,
}


