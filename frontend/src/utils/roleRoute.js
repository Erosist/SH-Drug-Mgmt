// 角色到路由的映射
export function roleToRoute(role) {
  if (role === 'unauth') {
    return '/unauth'
  }
  // 其他角色默认跳转首页
  return '/'
}

export default { roleToRoute }
