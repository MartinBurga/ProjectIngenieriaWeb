import { useMemo, useState } from "react";
import { api } from "../api/client.js";
import { currency } from "../utils/format.js";
import { emptyCosts } from "../utils/initialState.js";

export default function CostForm({ route, trip, onCancel, onSaved }) {
  const [form, setForm] = useState(trip.costos ? {
    precio_combustible: trip.costos.precio_combustible,
    sueldo_conductor: trip.costos.sueldo_conductor,
    valor_mantenimiento: trip.costos.valor_mantenimiento,
  } : emptyCosts);
  const [submitting, setSubmitting] = useState(false);

  const totals = useMemo(() => {
    const combustible = Number(form.precio_combustible) || 0;
    const sueldo = Number(form.sueldo_conductor) || 0;
    const mantenimiento = Number(form.valor_mantenimiento) || 0;
    const ingresos = trip.pasajeros_semanal * route.precio_pasaje;
    const total = sueldo + (route.distancia * combustible) + ((route.distancia / 100) * mantenimiento);
    return { ingresos, total, rentabilidad: ingresos - total };
  }, [form, route, trip]);

  async function submit(event) {
    event.preventDefault();
    setSubmitting(true);
    try {
      await api.put(`/api/viajes/${trip.id}/costos`, form);
      onSaved();
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="form-page">
      <h1>{trip.costos ? "Editar Costos" : "Registrar Costos"}</h1>
      <p>
        Ruta: <strong>{route.nombre}</strong> | Semana: <strong>{trip.fecha_inicio} - {trip.fecha_fin}</strong> | Pasajeros: <strong>{trip.pasajeros_semanal}</strong>
      </p>

      <form onSubmit={submit} className="cost-form">
        <label>Registro de viaje:</label><br />
        <select disabled>
          <option>#{trip.id} - {trip.fecha_inicio} a {trip.fecha_fin} ({trip.pasajeros_semanal} pasajeros)</option>
        </select>
        <br /><br />

        <div className="cost-grid">
          <div>
            <label>Combustible ($/km):</label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={form.precio_combustible}
              onChange={(event) => setForm({ ...form, precio_combustible: event.target.value })}
              placeholder="0.00"
              required
            />
          </div>
          <div>
            <label>Sueldo conductor ($):</label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={form.sueldo_conductor}
              onChange={(event) => setForm({ ...form, sueldo_conductor: event.target.value })}
              placeholder="0.00"
              required
            />
          </div>
          <div>
            <label>Mantenimiento ($/100 km):</label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={form.valor_mantenimiento}
              onChange={(event) => setForm({ ...form, valor_mantenimiento: event.target.value })}
              placeholder="0.00"
              required
            />
          </div>
        </div>

        <p>
          Ingresos estimados: {currency(totals.ingresos)} | Total costos: {currency(totals.total)} | Rentabilidad: <span className={totals.rentabilidad >= 0 ? "good" : "bad"}>{currency(totals.rentabilidad)}</span>
        </p>

        <button type="submit" disabled={submitting}>
          {submitting ? "Guardando..." : `${trip.costos ? "Actualizar" : "Guardar"} Costos`}
        </button>
        <button className="link-button" type="button" onClick={onCancel} disabled={submitting}>Cancelar</button>
      </form>
    </main>
  );
}
