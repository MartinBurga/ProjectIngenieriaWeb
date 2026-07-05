from datetime import datetime

from flask import Blueprint, jsonify, request

from models.costo import Costo
from models.ruta import Ruta
from models.viajeRegistro import ViajeRegistro
from services.costo_services import determinarRentabilidadRuta
from services.googlemaps_services import calcularDistancia
from services.pronostico_services import pronosticarRentabilidadRuta
from utils.db import db


api_bp = Blueprint("api", __name__, url_prefix="/api")


def _date_to_iso(value):
    return value.isoformat() if value else None


def _json_ready(value):
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _serialize_costo(costo):
    if not costo:
        return None

    total = (
        float(costo.precioCombustible or 0)
        + float(costo.sueldoConductor or 0)
        + float(costo.valorMantenimiento or 0)
    )

    return {
        "id": costo.idCosto,
        "precio_combustible": float(costo.precioCombustible or 0),
        "sueldo_conductor": float(costo.sueldoConductor or 0),
        "valor_mantenimiento": float(costo.valorMantenimiento or 0),
        "total_simple": round(total, 2),
    }


def _serialize_viaje(viaje):
    ingresos = float((viaje.pasajerosSemanal or 0) * (viaje.ruta.precio_pasaje or 0))
    rentabilidad = None
    costos_totales = None

    if viaje.costos:
        resultado = determinarRentabilidadRuta(
            precio_combustible=viaje.costos.precioCombustible,
            sueldo_conductor=viaje.costos.sueldoConductor,
            valor_mantenimiento=viaje.costos.valorMantenimiento,
            precio_pasaje=viaje.ruta.precio_pasaje,
            pasajeros=viaje.pasajerosSemanal,
            distancia=viaje.ruta.distancia,
        )["registros_semanales"][0]
        costos_totales = resultado["costos_totales"]
        rentabilidad = resultado["rentabilidad"]

    return {
        "id": viaje.idViaje,
        "id_ruta": viaje.idRuta,
        "ruta_nombre": viaje.ruta.nombreRuta,
        "pasajeros_semanal": viaje.pasajerosSemanal,
        "fecha_inicio": _date_to_iso(viaje.fechaInicio),
        "fecha_fin": _date_to_iso(viaje.fechaFin),
        "ingresos": round(ingresos, 2),
        "costos_totales": costos_totales,
        "rentabilidad": rentabilidad,
        "costos": _serialize_costo(viaje.costos),
    }


def _serialize_ruta(ruta, include_viajes=False, include_analytics=False):
    data = {
        "id": ruta.idRuta,
        "nombre": ruta.nombreRuta,
        "origen": ruta.origen,
        "destino": ruta.destino,
        "distancia": float(ruta.distancia or 0),
        "precio_pasaje": float(ruta.precio_pasaje or 0),
        "polyline": ruta.polyline,
        "total_viajes": len(ruta.viajes),
    }

    if include_viajes:
        data["viajes"] = [_serialize_viaje(viaje) for viaje in ruta.viajes]

    if include_analytics:
        rentabilidad = determinarRentabilidadRuta(
            precio_combustible=0.0,
            sueldo_conductor=0.0,
            valor_mantenimiento=0.0,
            precio_pasaje=ruta.precio_pasaje,
            pasajeros=0,
            distancia=ruta.distancia,
            ruta=ruta,
        )
        pronostico = pronosticarRentabilidadRuta(rentabilidad)
        data["rentabilidad"] = _json_ready(rentabilidad)
        data["pronostico"] = _json_ready(pronostico)

    return data


def _rentabilidad_estimada(ruta):
    rentabilidad = determinarRentabilidadRuta(
        precio_combustible=0.0,
        sueldo_conductor=0.0,
        valor_mantenimiento=0.0,
        precio_pasaje=ruta.precio_pasaje,
        pasajeros=0,
        distancia=ruta.distancia,
        ruta=ruta,
    )
    pronostico = pronosticarRentabilidadRuta(rentabilidad)

    if pronostico["estado"] != "ok" or not pronostico["pronosticos"]:
        return None

    promedio_futuro = sum(
        item["rentabilidad_estimada"] for item in pronostico["pronosticos"]
    ) / len(pronostico["pronosticos"])

    return {
        "valor": round(float(promedio_futuro), 2),
        "es_rentable": promedio_futuro > 0,
    }


def _required_json(*fields):
    payload = request.get_json(silent=True) or {}
    missing = [field for field in fields if payload.get(field) in (None, "")]
    if missing:
        return payload, jsonify({"error": "Campos obligatorios faltantes", "fields": missing}), 400
    return payload, None, None


@api_bp.get("/health")
def health():
    return jsonify({"status": "ok", "service": "rootz-api"})


@api_bp.get("/rutas")
def listar_rutas():
    rutas = Ruta.query.order_by(Ruta.idRuta.desc()).all()
    include_analytics = request.args.get("analytics") == "1"
    data = [_serialize_ruta(ruta, include_viajes=True) for ruta in rutas]

    if include_analytics:
        for item, ruta in zip(data, rutas):
            item["rentabilidad_estimada"] = _rentabilidad_estimada(ruta)

    return jsonify(data)


@api_bp.post("/rutas")
def crear_ruta():
    payload, error_response, status = _required_json(
        "nombre",
        "origen",
        "destino",
        "precio_pasaje",
    )
    if error_response:
        return error_response, status

    try:
        distancia, polyline = calcularDistancia(payload["origen"], payload["destino"])
        ruta = Ruta(
            nombreRuta=payload["nombre"],
            origen=payload["origen"],
            destino=payload["destino"],
            distancia=distancia,
            precio_pasaje=float(payload["precio_pasaje"]),
            polyline=polyline,
        )
    except (TypeError, ValueError):
        return jsonify({"error": "precio_pasaje debe ser numerico"}), 400

    db.session.add(ruta)
    db.session.commit()
    return jsonify(_serialize_ruta(ruta, include_viajes=True)), 201


