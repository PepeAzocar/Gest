import { useState } from 'react'
import { api, downloadFile } from '../api/client'
import { useFetch } from '../hooks/useFetch'

const emptyForm = { code: '', name: '', description: '' }

export default function WarehousesPage() {
  const { data: warehouses, loading, error, reload } = useFetch('/warehouses')
  const [form, setForm] = useState(emptyForm)
  const [editingId, setEditingId] = useState(null)
  const [formError, setFormError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [busyId, setBusyId] = useState(null)
  const [exporting, setExporting] = useState(false)

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  function startEdit(warehouse) {
    setEditingId(warehouse.id)
    setForm({
      code: warehouse.code,
      name: warehouse.name,
      description: warehouse.description ?? '',
    })
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
      if (editingId) {
        await api.put(`/warehouses/${editingId}`, {
          name: form.name,
          description: form.description || null,
        })
      } else {
        await api.post('/warehouses', {
          code: form.code,
          name: form.name,
          description: form.description || null,
        })
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

  async function handleDelete(warehouse) {
    if (!window.confirm(`¿Eliminar la bodega "${warehouse.name}"?`)) return
    setBusyId(warehouse.id)
    try {
      await api.delete(`/warehouses/${warehouse.id}`)
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
      await downloadFile('/warehouses/export/pdf', 'bodegas.pdf')
    } catch (err) {
      window.alert(err.message)
    } finally {
      setExporting(false)
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Bodegas</h1>
        <button className="btn btn-ghost" onClick={handleExportPdf} disabled={exporting}>
          {exporting ? 'Generando PDF...' : '📄 Exportar PDF'}
        </button>
      </div>

      <form className="card form-grid" onSubmit={handleSubmit}>
        <label>
          Código
          <input
            value={form.code}
            onChange={(e) => update('code', e.target.value.toUpperCase())}
            disabled={!!editingId}
            required
          />
        </label>
        <label>
          Nombre
          <input value={form.name} onChange={(e) => update('name', e.target.value)} required />
        </label>
        <label className="span-2">
          Descripción
          <input value={form.description} onChange={(e) => update('description', e.target.value)} />
        </label>
        {formError && <div className="alert alert-error span-2">{formError}</div>}
        <div className="span-2">
          <button className="btn btn-primary" type="submit" disabled={submitting}>
            {submitting ? 'Guardando...' : editingId ? 'Guardar cambios' : 'Agregar bodega'}
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
        {warehouses && (
          <table className="table">
            <thead>
              <tr>
                <th>Código</th>
                <th>Nombre</th>
                <th>Descripción</th>
                <th>Estado</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {warehouses.map((w) => (
                <tr key={w.id}>
                  <td>{w.code}</td>
                  <td>{w.name}</td>
                  <td>{w.description ?? '—'}</td>
                  <td>
                    <span className={'badge ' + (w.active ? 'badge-success' : 'badge-muted')}>
                      {w.active ? 'Activa' : 'Inactiva'}
                    </span>
                  </td>
                  <td>
                    <button className="btn btn-ghost" onClick={() => startEdit(w)}>
                      Editar
                    </button>
                    <button
                      className="btn btn-danger"
                      disabled={busyId === w.id}
                      onClick={() => handleDelete(w)}
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
