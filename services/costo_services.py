def determinarRentabilidadRuta(
    precio_combustible,
    sueldo_conductor,
    valor_mantenimiento,
    precio_pasaje,
    pasajeros,
    distancia,
    ruta=None,
):
    registros_semanales = []

    if ruta is not None:
        for viaje in ruta.viajes:
            if not viaje.costos:
                continue

            resultado = calcularRentabilidadCostos(
                viaje,
                precio_combustible=viaje.costos.precioCombustible,
                sueldo_conductor=viaje.costos.sueldoConductor,
                valor_mantenimiento=viaje.costos.valorMantenimiento,
            )
            registros_semanales.append({
                "id_viaje": viaje.idViaje,
                "fecha_inicio": viaje.fechaInicio,
                "fecha_fin": viaje.fechaFin,
                "pasajeros": viaje.pasajerosSemanal,
                "ingresos": resultado["ingresos"],
                "costos_totales": resultado["costo_total"],
                "rentabilidad": resultado["rentabilidad"],
            })

        return {
            "rentabilidad": float(round(
                sum(registro["rentabilidad"] for registro in registros_semanales),
                2,
            )),
            "registros_semanales": registros_semanales,
        }

    costo_total = (
        (float(distancia or 0.0) * precio_combustible)
        + sueldo_conductor
        + ((float(distancia or 0.0) / 100.0) * valor_mantenimiento)
    )
    ingresos = precio_pasaje * pasajeros
    rentabilidad = ingresos - costo_total
    
    return {
        "rentabilidad": float(round(rentabilidad, 2)),
        "registros_semanales": [{
            "id_viaje": None,
            "fecha_inicio": None,
            "fecha_fin": None,
            "pasajeros": pasajeros,
            "ingresos": float(round(ingresos, 2)),
            "costos_totales": float(round(costo_total, 2)),
            "rentabilidad": float(round(rentabilidad, 2)),
        }],
    }


def calcularRentabilidadCostos(
    viaje,
    precio_combustible: float,
    sueldo_conductor: float,
    valor_mantenimiento: float,
):

    precio_pasaje = float(viaje.ruta.precio_pasaje or 0.0)
    distancia = float(viaje.ruta.distancia or 0.0)
    
    pasajeros_estimados = int(viaje.pasajerosSemanal or 0)
    costo_combustible = distancia * precio_combustible
    costo_mantenimiento = (distancia / 100.0) * valor_mantenimiento
    costo_fijo_viaje = sueldo_conductor + costo_mantenimiento
    costo_total = costo_combustible + costo_fijo_viaje
    ingresos = precio_pasaje * pasajeros_estimados
    rentabilidad = ingresos - costo_total

    return {
        "rentabilidad": float(round(rentabilidad, 2)),
        "costo_combustible": float(round(costo_combustible, 2)),
        "costo_fijo_viaje": float(round(costo_fijo_viaje, 2)),
        "costo_total": float(round(costo_total, 2)),
        "ingresos": float(round(ingresos, 2)),
        "pasajeros_estimados": pasajeros_estimados,
    }
