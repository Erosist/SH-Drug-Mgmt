// 角色到路由的映射
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
    case 'admin':
      return '/'
    case 'unauth':
    default:
      return '/unauth'
  }
}

export default { roleToRoute }
