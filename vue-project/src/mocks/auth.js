// 简单前端 Mock 鉴权，无后端环境
// 提供几个内置账户（角色不同），使用 localStorage 持久化当前登录状态

const STORAGE_KEY = 'mock_auth_current_user'

// 预置账户（密码全部使用明文模拟，真实项目需加密）
// role 用于决定跳转哪个界面
export const users = [
  {
    username: 'pharmacy_admin',
    password: '123456',
    role: 'pharmacy',
    displayName: '药店管理员',
  },
  {
    username: 'supplier_user',
    password: '123456',
    role: 'supplier',
    displayName: '供应商用户',
  },
  {
    username: 'logistics_mgr',
    password: '123456',
    role: 'logistics',
    displayName: '物流管理员',
  },
  {
    username: 'regulator_staff',
    password: '123456',
    role: 'regulator',
    displayName: '监管人员',
  },
  {
    username: 'unauth_user',
    password: '123456',
    role: 'unauth',
    displayName: '未认证用户',
  },
]

// 已废弃：真实登录改为调用后端 /api/auth/login
export function login() {
  throw new Error('前端 mock 登录已禁用，请使用后端登录接口')
}

export function logout() {
  localStorage.removeItem(STORAGE_KEY)
}

export function getCurrentUser() {
  try {
    // 兼容后端真实登录：优先读取后端登录保存的键
    const real = localStorage.getItem('current_user')
    if (real) return JSON.parse(real)
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch (e) {
    return null
  }
}

// 根据角色返回对应路由路径
export function roleToRoute(role) {
  switch (role) {
    case 'pharmacy':
      return '/pharmacy'
    case 'supplier':
      return '/supplier'
    case 'logistics':
      return '/logistics'
    case 'regulator':
      return '/regulator'
    case 'unauth':
      return '/unauth'
    default:
      return '/'
  }
}

// 是否需要认证的路径统一由路由 meta 控制，这里辅助判断
export function isAuthenticated() {
  return !!getCurrentUser()
}
