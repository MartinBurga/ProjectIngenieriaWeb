export default function Navbar({ onNavigate }) {
  return (
    <nav className="navbar">
      <div className="navbar_container">
        <div className="logo">
          <h2>Rootz</h2>
        </div>
        <ul className="nav__links">
          <li className="index__link">
            <button type="button" onClick={() => onNavigate({ name: "home" })}>
              Inicio
            </button>
          </li>
          <li className="registrar__link">
            <button type="button" onClick={() => onNavigate({ name: "route-form" })}>
              Registrar Ruta
            </button>
          </li>
        </ul>
      </div>
    </nav>
  );
}
