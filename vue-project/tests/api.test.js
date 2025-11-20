import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'

// 模拟axios
vi.mock('axios', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

describe('API 基础功能测试', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('应该能够发送POST请求', async () => {
    const mockData = { message: 'success' }
    axios.post.mockResolvedValue({ data: mockData })

    const response = await axios.post('/api/test', { test: 'data' })

    expect(axios.post).toHaveBeenCalledWith('/api/test', { test: 'data' })
    expect(response.data).toEqual(mockData)
  })

  it('应该能够处理请求错误', async () => {
    const errorMessage = 'Network Error'
    axios.post.mockRejectedValue(new Error(errorMessage))

    await expect(axios.post('/api/test', {})).rejects.toThrow(errorMessage)
  })

  it('应该能够发送GET请求', async () => {
    const mockData = { items: [] }
    axios.get.mockResolvedValue({ data: mockData })

    const response = await axios.get('/api/items')

    expect(axios.get).toHaveBeenCalledWith('/api/items')
    expect(response.data).toEqual(mockData)
  })
})
