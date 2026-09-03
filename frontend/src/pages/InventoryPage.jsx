import { useState } from 'react'
import { api } from '../api/client'
import { useFetch } from '../hooks/useFetch'

const ADJUSTMENT_TYPES = [
  { value: 'INITIAL_STOCK', label: 'Carga inicial' },
  { value: 'PRODUCTION', label: 'Fabricación' },
  { value: 'RETURN', label: 'Devolución' },
  { value: 'ADJUSTMENT_IN', label: 'Ajuste (entrada)' },
  { value: 'ADJUSTMENT_OUT', label: 'Ajuste (salida)' },
  { value: 'DAMAGE', label: 'Daño' },
  { value: 'WASTE', label: 'Merma' },
]

const TABS = [
  { key: 'stock', label: 'Stock actual' },
  { key: 'adjustment', label: 'Ajuste manual' },
  { key: 'transfer', label: 'Transferencia' },
  { key: 'movements', label: 'Historial' },
]

export default function InventoryPage() {
  const [tab, setTab] = useState('stock')
  const { data: products } = useFetch('/products')
  const { data: warehouses } = useFetch('/warehouses')
  const {
    data: inventory,
    loading: invLoading,
    error: invError,
    reload: reloadInventory,
  } = useFetch('/inventory')
  const {
    data: movements,
    loading: movLoading,
    error: movError,
    reload: reloadMovements,
  } = useFetch('/inventory/movements')

  function reloadAll() {
    reloadInventory()
    reloadMovements()
  }

  return (
    <div>
      <h1>Inventario</h1>

      <div className="tabs">
        {TABS.map((t) => (
          <button
            key={t.key}
            className={'tab' + (tab === t.key ? ' active' : '')}
            onClick={() => setTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'stock' && (
        <div className="card">
          {invLoading && <p className="muted">Cargando...</p>}
          {invError && <div className="alert alert-error">{invError}</div>}
          {inventory && (
            <table className="table">
              <thead>
                <tr>
                  <th>Producto</th>
                  <th>Bodega</th>
                  <th>Físico</th>
                  <th>Reservado</th>
                  <th>Disponible</th>
                  <th>Mínimo</th>
                </tr>
              </thead>
              <tbody>
                {inventory.map((i) => {
                  const low = Number(i.quantity_available) <= Number(i.minimum_stock)
                  return (
                    <tr key={i.id}>
                      <td>
                        {i.product?.sku} — {i.product?.name}
                      </td>
                      <td>{i.warehouse?.name}</td>
                      <td>{i.quantity_on_hand}</td>
                      <td>{i.quantity_reserved}</td>
                      <td className={low ? 'text-danger' : ''}>{i.quantity_available}</td>
                      <td>{i.minimum_stock}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          )}
        </div>
      )}

      {tab === 'adjustment' && (
        <AdjustmentForm products={products} warehouses={warehouses} onDone={reloadAll} />
      )}

      {tab === 'transfer' && (
        <TransferForm products={products} warehouses={warehouses} onDone={reloadAll} />
      )}

      {tab === 'movements' && (
        <div className="card">
          {movLoading && <p className="muted">Cargando...</p>}
          {movError && <div className="alert alert-error">{movError}</div>}
          {movements && (
            <table className="table">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Tipo</th>
                  <th>Cantidad</th>
                  <th>Antes</th>
                  <th>Después</th>
                  <th>Motivo</th>
                </tr>
              </thead>
              <tbody>
                {movements.map((m) => (
                  <tr key={m.id}>
                    <td>{new Date(m.movement_date).toLocaleString('es-CL')}</td>
                    <td>
                      <span className="badge badge-muted">{m.movement_type}</span>
                    </td>
                    <td>{m.quantity}</td>
                    <td>{m.stock_before}</td>
                    <td>{m.stock_after}</td>
                    <td>{m.reason ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  )
}

function AdjustmentForm({ products, warehouses, onDone }) {
  const [productId, setProductId] = useState('')
  const [warehouseId, setWarehouseId] = useState('')
  const [movementType, setMovementType] = useState('INITIAL_STOCK')
  const [quantity, setQuantity] = useState('')
  const [reason, setReason] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setSubmitting(true)
    try {
      await api.post('/inventory/adjustments', {
        product_id: productId,
        warehouse_id: warehouseId,
        movement_type: movementType,
        quantity: Number(quantity),
        reason,
      })
      setQuantity('')
      setReason('')
      setSuccess('Movimiento registrado correctamente.')
      onDone()
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form className="card form-grid" onSubmit={handleSubmit}>
      <label>
        Producto
        <select value={productId} onChange={(e) => setProductId(e.target.value)} required>
          <option value="">Selecciona un producto</option>
          {products?.map((p) => (
            <option key={p.id} value={p.id}>
              {p.sku} — {p.name}
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
        Tipo de movimiento
        <select value={movementType} onChange={(e) => setMovementType(e.target.value)}>
          {ADJUSTMENT_TYPES.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </select>
      </label>
      <label>
        Cantidad
        <input type="number" step="0.001" min="0" value={quantity} onChange={(e) => setQuantity(e.target.value)} required />
      </label>
      <label className="span-2">
        Motivo
        <input value={reason} onChange={(e) => setReason(e.target.value)} required />
      </label>

      {error && <div className="alert alert-error span-2">{error}</div>}
      {success && <div className="alert alert-success span-2">{success}</div>}

      <div className="span-2">
        <button className="btn btn-primary" type="submit" disabled={submitting}>
          {submitting ? 'Guardando...' : 'Registrar movimiento'}
        </button>
      </div>
    </form>
  )
}

function TransferForm({ products, warehouses, onDone }) {
  const [productId, setProductId] = useState('')
  const [sourceId, setSourceId] = useState('')
  const [destinationId, setDestinationId] = useState('')
  const [quantity, setQuantity] = useState('')
  const [reason, setReason] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setSubmitting(true)
    try {
      await api.post('/inventory/transfers', {
        product_id: productId,
        source_warehouse_id: sourceId,
        destination_warehouse_id: destinationId,
        quantity: Number(quantity),
        reason,
      })
      setQuantity('')
      setReason('')
      setSuccess('Transferencia realizada correctamente.')
      onDone()
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form className="card form-grid" onSubmit={handleSubmit}>
      <label>
        Producto
        <select value={productId} onChange={(e) => setProductId(e.target.value)} required>
          <option value="">Selecciona un producto</option>
          {products?.map((p) => (
            <option key={p.id} value={p.id}>
              {p.sku} — {p.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        Cantidad
        <input type="number" step="0.001" min="0" value={quantity} onChange={(e) => setQuantity(e.target.value)} required />
      </label>
      <label>
        Bodega origen
        <select value={sourceId} onChange={(e) => setSourceId(e.target.value)} required>
          <option value="">Selecciona bodega origen</option>
          {warehouses?.map((w) => (
            <option key={w.id} value={w.id}>
              {w.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        Bodega destino
        <select value={destinationId} onChange={(e) => setDestinationId(e.target.value)} required>
          <option value="">Selecciona bodega destino</option>
          {warehouses?.map((w) => (
            <option key={w.id} value={w.id}>
              {w.name}
            </option>
          ))}
        </select>
      </label>
      <label className="span-2">
        Motivo
        <input value={reason} onChange={(e) => setReason(e.target.value)} required />
      </label>

      {error && <div className="alert alert-error span-2">{error}</div>}
      {success && <div className="alert alert-success span-2">{success}</div>}

      <div className="span-2">
        <button className="btn btn-primary" type="submit" disabled={submitting}>
          {submitting ? 'Transfiriendo...' : 'Transferir'}
        </button>
      </div>
    </form>
  )
}
