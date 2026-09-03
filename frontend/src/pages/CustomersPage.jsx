import { useState } from 'react'
import { api, downloadFile } from '../api/client'
import { useFetch } from '../hooks/useFetch'

const emptyForm = {
  customer_type: 'PERSON',
  first_name: '',
  last_name: '',
  rut: '',
  email: '',
  phone: '',
}

export default function CustomersPage() {
  const { data: customers, loading, error, reload } = useFetch('/customers')
  const [form, setForm] = useState(emptyForm)
  const [editingId, setEditingId] = useState(null)
  const [formError, setFormError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [busyId, setBusyId] = useState(null)
  const [exporting, setExporting] = useState(false)

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  function startEdit(customer) {
    setEditingId(customer.id)
    setForm({
      customer_type: customer.customer_type,
      first_name: customer.first_name,
      last_name: customer.last_name ?? '',
      rut: customer.rut ?? '',
      email: customer.email ?? '',
      phone: customer.phone ?? '',
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
      const payload = { ...form }
      for (const key of ['last_name', 'rut', 'email', 'phone']) {
        payload[key] = payload[key] || null
      }
      if (editingId) {
        await api.put(`/customers/${editingId}`, payload)
      } else {
        await api.post('/customers', payload)
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

  async function handleDelete(customer) {
    if (!window.confirm(`¿Eliminar al cliente "${customer.first_name} ${customer.last_name ?? ''}"?`)) return
    setBusyId(customer.id)
    try {
      await api.delete(`/customers/${customer.id}`)
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
      await downloadFile('/customers/export/pdf', 'clientes.pdf')
    } catch (err) {
      window.alert(err.message)
    } finally {
      setExporting(false)
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Clientes</h1>
        <button className="btn btn-ghost" onClick={handleExportPdf} disabled={exporting}>
          {exporting ? 'Generando PDF...' : '📄 Exportar PDF'}
        </button>
      </div>

      <form className="card form-grid" onSubmit={handleSubmit}>
        <label>
          Tipo
          <select value={form.customer_type} onChange={(e) => update('customer_type', e.target.value)}>
            <option value="PERSON">Persona</option>
            <option value="COMPANY">Empresa</option>
          </select>
        </label>
        <label>
          Nombre
          <input value={form.first_name} onChange={(e) => update('first_name', e.target.value)} required />
        </label>
        <label>
          Apellido
          <input value={form.last_name} onChange={(e) => update('last_name', e.target.value)} />
        </label>
        <label>
          RUT
          <input value={form.rut} onChange={(e) => update('rut', e.target.value)} />
        </label>
        <label>
          Email
          <input type="email" value={form.email} onChange={(e) => update('email', e.target.value)} />
        </label>
        <label>
          Teléfono
          <input value={form.phone} onChange={(e) => update('phone', e.target.value)} />
        </label>

        {formError && <div className="alert alert-error span-2">{formError}</div>}

        <div className="span-2">
          <button className="btn btn-primary" type="submit" disabled={submitting}>
            {submitting ? 'Guardando...' : editingId ? 'Guardar cambios' : 'Agregar cliente'}
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
        {customers && (
          <table className="table">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Tipo</th>
                <th>RUT</th>
                <th>Email</th>
                <th>Teléfono</th>
                <th>Estado</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {customers.map((c) => (
                <tr key={c.id}>
                  <td>
                    {c.first_name} {c.last_name ?? ''}
                  </td>
                  <td>{c.customer_type === 'PERSON' ? 'Persona' : 'Empresa'}</td>
                  <td>{c.rut ?? '—'}</td>
                  <td>{c.email ?? '—'}</td>
                  <td>{c.phone ?? '—'}</td>
                  <td>
                    <span className={'badge ' + (c.active ? 'badge-success' : 'badge-muted')}>
                      {c.active ? 'Activo' : 'Inactivo'}
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
