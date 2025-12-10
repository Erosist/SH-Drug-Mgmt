/**
 * 用药提醒通知服务
 * 使用 Web Notification API 实现浏览器弹窗通知
 */

import { homeApi } from '@/api/home'
import router from '@/router'
import { getToken } from '@/utils/authSession'
import { ElNotification } from 'element-plus'

class ReminderNotificationService {
  constructor() {
    this.checkInterval = null
    this.notifiedSet = new Set() // 记录已通知的提醒，避免重复
    this.todayReminders = []
    this.isRunning = false
  }

  /**
   * 请求通知权限
   */
  async requestPermission() {
    // Element Plus 弹窗不需要浏览器权限
    return true
  }

  /**
   * 检查通知权限状态
   */
  checkPermission() {
    if (!('Notification' in window)) {
      return 'unsupported'
    }
    return Notification.permission
  }

  /**
   * 发送通知
   */
  sendNotification(title, options = {}) {
    // 使用 Element Plus 弹窗替代浏览器通知
    ElNotification({
      title: title,
      message: options.body || '',
      type: 'info',
      duration: 0, // 不自动关闭
      onClick: () => {
        router.push({ name: 'medication-reminders' })
      }
    })

    console.log(`[Reminder] Notification sent: ${title}`)
    return true // 返回 true 表示成功发送
  }

  /**
   * 加载今日提醒
   */
  async loadTodayReminders() {
    // 检查是否已登录
    const token = getToken()
    if (!token) {
      console.log('[Reminder] User not logged in, skipping load')
      return
    }
    
    try {
      const response = await homeApi.getTodayReminders()
      if (response.data?.success) {
        this.todayReminders = response.data.items || []
        console.log(`[Reminder] Loaded ${this.todayReminders.length} reminders`)
      }
    } catch (error) {
      console.error('加载今日提醒失败:', error)
    }
  }

  /**
   * 检查是否到达提醒时间
   */
  checkReminders() {
    const now = new Date()
    const currentTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
    
    // 调试日志
    console.log(`[Reminder] Checking time: ${currentTime}, Reminders count: ${this.todayReminders.length}`)

    for (const reminder of this.todayReminders) {
      const key = `${reminder.id}-${reminder.remind_time}-${now.toDateString()}`
      
      // 检查是否已通知
      if (this.notifiedSet.has(key)) {
        continue
      }

      // 检查时间是否匹配（精确到分钟）
      if (reminder.remind_time === currentTime) {
        console.log(`[Reminder] Sending notification for:`, reminder)
        this.sendNotification('用药提醒', {
          body: `${reminder.drug_name} - ${reminder.dosage}${reminder.notes ? '\n' + reminder.notes : ''}`,
          tag: `reminder-${reminder.id}-${reminder.remind_time}`
        })
        this.notifiedSet.add(key)
      }
    }
  }

  /**
   * 启动通知服务
   */
  async start() {
    if (this.isRunning) {
      return
    }

    // 请求权限
    const hasPermission = await this.requestPermission()
    if (!hasPermission) {
      console.log('[Reminder] User did not grant notification permission')
      // 即使没有权限也启动服务，以便后续用户授予权限时能工作
      // this.isRunning = true // 不设置为运行状态，避免定时任务
      return
    }

    this.isRunning = true

    // 立即加载一次提醒
    await this.loadTodayReminders()

    // 每分钟检查一次
    this.checkInterval = setInterval(() => {
      this.checkReminders()
    }, 60 * 1000)

    // 每5分钟重新加载提醒列表（防止用户新增提醒后不生效）
    this.refreshInterval = setInterval(() => {
      this.loadTodayReminders()
    }, 5 * 60 * 1000)

    // 监听 storage 变化（用户登录/登出时刷新）
    this.storageHandler = () => {
      // 延迟加载以确保 currentUser 已更新
      setTimeout(() => {
        this.loadTodayReminders()
      }, 1000)
    }
    window.addEventListener('storage', this.storageHandler)

    // 立即检查一次
    this.checkReminders()

    console.log('[Reminder] Notification service started successfully')
  }

  /**
   * 停止通知服务
   */
  stop() {
    if (this.checkInterval) {
      clearInterval(this.checkInterval)
      this.checkInterval = null
    }
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval)
      this.refreshInterval = null
    }
    if (this.storageHandler) {
      window.removeEventListener('storage', this.storageHandler)
      this.storageHandler = null
    }
    this.isRunning = false
    console.log('用药提醒通知服务已停止')
  }

  /**
   * 清除今日已通知记录（用于测试）
   */
  clearNotified() {
    this.notifiedSet.clear()
  }

  /**
   * 手动触发一次测试通知
   */
  testNotification() {
    return this.sendNotification('用药提醒测试', {
      body: '这是一条测试通知\n点击可跳转到提醒管理页面',
      tag: 'test-notification'
    })
  }
}

// 导出单例
export const reminderNotificationService = new ReminderNotificationService()

export default reminderNotificationService
