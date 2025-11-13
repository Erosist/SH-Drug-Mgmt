// 简单的基于 fetch 的 API 封装，使用 Vite 代理转发到后端
const base = '/api/auth';

async function request(path, { method = 'GET', body, token } = {}) {
	const headers = { 'Content-Type': 'application/json' };
	if (token) headers['Authorization'] = `Bearer ${token}`;
	const res = await fetch(`${base}${path}`, {
		method,
		headers,
		body: body ? JSON.stringify(body) : undefined,
	});
	const data = await res.json().catch(() => ({}));
	if (!res.ok) {
		const msg = data?.msg || res.statusText || 'Request Error';
		throw new Error(msg);
	}
	return data;
}

export function register({ username, email, password, role }) {
	return request('/register', { method: 'POST', body: { username, email, password, role } });
}

export function login({ username, password }) {
	return request('/login', { method: 'POST', body: { username, password } });
}

export function me(token) {
	// 允许不传 token 时自动从本地获取
	try {
		if (!token) token = localStorage.getItem('access_token')
	} catch {}
	return request('/me', { method: 'GET', token });
}

export default { register, login, me };
