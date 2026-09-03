import { Fragment, useState } from 'react'
import { api, downloadFile } from '../api/client'
import ProductImagesPanel from '../components/ProductImagesPanel'
import { useFetch } from '../hooks/useFetch'

const emptyForm = {
  sku: '',
  name: '',
  description: '',
  category_id: '',
  length_cm: '',
  width_cm: '',
  height_cm: '',
  weight_kg: '',
  main_material: '',
  paint_type: '',
  finish_type: '',
  non_toxic_paint: false,
  handmade: false,
  requires_adult_supervision: false,
  recommended_age_min: '',
  recommended_age_max: '',
  production_time_hours: '',
  minimum_stock: 0,
  critical_stock: 0,
}

const NUMERIC_FIELDS = [
  'length_cm',
  'width_cm',
  'height_cm',
  'weight_kg',
  'recommended_age_min',
  'recommended_age_max',
  'production_time_hours',
]

function toPayload(form) {
  const payload = { ...form }
  for (const key of NUMERIC_FIELDS) {
    payload[key] = payload[key] === '' ? null : Number(payload[key])
  }
  payload.category_id = payload.category_id || null
  payload.minimum_stock = Number(payload.minimum_stock)
  payload.critical_stock = Number(payload.critical_stock)
  return payload
}

function toForm(product) {
  const form = { ...emptyForm }
  for (const key of Object.keys(emptyForm)) {
    if (key === 'category_id') {
      form[key] = product.category_id ?? ''
    } else if (NUMERIC_FIELDS.includes(key)) {
      form[key] = product[key] ?? ''
    } else if (key in product) {
      form[key] = product[key] ?? emptyForm[key]
    }
  }
  return form
}

