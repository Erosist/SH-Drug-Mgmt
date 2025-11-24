import { describe, it, expect } from 'vitest'

// 简单的工具函数用于测试
function formatCurrency(amount) {
  return `¥${amount.toFixed(2)}`
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

function validateEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

describe('工具函数测试', () => {
  describe('formatCurrency', () => {
    it('应该正确格式化货币', () => {
      expect(formatCurrency(100)).toBe('¥100.00')
      expect(formatCurrency(99.99)).toBe('¥99.99')
      expect(formatCurrency(0)).toBe('¥0.00')
    })
  })

  describe('formatDate', () => {
    it('应该正确格式化日期', () => {
      const result = formatDate('2023-12-25')
      expect(result).toMatch(/\d{4}\/\d{1,2}\/\d{1,2}/)
    })
  })

  describe('validateEmail', () => {
    it('应该验证有效的邮箱地址', () => {
      expect(validateEmail('test@example.com')).toBe(true)
      expect(validateEmail('user@domain.cn')).toBe(true)
    })

    it('应该拒绝无效的邮箱地址', () => {
      expect(validateEmail('invalid-email')).toBe(false)
      expect(validateEmail('test@')).toBe(false)
      expect(validateEmail('@example.com')).toBe(false)
    })
  })
})
