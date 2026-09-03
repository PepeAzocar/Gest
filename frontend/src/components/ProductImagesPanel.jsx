import { useRef, useState } from 'react'
import { api } from '../api/client'

export default function ProductImagesPanel({ product, onChange }) {
  const fileInputRef = useRef(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [busyImageId, setBusyImageId] = useState(null)

  const images = product.images ?? []

  async function handleUpload(e) {
    const files = Array.from(e.target.files || [])
    if (files.length === 0) return
    setError('')
    setUploading(true)
    try {
      const formData = new FormData()
      for (const file of files) formData.append('files', file)
      await api.upload(`/products/${product.id}/images`, formData)
      onChange()
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  async function handleDelete(imageId) {
    if (!window.confirm('¿Eliminar esta foto?')) return
    setError('')
    setBusyImageId(imageId)
    try {
      await api.delete(`/products/${product.id}/images/${imageId}`)
      onChange()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusyImageId(null)
    }
  }

  async function handleSetPrimary(imageId) {
    setError('')
    setBusyImageId(imageId)
    try {
      await api.put(`/products/${product.id}/images/${imageId}/primary`)
      onChange()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusyImageId(null)
    }
  }

  return (
    <div className="product-images">
      <div className="product-images-grid">
        {images.map((img) => (
          <div key={img.id} className="product-image-item">
            <img src={img.url} alt={product.name} />
            {img.is_primary && <span className="badge badge-success product-image-badge">Portada</span>}
            <div className="product-image-actions">
              {!img.is_primary && (
                <button
                  type="button"
                  className="btn btn-ghost"
                  disabled={busyImageId === img.id}
                  onClick={() => handleSetPrimary(img.id)}
                >
                  Hacer portada
                </button>
              )}
              <button
                type="button"
                className="btn btn-danger"
                disabled={busyImageId === img.id}
                onClick={() => handleDelete(img.id)}
              >
                Eliminar
              </button>
            </div>
          </div>
        ))}
        {images.length === 0 && <p className="muted">Sin fotos todavía.</p>}
      </div>

      <label className="btn btn-ghost">
        {uploading ? 'Subiendo...' : '+ Agregar fotos'}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/png,image/jpeg,image/webp,image/gif"
          multiple
          hidden
          disabled={uploading}
          onChange={handleUpload}
        />
      </label>

      {error && <div className="alert alert-error">{error}</div>}
    </div>
  )
}
