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

function resolveToken(explicitToken) {
	if (explicitToken) return explicitToken;
	try {
		return localStorage.getItem('access_token') || undefined;
	} catch {
		return undefined;
	}
}

export function register({ username, email, password, phone }) {
	const payload = { username, email, password };
	if (phone) payload.phone = phone;
	return request('/register', { method: 'POST', body: payload });
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

export function changePassword({ oldPassword, newPassword, token }) {
	return request('/change-password', {
		method: 'POST',
		body: { old_password: oldPassword, new_password: newPassword },
		token: resolveToken(token)
	});
}

export function resetPassword({ identifier, channel, contact, newPassword }) {
	return request('/reset-password', {
		method: 'POST',
		body: { identifier, channel, contact, newPassword }
	});
}

export function adminResetUserPassword({ userId, identifier, newPassword, token }) {
	const body = { new_password: newPassword }
	if (userId !== undefined && userId !== null) body.user_id = userId
	if (identifier) body.identifier = identifier
	return request('/admin/reset-user-password', {
		method: 'POST',
		body,
		token: resolveToken(token)
	})
}

export default { register, login, me, changePassword, resetPassword, adminResetUserPassword };
