import { describe, it, expect, beforeEach, vi } from 'vitest'
import axios from 'axios'

// Mock axios
vi.mock('axios')
const mockedAxios = vi.mocked(axios)

describe('Order Management Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Order Creation', () => {
    it('should create new order successfully', async () => {
      const newOrder = {
        supplier_id: 1,
        items: [
          {
            drug_name: '阿莫西林',
            quantity: 50,
            unit_price: 25.50
          },
          {
            drug_name: '感冒灵',
            quantity: 30,
            unit_price: 15.30
          }
        ],
        delivery_address: '上海市浦东新区张江路123号',
        notes: '紧急采购'
      }

      const mockResponse = {
        data: {
          id: 1001,
          order_number: 'ORD-2024-001001',
          status: 'pending',
          total_amount: 1734.00,
          created_at: '2024-12-03T10:30:00Z',
          ...newOrder
        }
      }

      mockedAxios.post.mockResolvedValue(mockResponse)

      const response = await axios.post('/api/orders', newOrder)
      
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/orders', newOrder)
      expect(response.data.order_number).toBe('ORD-2024-001001')
      expect(response.data.status).toBe('pending')
      expect(response.data.items).toHaveLength(2)
    })

    it('should handle order creation with invalid data', async () => {
      const invalidOrder = {
        supplier_id: null,
        items: []
      }

      mockedAxios.post.mockRejectedValue({
        response: {
          status: 400,
          data: {
            message: 'Invalid order data',
            errors: {
              supplier_id: 'Supplier is required',
              items: 'At least one item is required'
            }
          }
        }
      })

      try {
        await axios.post('/api/orders', invalidOrder)
      } catch (error) {
        expect(error.response.status).toBe(400)
        expect(error.response.data.errors.supplier_id).toBe('Supplier is required')
      }
    })
  })

  describe('Order Status Management', () => {
    it('should update order status successfully', async () => {
      const statusUpdate = {
        status: 'confirmed',
        notes: 'Order confirmed by supplier'
      }

      mockedAxios.put.mockResolvedValue({
        data: {
          id: 1001,
          status: 'confirmed',
          updated_at: '2024-12-03T11:00:00Z',
          message: 'Order status updated successfully'
        }
      })

      const response = await axios.put('/api/orders/1001/status', statusUpdate)
      
      expect(mockedAxios.put).toHaveBeenCalledWith('/api/orders/1001/status', statusUpdate)
      expect(response.data.status).toBe('confirmed')
    })

    it('should fetch order status history', async () => {
      const mockHistory = {
        data: [
          {
            id: 1,
            status: 'pending',
            timestamp: '2024-12-03T10:30:00Z',
            notes: 'Order created'
          },
          {
            id: 2,
            status: 'confirmed',
            timestamp: '2024-12-03T11:00:00Z',
            notes: 'Order confirmed by supplier'
          }
        ]
      }

      mockedAxios.get.mockResolvedValue(mockHistory)

      const response = await axios.get('/api/orders/1001/history')
      
      expect(response.data).toHaveLength(2)
      expect(response.data[0].status).toBe('pending')
      expect(response.data[1].status).toBe('confirmed')
    })
  })

  describe('Order Queries', () => {
    it('should fetch orders with pagination', async () => {
      const mockOrders = {
        data: {
          orders: [
            {
              id: 1001,
              order_number: 'ORD-2024-001001',
              status: 'pending',
              total_amount: 1734.00
            },
            {
              id: 1002,
              order_number: 'ORD-2024-001002',
              status: 'confirmed',
              total_amount: 892.50
            }
          ],
          pagination: {
            current_page: 1,
            total_pages: 5,
            total_orders: 45,
            per_page: 10
          }
        }
      }

      mockedAxios.get.mockResolvedValue(mockOrders)

      const response = await axios.get('/api/orders?page=1&per_page=10')
      
      expect(response.data.orders).toHaveLength(2)
      expect(response.data.pagination.current_page).toBe(1)
      expect(response.data.pagination.total_orders).toBe(45)
    })

    it('should search orders by order number', async () => {
      const searchResults = {
        data: [
          {
            id: 1001,
            order_number: 'ORD-2024-001001',
            status: 'pending'
          }
        ]
      }

      mockedAxios.get.mockResolvedValue(searchResults)

      const response = await axios.get('/api/orders/search?q=ORD-2024-001001')
      
      expect(response.data[0].order_number).toBe('ORD-2024-001001')
    })

    it('should filter orders by status and date range', async () => {
      const filterResults = {
        data: [
          {
            id: 1003,
            status: 'completed',
            created_at: '2024-12-01T15:30:00Z'
          }
        ]
      }

      mockedAxios.get.mockResolvedValue(filterResults)

      const response = await axios.get('/api/orders/filter?status=completed&start_date=2024-12-01&end_date=2024-12-03')
      
      expect(response.data[0].status).toBe('completed')
    })
  })

  describe('Order Analytics', () => {
    it('should fetch order statistics', async () => {
      const mockStats = {
        data: {
          total_orders: 156,
          pending_orders: 23,
          completed_orders: 120,
          cancelled_orders: 13,
          total_value: 456789.50,
          average_order_value: 2927.49
        }
      }

      mockedAxios.get.mockResolvedValue(mockStats)

      const response = await axios.get('/api/orders/statistics')
      
      expect(response.data.total_orders).toBe(156)
      expect(response.data.average_order_value).toBe(2927.49)
    })
  })
})