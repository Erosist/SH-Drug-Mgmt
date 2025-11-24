import { describe, it, expect } from 'vitest'
import { createRouter, createWebHistory } from 'vue-router'

// 创建测试路由配置
const testRoutes = [
  { path: '/', name: 'Home', component: { template: '<div>Home</div>' } },
  { path: '/login', name: 'Login', component: { template: '<div>Login</div>' } },
  { path: '/register', name: 'Register', component: { template: '<div>Register</div>' } },
  { path: '/inventory', name: 'Inventory', component: { template: '<div>Inventory</div>' } },
  { path: '/b2b', name: 'B2B', component: { template: '<div>B2B</div>' } },
  { path: '/analysis', name: 'Analysis', component: { template: '<div>Analysis</div>' } }
]

describe('Router 基础功能测试', () => {
  it('应该正确创建路由器', () => {
    const router = createRouter({
      history: createWebHistory(),
      routes: testRoutes
    })

    expect(router).toBeDefined()
    expect(router.options.history).toBeDefined()
  })

  it('应该包含基本路由', () => {
    const router = createRouter({
      history: createWebHistory(),
      routes: testRoutes
    })

    const routes = router.getRoutes()

    // 检查是否包含主要路由
    expect(routes.some(route => route.path === '/')).toBe(true)
    expect(routes.some(route => route.path === '/login')).toBe(true)
    expect(routes.some(route => route.path === '/register')).toBe(true)
    expect(routes.some(route => route.path === '/inventory')).toBe(true)
    expect(routes.some(route => route.path === '/b2b')).toBe(true)
    expect(routes.some(route => route.path === '/analysis')).toBe(true)
  })

  it('应该能够正确解析路由', async () => {
    const router = createRouter({
      history: createWebHistory(),
      routes: testRoutes
    })

    await router.push('/login')
    expect(router.currentRoute.value.name).toBe('Login')

    await router.push('/inventory')
    expect(router.currentRoute.value.name).toBe('Inventory')
  })
})
