const TOKEN_KEY = 'gest_token'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else localStorage.removeItem(TOKEN_KEY)
}

class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

async function request(path, { method = 'GET', body, form, formData } = {}) {
  const headers = {}
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`

  let payload
  if (formData) {
    // Content-Type is set by the browser (with the multipart boundary)
    payload = formData
  } else if (form) {
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    payload = new URLSearchParams(form).toString()
  } else if (body !== undefined) {
    headers['Content-Type'] = 'application/json'
    payload = JSON.stringify(body)
  }

  const res = await fetch(`/api${path}`, { method, headers, body: payload })

  if (res.status === 204) return null

  const isJson = res.headers.get('content-type')?.includes('application/json')
  const data = isJson ? await res.json() : await res.text()

  if (!res.ok) {
    const message = (isJson && (data.detail || JSON.stringify(data))) || res.statusText
    if (res.status === 401) setToken(null)
    throw new ApiError(typeof message === 'string' ? message : JSON.stringify(message), res.status)
  }

  return data
}

export const api = {
  get: (path) => request(path),
  post: (path, body) => request(path, { method: 'POST', body }),
  put: (path, body) => request(path, { method: 'PUT', body }),
  delete: (path) => request(path, { method: 'DELETE' }),
  upload: (path, formData) => request(path, { method: 'POST', formData }),
  login: (username, password) => request('/auth/login', { method: 'POST', form: { username, password } }),
}

export async function downloadFile(path, filename) {
  const headers = {}
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`

  const res = await fetch(`/api${path}`, { headers })
  if (!res.ok) {
    const isJson = res.headers.get('content-type')?.includes('application/json')
    const data = isJson ? await res.json() : await res.text()
    const message = (isJson && (data.detail || JSON.stringify(data))) || res.statusText
    throw new ApiError(typeof message === 'string' ? message : JSON.stringify(message), res.status)
  }

  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

export { ApiError }
