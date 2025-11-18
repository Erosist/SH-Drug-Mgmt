const BASE = '/api/catalog';

function buildQuery(params = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return;
    query.append(key, value);
  });
  const qs = query.toString();
  return qs ? `?${qs}` : '';
}

async function request(path, params) {
  const res = await fetch(`${BASE}${path}${buildQuery(params)}`);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data?.msg || '请求失败');
  }
  return data;
}

export function fetchDrugs({ keyword, page = 1, perPage = 10, category, prescriptionType } = {}) {
  return request('/drugs', {
    keyword,
    page,
    per_page: perPage,
    category,
    prescription_type: prescriptionType
  });
}

export function fetchTenants({ keyword, page = 1, perPage = 10, type, isActive } = {}) {
  return request('/tenants', {
    keyword,
    page,
    per_page: perPage,
    type,
    is_active: typeof isActive === 'boolean' ? String(isActive) : isActive
  });
}

export function fetchInventory({ keyword, page = 1, perPage = 10, tenantId, drugId } = {}) {
  return request('/inventory', {
    keyword,
    page,
    per_page: perPage,
    tenant_id: tenantId,
    drug_id: drugId
  });
}

export default { fetchDrugs, fetchTenants, fetchInventory };
