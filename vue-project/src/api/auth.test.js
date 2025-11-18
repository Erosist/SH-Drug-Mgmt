// vue-project/src/api/auth.test.js

// 导入 Vitest 的“测试工具”（比如 expect, it, vi）
import { describe, it, expect, vi, beforeEach } from 'vitest'

// 导入我们要“测试”的“零件”（你写的 auth.js）
import { login } from './auth.js' 

// --- 关键一步：我们必须“模拟” (Mock) 掉 fetch ---
// "单元测试"不应该真的去发网络请求
// 我们告诉 Vitest：“如果代码里调用了 fetch，你就假装它成功了”
global.fetch = vi.fn()

describe('auth.js - 登录函数', () => {

  // 在“每次测试 (it)”之前，都“重置”一下 fetch 这个“模拟器”
  beforeEach(() => {
    vi.clearAllMocks()
  })

  // --- 我们的第一个前端测试用例 ---
  // （你的 .gitlab-ci.yml 里的 vitest 就会来运行这个 'it'）
  it('当调用 login 时，应该用正确的 URL 和 Body 去 fetch', async () => {
    
    // 1. 准备“假”数据（假装服务器返回了这个）
    const mockSuccessResponse = { access_token: 'fake_token' }
    global.fetch.mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue(mockSuccessResponse),
    })

    // 2. 真正“运行”你的 login 函数
    await login({ username: 'testuser', password: '123' })

    // 3. 断言 (Assert)：
    // 我们“断言” fetch（“模拟器”）是不是被“正确地”调用了？
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/auth/login', // （检查 URL 对不对）
      expect.objectContaining({
        method: 'POST',     // （检查方法对不对）
        body: JSON.stringify({ username: 'testuser', password: '123' }) // （检查 Body 对不对）
      })
    )
  })
})