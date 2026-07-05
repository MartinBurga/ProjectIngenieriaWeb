import { currency } from "../utils/format.js";

export default function RouteDetail({ route, onBack, onNewTrip, onCosts, onDeleteTrip }) {
  const registros = route.rentabilidad?.registros_semanales || [];
  const pronostico = route.pronostico || {};
  const trips = [...route.viajes].sort((a, b) => a.fecha_inicio.localeCompare(b.fecha_inicio));

  return (
    <div className="detalle-container">
      <h1>Ruta: {route.nombre}</h1>

      <div className="info-ruta">
        <p><strong>Origen:</strong> {route.origen}</p>
        <p><strong>Destino:</strong> {route.destino}</p>
        <p><strong>Distancia:</strong> {route.distancia} km</p>
        <p><strong>Precio por pasaje:</strong> {currency(route.precio_pasaje)}</p>
      </div>

      <h3>Registros Semanales</h3>
      {registros.length > 0 && (
        <div className="info-ruta">
          <p><strong>Rentabilidad acumulada:</strong> {currency(route.rentabilidad.rentabilidad)}</p>
        </div>
      )}

      {registros.length > 0 && (
        <>
          <h3>Pronostico SARIMA</h3>
          {pronostico.estado === "ok" ? (
            <>
              <p>
                Modelo usado: SARIMA{JSON.stringify(pronostico.modelo?.order)}
                {JSON.stringify(pronostico.modelo?.seasonal_order)}
              </p>
              <table className="table">
                <thead>
                  <tr>
                    <th>Semana</th>
                    <th>Fecha estimada</th>
                    <th>Rentabilidad estimada</th>
                    <th>Limite inferior</th>
                    <th>Limite superior</th>
                  </tr>
                </thead>
                <tbody>
                  {pronostico.pronosticos.map((item) => (
                    <tr key={item.semana}>
                      <td>{item.semana}</td>
                      <td>{item.fecha}</td>
                      <td>{currency(item.rentabilidad_estimada)}</td>
                      <td>{currency(item.limite_inferior)}</td>
                      <td>{currency(item.limite_superior)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          ) : (
            <p>{pronostico.mensaje}</p>
          )}
        </>
      )}

      {trips.length > 0 ? (
        <table className="table">
          <thead>
            <tr>
              <th>Fecha inicio</th>
              <th>Fecha fin</th>
              <th>Pasajeros</th>
              <th>Ingresos</th>
              <th>Costos Totales</th>
              <th>Rentabilidad</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {trips.map((trip) => (
              <tr key={trip.id}>
                <td>{trip.fecha_inicio}</td>
                <td>{trip.fecha_fin}</td>
                <td>{trip.pasajeros_semanal}</td>
                <td>{currency(trip.ingresos)}</td>
                {trip.costos ? (
                  <>
                    <td>{currency(trip.costos_totales)}</td>
                    <td>{currency(trip.rentabilidad)} {trip.rentabilidad >= 0 ? "up" : "down"}</td>
                    <td className="action-buttons">
                      <button className="btn btn-sm btn-warning" type="button" onClick={() => onCosts(trip)}>
                        Editar costos
                      </button>
                      <button className="btn btn-sm btn-danger" type="button" onClick={() => onDeleteTrip(trip.id, route.id)}>
                        Eliminar
                      </button>
                    </td>
                  </>
                ) : (
                  <>
                    <td><em>Sin costos</em></td>
                    <td>-</td>
                    <td className="action-buttons">
                      <button className="btn btn-sm btn-primary" type="button" onClick={() => onCosts(trip)}>
                        Agregar costos
                      </button>
                      <button className="btn btn-sm btn-danger" type="button" onClick={() => onDeleteTrip(trip.id, route.id)}>
                        Eliminar
                      </button>
                    </td>
                  </>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>Aun no hay registros semanales para esta ruta.</p>
      )}

      <div className="form-actions">
        <button className="btn btn-secondary" type="button" onClick={onBack}>Volver</button>
        <button className="btn btn-primary" type="button" onClick={onNewTrip}>Nuevo</button>
      </div>
    </div>
  );
}
