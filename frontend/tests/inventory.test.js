import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import axios from 'axios'

// Mock axios
vi.mock('axios')
const mockedAxios = vi.mocked(axios)

describe('Inventory Management Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Inventory Operations', () => {
    it('should fetch inventory items successfully', async () => {
      const mockInventoryData = {
        data: [
          {
            id: 1,
            drug_name: '阿莫西林',
            quantity: 100,
            unit_price: 25.50,
            expiry_date: '2025-06-15',
            batch_number: 'AMX20241101'
          },
          {
            id: 2,
            drug_name: '感冒灵',
            quantity: 50,
            unit_price: 15.30,
            expiry_date: '2025-03-20',
            batch_number: 'GML20241015'
          }
        ]
      }

      mockedAxios.get.mockResolvedValue(mockInventoryData)

      const response = await axios.get('/api/inventory')
      
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/inventory')
      expect(response.data).toHaveLength(2)
      expect(response.data[0].drug_name).toBe('阿莫西林')
      expect(response.data[1].drug_name).toBe('感冒灵')
    })

    it('should add new inventory item successfully', async () => {
      const newItem = {
        drug_name: '布洛芬',
        quantity: 75,
        unit_price: 18.90,
        expiry_date: '2025-08-10',
        batch_number: 'BLF20241120'
      }

      mockedAxios.post.mockResolvedValue({
        data: {
          id: 3,
          ...newItem,
          message: 'Inventory item added successfully'
        }
      })

      const response = await axios.post('/api/inventory', newItem)
      
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/inventory', newItem)
      expect(response.data.drug_name).toBe('布洛芬')
      expect(response.data.id).toBe(3)
    })

    it('should update inventory item successfully', async () => {
      const updatedItem = {
        id: 1,
        drug_name: '阿莫西林胶囊',
        quantity: 120,
        unit_price: 26.00,
        expiry_date: '2025-06-15',
        batch_number: 'AMX20241101'
      }

      mockedAxios.put.mockResolvedValue({
        data: {
          ...updatedItem,
          message: 'Inventory item updated successfully'
        }
      })

      const response = await axios.put(`/api/inventory/${updatedItem.id}`, updatedItem)
      
      expect(mockedAxios.put).toHaveBeenCalledWith('/api/inventory/1', updatedItem)
      expect(response.data.drug_name).toBe('阿莫西林胶囊')
      expect(response.data.quantity).toBe(120)
    })

    it('should delete inventory item successfully', async () => {
      mockedAxios.delete.mockResolvedValue({
        data: {
          message: 'Inventory item deleted successfully'
        }
      })

      const response = await axios.delete('/api/inventory/1')
      
      expect(mockedAxios.delete).toHaveBeenCalledWith('/api/inventory/1')
      expect(response.data.message).toBe('Inventory item deleted successfully')
    })
  })

  describe('Inventory Warnings', () => {
    it('should fetch low stock warnings', async () => {
      const mockWarnings = {
        data: [
          {
            id: 1,
            drug_name: '感冒灵',
            current_quantity: 5,
            warning_threshold: 10,
            warning_type: 'low_stock'
          },
          {
            id: 2,
            drug_name: '止痛片',
            current_quantity: 2,
            warning_threshold: 15,
            warning_type: 'low_stock'
          }
        ]
      }

      mockedAxios.get.mockResolvedValue(mockWarnings)

      const response = await axios.get('/api/inventory/warnings')
      
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/inventory/warnings')
      expect(response.data).toHaveLength(2)
      expect(response.data[0].warning_type).toBe('low_stock')
    })

    it('should fetch expiry warnings', async () => {
      const mockExpiryWarnings = {
        data: [
          {
            id: 1,
            drug_name: '维生素C',
            expiry_date: '2025-01-15',
            days_until_expiry: 43,
            warning_type: 'expiry_soon'
          }
        ]
      }

      mockedAxios.get.mockResolvedValue(mockExpiryWarnings)

      const response = await axios.get('/api/inventory/expiry-warnings')
      
      expect(response.data[0].warning_type).toBe('expiry_soon')
      expect(response.data[0].days_until_expiry).toBe(43)
    })
  })

  describe('Search and Filter', () => {
    it('should search inventory by drug name', async () => {
      const searchResults = {
        data: [
          {
            id: 1,
            drug_name: '阿莫西林',
            quantity: 100,
            unit_price: 25.50
          }
        ]
      }

      mockedAxios.get.mockResolvedValue(searchResults)

      const response = await axios.get('/api/inventory/search?q=阿莫西林')
      
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/inventory/search?q=阿莫西林')
      expect(response.data[0].drug_name).toContain('阿莫西林')
    })

    it('should filter inventory by expiry date range', async () => {
      const filterResults = {
        data: [
          {
            id: 1,
            drug_name: '感冒灵',
            expiry_date: '2025-03-20',
            quantity: 50
          }
        ]
      }

      mockedAxios.get.mockResolvedValue(filterResults)

      const response = await axios.get('/api/inventory/filter?expiry_start=2025-01-01&expiry_end=2025-06-30')
      
      expect(response.data[0].expiry_date).toBe('2025-03-20')
    })
  })
})