export default function ProductsPage() {
  const { data: products, loading, error, reload } = useFetch('/products')
  const { data: categories } = useFetch('/categories')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [editingId, setEditingId] = useState(null)
  const [formError, setFormError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [expandedProduct, setExpandedProduct] = useState(null)
  const [busyId, setBusyId] = useState(null)
  const [exporting, setExporting] = useState(false)

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  function toggleNewForm() {
    if (showForm) {
      setShowForm(false)
      setEditingId(null)
      setForm(emptyForm)
    } else {
      setShowForm(true)
      setEditingId(null)
      setForm(emptyForm)
    }
  }

  function startEdit(product) {
    setEditingId(product.id)
    setForm(toForm(product))
    setFormError('')
    setShowForm(true)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setFormError('')
    setSubmitting(true)
    try {
      if (editingId) {
        await api.put(`/products/${editingId}`, toPayload(form))
      } else {
        await api.post('/products', toPayload(form))
      }
      setForm(emptyForm)
      setEditingId(null)
      setShowForm(false)
      reload()
    } catch (err) {
      setFormError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete(product) {
    if (!window.confirm(`¿Eliminar el producto "${product.name}"?`)) return
    setBusyId(product.id)
    try {
      await api.delete(`/products/${product.id}`)
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
      await downloadFile('/products/export/pdf', 'productos.pdf')
    } catch (err) {
      window.alert(err.message)
    } finally {
      setExporting(false)
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Productos</h1>
        <div className="page-header-actions">
          <button className="btn btn-ghost" onClick={handleExportPdf} disabled={exporting}>
            {exporting ? 'Generando PDF...' : '📄 Exportar PDF'}
          </button>
          <button className="btn btn-primary" onClick={toggleNewForm}>
            {showForm ? 'Cancelar' : '+ Nuevo producto'}
          </button>
        </div>
      </div>

      {showForm && (
        <form className="card form-grid" onSubmit={handleSubmit}>
          <label>
            SKU
            <input value={form.sku} onChange={(e) => update('sku', e.target.value)} required />
          </label>
          <label>
            Nombre
            <input value={form.name} onChange={(e) => update('name', e.target.value)} required />
          </label>
          <label className="span-2">
            Descripción
            <textarea value={form.description} onChange={(e) => update('description', e.target.value)} />
          </label>
          <label>
            Categoría
            <select value={form.category_id} onChange={(e) => update('category_id', e.target.value)}>
              <option value="">Sin categoría</option>
              {categories?.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Material principal
            <input value={form.main_material} onChange={(e) => update('main_material', e.target.value)} />
          </label>
          <label>
            Largo (cm)
            <input type="number" step="0.01" value={form.length_cm} onChange={(e) => update('length_cm', e.target.value)} />
          </label>
          <label>
            Ancho (cm)
            <input type="number" step="0.01" value={form.width_cm} onChange={(e) => update('width_cm', e.target.value)} />
          </label>
          <label>
            Alto (cm)
            <input type="number" step="0.01" value={form.height_cm} onChange={(e) => update('height_cm', e.target.value)} />
          </label>
          <label>
            Peso (kg)
            <input type="number" step="0.001" value={form.weight_kg} onChange={(e) => update('weight_kg', e.target.value)} />
          </label>
          <label>
            Tipo de pintura
            <input value={form.paint_type} onChange={(e) => update('paint_type', e.target.value)} />
          </label>
          <label>
            Terminación
            <input value={form.finish_type} onChange={(e) => update('finish_type', e.target.value)} />
          </label>
          <label>
            Edad mínima recomendada
            <input type="number" value={form.recommended_age_min} onChange={(e) => update('recommended_age_min', e.target.value)} />
          </label>
          <label>
            Edad máxima recomendada
            <input type="number" value={form.recommended_age_max} onChange={(e) => update('recommended_age_max', e.target.value)} />
          </label>
          <label>
            Horas de producción
            <input type="number" step="0.1" value={form.production_time_hours} onChange={(e) => update('production_time_hours', e.target.value)} />
          </label>
          <label>
            Stock mínimo
            <input type="number" value={form.minimum_stock} onChange={(e) => update('minimum_stock', e.target.value)} />
          </label>
          <label>
            Stock crítico
            <input type="number" value={form.critical_stock} onChange={(e) => update('critical_stock', e.target.value)} />
          </label>

          <label className="checkbox">
            <input type="checkbox" checked={form.handmade} onChange={(e) => update('handmade', e.target.checked)} />
            Hecho a mano
          </label>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={form.non_toxic_paint}
              onChange={(e) => update('non_toxic_paint', e.target.checked)}
            />
            Pintura no tóxica
          </label>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={form.requires_adult_supervision}
              onChange={(e) => update('requires_adult_supervision', e.target.checked)}
            />
            Requiere supervisión de un adulto
          </label>

          {formError && <div className="alert alert-error span-2">{formError}</div>}

          <div className="span-2">
            <button className="btn btn-primary" type="submit" disabled={submitting}>
              {submitting ? 'Guardando...' : editingId ? 'Guardar cambios' : 'Guardar producto'}
            </button>
          </div>
        </form>
      )}

      <div className="card">
        {loading && <p className="muted">Cargando...</p>}
        {error && <div className="alert alert-error">{error}</div>}
        {products && (
          <table className="table">
            <thead>
              <tr>
                <th></th>
                <th>SKU</th>
                <th>Nombre</th>
                <th>Categoría</th>
                <th>Material</th>
                <th>Stock mín. / crít.</th>
                <th>Estado</th>
                <th>Fotos</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {products.map((p) => (
                <Fragment key={p.id}>
                  <tr>
                    <td>
                      <button
                        className="btn btn-ghost"
                        onClick={() => setExpandedProduct(expandedProduct === p.id ? null : p.id)}
                      >
                        {expandedProduct === p.id ? '▾' : '▸'}
                      </button>
                    </td>
                    <td>{p.sku}</td>
                    <td>{p.name}</td>
                    <td>{p.category?.name ?? '—'}</td>
                    <td>{p.main_material ?? '—'}</td>
                    <td>
                      {p.minimum_stock} / {p.critical_stock}
                    </td>
                    <td>
                      <span className={'badge ' + (p.active ? 'badge-success' : 'badge-muted')}>
                        {p.active ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                    <td>{p.images?.length ?? 0}</td>
                    <td>
                      <button className="btn btn-ghost" onClick={() => startEdit(p)}>
                        Editar
                      </button>
                      <button
                        className="btn btn-danger"
                        disabled={busyId === p.id}
                        onClick={() => handleDelete(p)}
                      >
                        Eliminar
                      </button>
                    </td>
                  </tr>
                  {expandedProduct === p.id && (
                    <tr>
                      <td colSpan={9}>
                        <ProductImagesPanel product={p} onChange={reload} />
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
