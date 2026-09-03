import { Fragment, useState } from 'react'
import { api } from '../api/client'
import { useFetch } from '../hooks/useFetch'

const CHANNELS = ['STORE', 'WEBSITE', 'MERCADOLIBRE', 'INSTAGRAM', 'WHATSAPP', 'FAIR', 'DIRECT']

const STATUS_LABELS = {
  DRAFT: 'Borrador',
  PENDING_PAYMENT: 'Pendiente de pago',
  PAID: 'Pagada',
  CANCELLED: 'Cancelada',
  REFUNDED: 'Reembolsada',
}

const money = (n) => Number(n).toLocaleString('es-CL', { style: 'currency', currency: 'CLP' })

function emptyItem() {
  return { product_id: '', quantity: 1, unit_price: '', discount_amount: 0 }
}

export default function SalesPage() {
  const { data: sales, loading, error, reload } = useFetch('/sales')
  const { data: products } = useFetch('/products')
  const { data: warehouses } = useFetch('/warehouses')
  const { data: customers } = useFetch('/customers')

  const [showForm, setShowForm] = useState(false)
  const [customerId, setCustomerId] = useState('')
  const [warehouseId, setWarehouseId] = useState('')
  const [salesChannel, setSalesChannel] = useState('STORE')
  const [paymentMethod, setPaymentMethod] = useState('')
  const [paymentStatus, setPaymentStatus] = useState('PAID')
  const [items, setItems] = useState([emptyItem()])
  const [formError, setFormError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [expanded, setExpanded] = useState(null)
  const [cancelling, setCancelling] = useState(null)

  function updateItem(index, field, value) {
    setItems((prev) => prev.map((it, i) => (i === index ? { ...it, [field]: value } : it)))
  }

  function addItem() {
    setItems((prev) => [...prev, emptyItem()])
  }

  function removeItem(index) {
    setItems((prev) => prev.filter((_, i) => i !== index))
  }

  function resetForm() {
    setCustomerId('')
    setWarehouseId('')
    setSalesChannel('STORE')
    setPaymentMethod('')
    setPaymentStatus('PAID')
    setItems([emptyItem()])
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setFormError('')
    setSubmitting(true)
    try {
      const payload = {
        customer_id: customerId || null,
        warehouse_id: warehouseId,
        sales_channel: salesChannel,
        payment_method: paymentMethod || null,
        payment_status: paymentStatus,
        items: items.map((it) => ({
          product_id: it.product_id,
          quantity: Number(it.quantity),
          unit_price: Number(it.unit_price),
          discount_amount: Number(it.discount_amount || 0),
        })),
      }
      await api.post('/sales', payload)
      resetForm()
      setShowForm(false)
      reload()
    } catch (err) {
      setFormError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  async function handleCancel(saleId) {
    setCancelling(saleId)
    try {
      await api.post(`/sales/${saleId}/cancel`)
      reload()
    } catch (err) {
      window.alert(err.message)
    } finally {
      setCancelling(null)
    }
  }

  const total = items.reduce(
    (sum, it) => sum + (Number(it.quantity) || 0) * (Number(it.unit_price) || 0) - (Number(it.discount_amount) || 0),
    0,
  )

  return (
    <div>
      <div className="page-header">
        <h1>Ventas</h1>
        <button className="btn btn-primary" onClick={() => setShowForm((s) => !s)}>
          {showForm ? 'Cancelar' : '+ Nueva venta'}
        </button>
      </div>

      {showForm && (
        <form className="card" onSubmit={handleSubmit}>
          <div className="form-grid">
            <label>
              Cliente (opcional)
              <select value={customerId} onChange={(e) => setCustomerId(e.target.value)}>
                <option value="">Sin cliente registrado</option>
                {customers?.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.first_name} {c.last_name ?? ''}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Bodega
              <select value={warehouseId} onChange={(e) => setWarehouseId(e.target.value)} required>
                <option value="">Selecciona una bodega</option>
                {warehouses?.map((w) => (
                  <option key={w.id} value={w.id}>
                    {w.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Canal
              <select value={salesChannel} onChange={(e) => setSalesChannel(e.target.value)}>
                {CHANNELS.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Método de pago
              <input value={paymentMethod} onChange={(e) => setPaymentMethod(e.target.value)} placeholder="efectivo, transferencia..." />
            </label>
            <label>
              Estado del pago
              <select value={paymentStatus} onChange={(e) => setPaymentStatus(e.target.value)}>
                <option value="PAID">Pagado</option>
                <option value="PENDING">Pendiente</option>
              </select>
            </label>
          </div>

          <h3>Productos</h3>
          <table className="table">
            <thead>
              <tr>
                <th>Producto</th>
                <th>Cantidad</th>
                <th>Precio unitario</th>
                <th>Descuento</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {items.map((item, index) => (
                <tr key={index}>
                  <td>
                    <select
                      value={item.product_id}
                      onChange={(e) => updateItem(index, 'product_id', e.target.value)}
                      required
                    >
                      <option value="">Selecciona un producto</option>
                      {products?.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.sku} — {p.name}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td>
                    <input
                      type="number"
                      step="0.001"
                      min="0.001"
                      value={item.quantity}
                      onChange={(e) => updateItem(index, 'quantity', e.target.value)}
                      required
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      value={item.unit_price}
                      onChange={(e) => updateItem(index, 'unit_price', e.target.value)}
                      required
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      value={item.discount_amount}
                      onChange={(e) => updateItem(index, 'discount_amount', e.target.value)}
                    />
                  </td>
                  <td>
                    {items.length > 1 && (
                      <button type="button" className="btn btn-ghost" onClick={() => removeItem(index)}>
                        Quitar
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <button type="button" className="btn btn-ghost" onClick={addItem}>
            + Agregar producto
          </button>

          <div className="sale-total">Total: {money(total)}</div>

          {formError && <div className="alert alert-error">{formError}</div>}

          <button className="btn btn-primary" type="submit" disabled={submitting}>
            {submitting ? 'Registrando...' : 'Registrar venta'}
          </button>
        </form>
      )}

      <div className="card">
        {loading && <p className="muted">Cargando...</p>}
        {error && <div className="alert alert-error">{error}</div>}
        {sales && (
          <table className="table">
            <thead>
              <tr>
                <th></th>
                <th>N° Venta</th>
                <th>Fecha</th>
                <th>Cliente</th>
                <th>Canal</th>
                <th>Total</th>
                <th>Estado</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {sales.map((s) => (
                <Fragment key={s.id}>
                  <tr>
                    <td>
                      <button className="btn btn-ghost" onClick={() => setExpanded(expanded === s.id ? null : s.id)}>
                        {expanded === s.id ? '▾' : '▸'}
                      </button>
                    </td>
                    <td>{s.sale_number}</td>
                    <td>{new Date(s.sale_date).toLocaleDateString('es-CL')}</td>
                    <td>{s.customer ? `${s.customer.first_name} ${s.customer.last_name ?? ''}` : '—'}</td>
                    <td>{s.sales_channel}</td>
                    <td>{money(s.total_amount)}</td>
                    <td>
                      <span className={'badge ' + (s.status === 'CANCELLED' || s.status === 'REFUNDED' ? 'badge-muted' : 'badge-success')}>
                        {STATUS_LABELS[s.status] ?? s.status}
                      </span>
                    </td>
                    <td>
                      {s.status !== 'CANCELLED' && s.status !== 'REFUNDED' && (
                        <button
                          className="btn btn-danger"
                          disabled={cancelling === s.id}
                          onClick={() => handleCancel(s.id)}
                        >
                          {cancelling === s.id ? 'Cancelando...' : 'Cancelar'}
                        </button>
                      )}
                    </td>
                  </tr>
                  {expanded === s.id && (
                    <tr>
                      <td colSpan={8}>
                        <table className="table table-nested">
                          <thead>
                            <tr>
                              <th>Producto</th>
                              <th>Cantidad</th>
                              <th>Precio unitario</th>
                              <th>Descuento</th>
                              <th>Subtotal</th>
                            </tr>
                          </thead>
                          <tbody>
                            {s.items.map((it) => (
                              <tr key={it.id}>
                                <td>
                                  {it.product?.sku} — {it.product?.name}
                                </td>
                                <td>{it.quantity}</td>
                                <td>{money(it.unit_price)}</td>
                                <td>{money(it.discount_amount)}</td>
                                <td>{money(it.subtotal)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
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
