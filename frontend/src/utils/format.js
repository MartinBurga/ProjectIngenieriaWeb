export function currency(value) {
  const number = Number(value) || 0;
  return `$${number.toFixed(2)}`;
}

export function routeToForm(route) {
  return {
    nombre: route.nombre,
    origen: route.origen,
    destino: route.destino,
    precio_pasaje: route.precio_pasaje,
  };
}
