import { Outlet, Link } from "react-router-dom";

export function Layout() {
  return (
    <div className="layout">
      <header className="header">
        <Link to="/" className="logo">
          KINEO
        </Link>
        <nav>
          <Link to="/">Фільми</Link>
          <Link to="/sessions">Сеанси</Link>
          <Link to="/movies/new">Додати фільм</Link>
        </nav>
      </header>
      <main className="main">
        <Outlet />
      </main>
      <footer className="footer">
        <span>KINEO © {new Date().getFullYear()}</span>
      </footer>
    </div>
  );
}
