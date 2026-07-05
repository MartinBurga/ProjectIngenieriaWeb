export const api = {
  async request(path, options = {}) {
    const response = await fetch(path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.error || "No se pudo completar la operacion");
    }
    return data;
  },
  get(path) {
    return this.request(path);
  },
  post(path, payload) {
    return this.request(path, { method: "POST", body: JSON.stringify(payload) });
  },
  put(path, payload) {
    return this.request(path, { method: "PUT", body: JSON.stringify(payload) });
  },
  delete(path) {
    return this.request(path, { method: "DELETE" });
  },
};
