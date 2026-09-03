import { useState } from 'react'
import { api, downloadFile } from '../api/client'
import { useFetch } from '../hooks/useFetch'

const emptyForm = { name: '', description: '' }

export default function CategoriesPage() {
  const { data: categories, loading, error, reload } = useFetch('/categories')
  const [form, setForm] = useState(emptyForm)
  const [editingId, setEditingId] = useState(null)
  const [formError, setFormError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [busyId, setBusyId] = useState(null)
  const [exporting, setExporting] = useState(false)

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  function startEdit(category) {
    setEditingId(category.id)
    setForm({ name: category.name, description: category.description ?? '' })
    setFormError('')
  }

  function cancelEdit() {
    setEditingId(null)
    setForm(emptyForm)
    setFormError('')
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setFormError('')
    setSubmitting(true)
    try {
      const payload = { name: form.name, description: form.description || null }
      if (editingId) {
        await api.put(`/categories/${editingId}`, payload)
      } else {
        await api.post('/categories', payload)
      }
      setForm(emptyForm)
      setEditingId(null)
      reload()
    } catch (err) {
      setFormError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete(category) {
    if (!window.confirm(`¿Eliminar la categoría "${category.name}"?`)) return
    setBusyId(category.id)
    try {
      await api.delete(`/categories/${category.id}`)
      reload()
    } catch (err) {
      window.alert(err.message)
    } finally {
      setBusyId(null)
    }
  }

  async function handleExportPdf() {
    setExporting(true)
    try {
      await downloadFile('/categories/export/pdf', 'categorias.pdf')
    } catch (err) {
      window.alert(err.message)
    } finally {
      setExporting(false)
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Categorías</h1>
        <button className="btn btn-ghost" onClick={handleExportPdf} disabled={exporting}>
          {exporting ? 'Generando PDF...' : '📄 Exportar PDF'}
        </button>
      </div>

      <form className="card form-grid" onSubmit={handleSubmit}>
        <label>
          Nombre
          <input value={form.name} onChange={(e) => update('name', e.target.value)} required />
        </label>
        <label>
          Descripción
          <input value={form.description} onChange={(e) => update('description', e.target.value)} />
        </label>
        {formError && <div className="alert alert-error span-2">{formError}</div>}
        <div className="span-2">
          <button className="btn btn-primary" type="submit" disabled={submitting}>
            {submitting ? 'Guardando...' : editingId ? 'Guardar cambios' : 'Agregar categoría'}
          </button>
          {editingId && (
            <button type="button" className="btn btn-ghost" onClick={cancelEdit}>
              Cancelar edición
            </button>
          )}
        </div>
      </form>

      <div className="card">
        {loading && <p className="muted">Cargando...</p>}
        {error && <div className="alert alert-error">{error}</div>}
        {categories && (
          <table className="table">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Descripción</th>
                <th>Estado</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {categories.map((c) => (
                <tr key={c.id}>
                  <td>{c.name}</td>
                  <td>{c.description ?? '—'}</td>
                  <td>
                    <span className={'badge ' + (c.active ? 'badge-success' : 'badge-muted')}>
                      {c.active ? 'Activa' : 'Inactiva'}
                    </span>
                  </td>
                  <td>
                    <button className="btn btn-ghost" onClick={() => startEdit(c)}>
                      Editar
                    </button>
                    <button
                      className="btn btn-danger"
                      disabled={busyId === c.id}
                      onClick={() => handleDelete(c)}
                    >
                      Eliminar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
