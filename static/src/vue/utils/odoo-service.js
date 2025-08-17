class OdooService {
  constructor() {
    this.baseUrl = window.location.origin
    this.session = null
    this.init()
  }

  async init() {
    try {
      this.session = window.odoo?.session || null
      console.log('✓ Odoo Service инициализирован')
    } catch (error) {
      console.error('❌ Ошибка инициализации Odoo Service:', error)
    }
  }

  async rpc(url, params = {}) {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCSRFToken()
        },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'call',
          params: params,
          id: Date.now()
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      
      if (data.error) {
        throw new Error(data.error.message || 'RPC Error')
      }

      return data.result
    } catch (error) {
      console.error('RPC Error:', error)
      throw error
    }
  }

  getCSRFToken() {
    const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
                  this.session?.csrf_token ||
                  ''
    return token
  }

  async getData({ model = 'res.users', domain = [], fields = [], limit = 50, offset = 0 } = {}) {
    try {
      const result = await this.rpc('/vue/api/data', {
        model,
        domain,
        fields,
        limit,
        offset
      })
      return result
    } catch (error) {
      console.error('Ошибка получения данных:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }

  async getUserInfo() {
    try {
      const result = await this.rpc('/vue/api/user-info')
      return result
    } catch (error) {
      console.error('Ошибка получения информации о пользователе:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }
}

export const odooService = new OdooService()

export default OdooService