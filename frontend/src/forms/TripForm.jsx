import { useState } from "react";
import { api } from "../api/client.js";
import { currency } from "../utils/format.js";
import { emptyTrip } from "../utils/initialState.js";

export default function TripForm({ route, onCancel, onSaved }) {
  const [form, setForm] = useState(emptyTrip);
  const [submitting, setSubmitting] = useState(false);
  const today = new Date().toISOString().slice(0, 10);

  async function submit(event) {
    event.preventDefault();
    const start = new Date(form.fecha_inicio);
    const end = new Date(form.fecha_fin);
    const diffDays = (end - start) / 86400000;

    if (form.fecha_fin <= form.fecha_inicio) {
      window.alert("La fecha de fin debe ser posterior al inicio.");
      return;
    }

    if (diffDays > 7) {
      window.alert("El periodo no puede superar 7 dias.");
      return;
    }

    setSubmitting(true);
    try {
      await api.post(`/api/rutas/${route.id}/viajes`, form);
      onSaved(route.id);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="form-container">
      <h1>Registro Semanal</h1>
      <p className="subtitle">Ruta: <strong>{route.nombre}</strong></p>
      <hr />
      <form onSubmit={submit}>
        <div className="form-group">
          <label htmlFor="sel_ruta">Ruta asignada</label>
          <select id="sel_ruta" disabled>
            <option>#{route.id} - {route.nombre} ({route.origen} a {route.destino})</option>
          </select>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="fecha_inicio">Fecha inicio de semana</label>
            <input
              id="fecha_inicio"
              type="date"
              required
              max={today}
              value={form.fecha_inicio}
              onChange={(event) => setForm({ ...form, fecha_inicio: event.target.value })}
            />
          </div>
          <div className="form-group">
            <label htmlFor="fecha_fin">Fecha fin de semana</label>
            <input
              id="fecha_fin"
              type="date"
              required
              max={today}
              value={form.fecha_fin}
              onChange={(event) => setForm({ ...form, fecha_fin: event.target.value })}
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="pasajeros">Pasajeros transportados en la semana</label>
          <input
            id="pasajeros"
            type="number"
            min="0"
            placeholder="Ej: 320"
            required
            value={form.pasajeros_semanal}
            onChange={(event) => setForm({ ...form, pasajeros_semanal: event.target.value })}
          />
        </div>

        <div className="info-box">
          <p>
            <strong>Precio por pasaje:</strong> {currency(route.precio_pasaje)}<br />
            <em>Los costos operativos se ingresaran en el siguiente paso.</em>
          </p>
        </div>

        <div className="form-actions">
          <button className="btn btn-secondary" type="button" onClick={onCancel} disabled={submitting}>Cancelar</button>
          <button className="btn btn-primary" type="submit" disabled={submitting}>
            {submitting ? "Guardando..." : "Siguiente: Ingresar Costos"}
          </button>
        </div>
      </form>
    </div>
  );
}
