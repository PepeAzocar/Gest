import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', end: true },
  { to: '/products', label: 'Productos' },
  { to: '/categories', label: 'Categorías' },
  { to: '/warehouses', label: 'Bodegas' },
  { to: '/inventory', label: 'Inventario' },
  { to: '/customers', label: 'Clientes' },
  { to: '/sales', label: 'Ventas' },
]

export default function Layout() {
  const { user, logout } = useAuth()

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="brand">Gest</div>
        <nav>
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="user-name">{user?.username}</div>
          <button className="btn btn-ghost" onClick={logout}>
            Cerrar sesión
          </button>
        </div>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  )
}
