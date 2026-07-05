import { currency } from "../utils/format.js";

export default function HomePage({ routes, loading, onDetail, onEdit, onDelete }) {
  const totalTrips = routes.reduce((total, route) => total + route.viajes.length, 0);

  return (
    <main>
      <div className="main-header">
        <h1>Inicio</h1>
        <p>Bienvenido a Rootz!</p>
      </div>

      <div className="table_container-Rutas">
        <h3>Rutas</h3>
        {loading && <p>Cargando rutas...</p>}
        {!loading && routes.length === 0 && <p>No hay rutas registradas.</p>}
        {routes.length > 0 && (
          <table className="table-rutas">
            <thead>
              <tr>
                <th>ID</th>
                <th>Nombre</th>
                <th>Origen</th>
                <th>Destino</th>
                <th>Distancia (km)</th>
                <th>Valor Pasaje</th>
                <th>Rentabilidad Estimada</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {routes.map((route) => (
                <tr key={route.id}>
                  <td>{route.id}</td>
                  <td>{route.nombre}</td>
                  <td>{route.origen}</td>
                  <td>{route.destino}</td>
                  <td>{route.distancia} km</td>
                  <td>{currency(route.precio_pasaje)}</td>
                  <td>
                    {route.rentabilidad_estimada ? (
                      <span className={route.rentabilidad_estimada.es_rentable ? "good" : "bad"}>
                        {route.rentabilidad_estimada.es_rentable ? "Rentable" : "No rentable"}
                      </span>
                    ) : (
                      <em>Ver detalles</em>
                    )}
                  </td>
                  <td className="action-buttons">
                    <button className="btn btn-info" type="button" onClick={() => onDetail(route.id)}>
                      Detalles
                    </button>
                    <button className="btn btn-warning" type="button" onClick={() => onEdit(route)}>
                      Editar
                    </button>
                    <button className="btn btn-danger" type="button" onClick={() => onDelete(route.id)}>
                      Eliminar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="table_container-viajes">
        <h3>Viajes Realizados</h3>
        {totalTrips === 0 && <p>No hay viajes registrados.</p>}
        {routes
          .filter((route) => route.viajes.length > 0)
          .map((route) => (
            <div className="ruta-viajes-group" key={route.id}>
              <div className="accordion-btn">Ruta: {route.nombre}</div>
              <div className="accordion-content">
                <table className="ruta-viajes-table">
                  <thead>
                    <tr>
                      <th>ID Ruta</th>
                      <th>Ruta</th>
                      <th>Inicio</th>
                      <th>Fin</th>
                      <th>Pasajeros</th>
                    </tr>
                  </thead>
                  <tbody>
                    {route.viajes.map((trip) => (
                      <tr key={trip.id}>
                        <td>{route.id}</td>
                        <td>{route.nombre}</td>
                        <td>{trip.fecha_inicio}</td>
                        <td>{trip.fecha_fin}</td>
                        <td>{trip.pasajeros_semanal}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
      </div>
    </main>
  );
}
