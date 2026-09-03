import { useFetch } from '../hooks/useFetch'

const money = (n) => Number(n).toLocaleString('es-CL', { style: 'currency', currency: 'CLP' })

export default function DashboardPage() {
  const { data: products } = useFetch('/products')
  const { data: inventory } = useFetch('/inventory')
  const { data: lowStock } = useFetch('/inventory?low_stock_only=true')
  const { data: sales } = useFetch('/sales')

  const totalProducts = products?.length ?? 0
  const totalUnits = inventory?.reduce((sum, i) => sum + Number(i.quantity_on_hand), 0) ?? 0

  const now = new Date()
  const salesThisMonth = (sales ?? []).filter((s) => {
    const d = new Date(s.sale_date)
    return (
      s.status === 'PAID' &&
      d.getMonth() === now.getMonth() &&
      d.getFullYear() === now.getFullYear()
    )
  })
  const revenueThisMonth = salesThisMonth.reduce((sum, s) => sum + Number(s.total_amount), 0)

  return (
    <div>
      <h1>Dashboard</h1>

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-label">Productos</div>
          <div className="stat-value">{totalProducts}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Unidades en stock</div>
          <div className="stat-value">{totalUnits}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Bajo stock</div>
          <div className="stat-value">{lowStock?.length ?? 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Ventas del mes</div>
          <div className="stat-value">{money(revenueThisMonth)}</div>
        </div>
      </div>

      <div className="card">
        <h2>Alertas de stock</h2>
        {lowStock && lowStock.length === 0 && <p className="muted">Sin alertas por ahora.</p>}
        {lowStock && lowStock.length > 0 && (
          <table className="table">
            <thead>
              <tr>
                <th>Producto</th>
                <th>Bodega</th>
                <th>Disponible</th>
                <th>Mínimo</th>
              </tr>
            </thead>
            <tbody>
              {lowStock.map((i) => (
                <tr key={i.id}>
                  <td>
                    {i.product?.sku} — {i.product?.name}
                  </td>
                  <td>{i.warehouse?.name}</td>
                  <td className="text-danger">{i.quantity_available}</td>
                  <td>{i.minimum_stock}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
