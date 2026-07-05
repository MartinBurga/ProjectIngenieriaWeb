import { api } from "../api/client.js";
import { currency, routeToForm } from "../utils/format.js";
import { emptyRoute } from "../utils/initialState.js";
import { useState } from "react";

export default function RouteForm({ route, nextId, onCancel, onSaved }) {
  const [form, setForm] = useState(route ? routeToForm(route) : emptyRoute);
  const [submitting, setSubmitting] = useState(false);
  const editMode = Boolean(route);

  async function submit(event) {
    event.preventDefault();
    setSubmitting(true);
    try {
      const saved = editMode
        ? await api.put(`/api/rutas/${route.id}`, form)
        : await api.post("/api/rutas", form);
      onSaved(saved);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="form-page">
      <h1>{editMode ? "Editar Ruta" : "Registro de Ruta"}</h1>
      <form onSubmit={submit}>
        <label>ID:</label><br />
        <input type="text" value={editMode ? route.id : nextId} readOnly /><br /><br />

        <label>Nombre de Ruta:</label><br />
        <input
          type="text"
          value={form.nombre}
          onChange={(event) => setForm({ ...form, nombre: event.target.value })}
          required
        /><br /><br />

        <div className="form-group">
          <label>Origen</label>
          <input
            type="text"
            value={form.origen}
            onChange={(event) => setForm({ ...form, origen: event.target.value })}
            required
            placeholder="Ej: Terminal Quitumbe, Quito"
          />
        </div>

        <div className="form-group">
          <label>Destino</label>
          <input
            type="text"
            value={form.destino}
            onChange={(event) => setForm({ ...form, destino: event.target.value })}
            required
            placeholder="Ej: Terminal Carcelen, Quito"
          />
        </div>

        {editMode && (
          <div className="info-box">
            <p>
              <strong>Distancia calculada:</strong> {route.distancia} km<br />
              <em>Si cambias origen o destino, el backend recalculara la ruta con Google Maps.</em>
            </p>
          </div>
        )}

        <div className="form-group">
          <label>Precio Pasaje ($):</label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={form.precio_pasaje}
            onChange={(event) => setForm({ ...form, precio_pasaje: event.target.value })}
            required
          />
        </div>

        {Number(form.precio_pasaje) > 0 && (
          <p>Valor ingresado: <strong>{currency(form.precio_pasaje)}</strong></p>
        )}

        <button type="submit" disabled={submitting}>
          {submitting ? "Guardando..." : `${editMode ? "Actualizar" : "Guardar"} Ruta`}
        </button>
        <button className="link-button" type="button" onClick={onCancel} disabled={submitting}>Cancelar</button>
      </form>
    </main>
  );
}
