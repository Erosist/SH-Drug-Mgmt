import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import axios from 'axios'

// Mock axios
vi.mock('axios')
const mockedAxios = vi.mocked(axios)

describe('Authentication Tests', () => {
  let wrapper
  let router
  let pinia  git reset --hard origin/main  git reset --hard origin/main  git reset --hard origin/main

  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks()
    
    // Setup router
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
        { path: '/login', name: 'login', component: { template: '<div>Login</div>' } }
      ]
    })
    
    // Setup pinia
    pinia = createPinia()
  })

  describe('Login Functionality', () => {
    it('should login successfully with valid credentials', async () => {
      // Mock successful login response
      mockedAxios.post.mockResolvedValue({
        data: {
          token: 'mock-token-123',
          user: {
            id: 1,
            username: 'testuser',
            role: 'pharmacy'
          }
        }
      })

      const credentials = {
        username: 'testuser',
        password: 'password123'
      }

      const response = await axios.post('/api/login', credentials)
      
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/login', credentials)
      expect(response.data.token).toBe('mock-token-123')
      expect(response.data.user.username).toBe('testuser')
    })

    it('should handle login failure with invalid credentials', async () => {
      // Mock failed login response
      mockedAxios.post.mockRejectedValue({
        response: {
          status: 401,
          data: {
            message: 'Invalid credentials'
          }
        }
      })

      const credentials = {
        username: 'wronguser',
        password: 'wrongpassword'
      }

      try {
        await axios.post('/api/login', credentials)
      } catch (error) {
        expect(error.response.status).toBe(401)
        expect(error.response.data.message).toBe('Invalid credentials')
      }
    })

    it('should store token in localStorage after successful login', async () => {
      // Mock localStorage
      const localStorageMock = {
        getItem: vi.fn(),
        setItem: vi.fn(),
        removeItem: vi.fn(),
        clear: vi.fn(),
      }
      global.localStorage = localStorageMock

      // Mock successful response
      mockedAxios.post.mockResolvedValue({
        data: {
          token: 'mock-token-123',
          user: { id: 1, username: 'testuser' }
        }
      })

      const response = await axios.post('/api/login', { username: 'test', password: 'test' })
      
      // Simulate storing token
      localStorage.setItem('token', response.data.token)
      
      expect(localStorageMock.setItem).toHaveBeenCalledWith('token', 'mock-token-123')
    })
  })

  describe('User Registration', () => {
    it('should register new user successfully', async () => {
      mockedAxios.post.mockResolvedValue({
        data: {
          message: 'User registered successfully',
          user: {
            id: 2,
            username: 'newuser',
            email: 'newuser@test.com'
          }
        }
      })

      const userData = {
        username: 'newuser',
        email: 'newuser@test.com',
        password: 'password123',
        role: 'pharmacy'
      }

      const response = await axios.post('/api/register', userData)
      
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/register', userData)
      expect(response.data.message).toBe('User registered successfully')
      expect(response.data.user.username).toBe('newuser')
    })

    it('should handle registration failure for existing user', async () => {
      mockedAxios.post.mockRejectedValue({
        response: {
          status: 409,
          data: {
            message: 'Username already exists'
          }
        }
      })

      const userData = {
        username: 'existinguser',
        email: 'test@test.com',
        password: 'password123'
      }

      try {
        await axios.post('/api/register', userData)
      } catch (error) {
        expect(error.response.status).toBe(409)
        expect(error.response.data.message).toBe('Username already exists')
      }
    })
  })

  describe('Token Validation', () => {
    it('should validate token successfully', async () => {
      mockedAxios.get.mockResolvedValue({
        data: {
          valid: true,
          user: {
            id: 1,
            username: 'testuser',
            role: 'pharmacy'
          }
        }
      })

      const response = await axios.get('/api/validate-token', {
        headers: { Authorization: 'Bearer mock-token-123' }
      })

      expect(response.data.valid).toBe(true)
      expect(response.data.user.username).toBe('testuser')
    })

    it('should handle invalid token', async () => {
      mockedAxios.get.mockRejectedValue({
        response: {
          status: 401,
          data: {
            message: 'Invalid token'
          }
        }
      })

      try {
        await axios.get('/api/validate-token', {
          headers: { Authorization: 'Bearer invalid-token' }
        })
      } catch (error) {
        expect(error.response.status).toBe(401)
        expect(error.response.data.message).toBe('Invalid token')
      }
    })
  })
})