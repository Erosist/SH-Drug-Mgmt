const ROLE_LABELS = {
  pharmacy: '药店用户',
  supplier: '供应商用户',
  logistics: '物流用户',
  regulator: '监管用户',
  admin: '系统管理员',
  unauth: '未认证用户'
}

export function getRoleLabel(role) {
  if (!role) {
    return '未登录'
  }
  return ROLE_LABELS[role] || '未知角色'
}

export function isApprovedRole(role) {
  return role && !['unauth'].includes(role)
}