@api_bp.get("/rutas/<int:ruta_id>")
def obtener_ruta(ruta_id):
    ruta = Ruta.query.get_or_404(ruta_id)
    return jsonify(_serialize_ruta(ruta, include_viajes=True, include_analytics=True))


@api_bp.put("/rutas/<int:ruta_id>")
def actualizar_ruta(ruta_id):
    ruta = Ruta.query.get_or_404(ruta_id)
    payload, error_response, status = _required_json(
        "nombre",
        "origen",
        "destino",
        "precio_pasaje",
    )
    if error_response:
        return error_response, status

    try:
        origen_cambio = ruta.origen != payload["origen"]
        destino_cambio = ruta.destino != payload["destino"]

        if origen_cambio or destino_cambio:
            distancia, polyline = calcularDistancia(payload["origen"], payload["destino"])
            ruta.distancia = distancia
            ruta.polyline = polyline

        ruta.nombreRuta = payload["nombre"]
        ruta.origen = payload["origen"]
        ruta.destino = payload["destino"]
        ruta.precio_pasaje = float(payload["precio_pasaje"])
    except (TypeError, ValueError):
        return jsonify({"error": "precio_pasaje debe ser numerico"}), 400

    db.session.commit()
    return jsonify(_serialize_ruta(ruta, include_viajes=True, include_analytics=True))


@api_bp.delete("/rutas/<int:ruta_id>")
def eliminar_ruta(ruta_id):
    ruta = Ruta.query.get_or_404(ruta_id)
    db.session.delete(ruta)
    db.session.commit()
    return jsonify({"ok": True})


@api_bp.get("/rutas/<int:ruta_id>/viajes")
def listar_viajes_ruta(ruta_id):
    Ruta.query.get_or_404(ruta_id)
    viajes = (
        ViajeRegistro.query.filter_by(idRuta=ruta_id)
        .order_by(ViajeRegistro.fechaInicio.desc())
        .all()
    )
    return jsonify([_serialize_viaje(viaje) for viaje in viajes])


@api_bp.post("/rutas/<int:ruta_id>/viajes")
def crear_viaje_ruta(ruta_id):
    Ruta.query.get_or_404(ruta_id)
    payload, error_response, status = _required_json(
        "fecha_inicio",
        "fecha_fin",
        "pasajeros_semanal",
    )
    if error_response:
        return error_response, status

    try:
        fecha_inicio = datetime.strptime(payload["fecha_inicio"], "%Y-%m-%d").date()
        fecha_fin = datetime.strptime(payload["fecha_fin"], "%Y-%m-%d").date()
        pasajeros = int(payload["pasajeros_semanal"])
    except (TypeError, ValueError):
        return jsonify({"error": "Fechas invalidas o pasajeros no numerico"}), 400

    if fecha_fin <= fecha_inicio:
        return jsonify({"error": "La fecha de fin debe ser posterior a la fecha de inicio"}), 400

    if pasajeros < 0:
        return jsonify({"error": "Los pasajeros no pueden ser negativos"}), 400

    viaje = ViajeRegistro(
        idRuta=ruta_id,
        fechaInicio=fecha_inicio,
        fechaFin=fecha_fin,
        pasajerosSemanal=pasajeros,
    )
    db.session.add(viaje)
    db.session.commit()
    return jsonify(_serialize_viaje(viaje)), 201


@api_bp.delete("/viajes/<int:viaje_id>")
def eliminar_viaje(viaje_id):
    viaje = ViajeRegistro.query.get_or_404(viaje_id)
    db.session.delete(viaje)
    db.session.commit()
    return jsonify({"ok": True})


@api_bp.post("/viajes/<int:viaje_id>/costos")
@api_bp.put("/viajes/<int:viaje_id>/costos")
def guardar_costos(viaje_id):
    viaje = ViajeRegistro.query.get_or_404(viaje_id)
    payload, error_response, status = _required_json(
        "precio_combustible",
        "sueldo_conductor",
        "valor_mantenimiento",
    )
    if error_response:
        return error_response, status

    try:
        precio_combustible = float(payload["precio_combustible"])
        sueldo_conductor = float(payload["sueldo_conductor"])
        valor_mantenimiento = float(payload["valor_mantenimiento"])
    except (TypeError, ValueError):
        return jsonify({"error": "Los costos deben ser numericos"}), 400

    if min(precio_combustible, sueldo_conductor, valor_mantenimiento) < 0:
        return jsonify({"error": "Los costos no pueden ser negativos"}), 400

    costo = viaje.costos
    if not costo:
        costo = Costo(
            id_viaje=viaje_id,
            precioCombustible=precio_combustible,
            sueldoConductor=sueldo_conductor,
            valorMantenimiento=valor_mantenimiento,
        )
        db.session.add(costo)
    else:
        costo.precioCombustible = precio_combustible
        costo.sueldoConductor = sueldo_conductor
        costo.valorMantenimiento = valor_mantenimiento

    db.session.commit()
    return jsonify(_serialize_viaje(viaje))


@api_bp.get("/resumen")
def resumen():
    rutas = Ruta.query.all()
    total_viajes = sum(len(ruta.viajes) for ruta in rutas)
    rutas_con_costos = sum(
        1 for ruta in rutas for viaje in ruta.viajes if viaje.costos
    )

    return jsonify({
        "total_rutas": len(rutas),
        "total_viajes": total_viajes,
        "viajes_con_costos": rutas_con_costos,
    })
