// 统一的鉴权会话管理（使用真实后端登录）
// 本模块负责读取/写入本地 token 与用户信息，替代 mocks/auth 中的同类能力

export const AUTH_TOKEN_KEY = 'access_token'
export const AUTH_USER_KEY = 'current_user'

export function getToken() {
	try {
		return localStorage.getItem(AUTH_TOKEN_KEY) || null
	} catch {
		return null
	}
}

export function getCurrentUser() {
	try {
		const raw = localStorage.getItem(AUTH_USER_KEY)
		return raw ? JSON.parse(raw) : null
	} catch {
		return null
	}
}

export function setAuth(token, user) {
	try {
		if (token) localStorage.setItem(AUTH_TOKEN_KEY, token)
		if (user) localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user))
	} catch {}
}

export function clearAuth() {
	try {
		localStorage.removeItem(AUTH_TOKEN_KEY)
		localStorage.removeItem(AUTH_USER_KEY)
		// 清理旧的 mock 遗留键
		localStorage.removeItem('mock_auth_current_user')
	} catch {}
}

export function isAuthenticated() {
	return !!getToken() && !!getCurrentUser()
}

export default { getToken, getCurrentUser, setAuth, clearAuth, isAuthenticated }
