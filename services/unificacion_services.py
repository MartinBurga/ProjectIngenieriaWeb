from models.ruta import Ruta
from services.similitud_services import similitud_services
from services.costo_services import determinarRentabilidadRuta
import logging


logger = logging.getLogger(__name__)


class unificarRuta:

    def __init__(self, umbral=70):
        self.umbral = umbral
        self.similitud = similitud_services()

    def _calcular_rentabilidad(self, ruta):
        """Calcula la rentabilidad real de una ruta usando costos y pasajeros semanales."""
        try:
            return determinarRentabilidadRuta(
                precio_combustible=0.0,
                sueldo_conductor=0.0,
                valor_mantenimiento=0.0,
                precio_pasaje=ruta.precio_pasaje,
                pasajeros=0,
                distancia=ruta.distancia,
                ruta=ruta,
            )
        except (ValueError, TypeError, AttributeError, KeyError, ZeroDivisionError) as error:
            logger.exception("Error calculando rentabilidad para ruta %s: %s", ruta.idRuta, error)
            return {
                "rentabilidad": 0.0,
                "registros_semanales": [],
            }

    def determinarRutasUnibles(self, ruta_actual):
        """
        Determina qué rutas pueden fusionarse con la ruta actual.
        Regla principal:
        1) similitud del polyline >= 70%
        2) la ruta candidata debe ser más rentable que la ruta actual
        """
        candidatos = []

        if not ruta_actual or not getattr(ruta_actual, "polyline", None):
            return candidatos

        rentabilidad_actual = self._calcular_rentabilidad(ruta_actual)
        rentabilidad_base = float(rentabilidad_actual.get("rentabilidad", 0.0) or 0.0)

        rutas = Ruta.query.filter(Ruta.idRuta != ruta_actual.idRuta).all()

        for ruta in rutas:
            if not getattr(ruta, "polyline", None):
                continue

            try:
                resultado = self.similitud.compare_routes(
                    ruta_actual.polyline,
                    ruta.polyline,
                )
            except (ValueError, TypeError, AttributeError, KeyError, ZeroDivisionError) as error:
                logger.exception(
                    "Error comparando ruta %s con ruta %s: %s",
                    ruta_actual.idRuta,
                    ruta.idRuta,
                    error,
                )
                continue

            score = float(resultado.get("score", 0.0) or 0.0)
            if score < self.umbral:
                continue

            rentabilidad_ruta = self._calcular_rentabilidad(ruta)
            rentabilidad_candidata = float(rentabilidad_ruta.get("rentabilidad", 0.0) or 0.0)

            diferencia = rentabilidad_candidata - rentabilidad_base
            es_mejor = rentabilidad_candidata > rentabilidad_base

            if not es_mejor:
                continue

            candidatos.append({
                "ruta": ruta,
                "score": round(score, 2),
                "frechet": resultado.get("frechet"),
                "origen": resultado.get("origen"),
                "destino": resultado.get("destino"),
                "rentabilidad_actual": round(rentabilidad_base, 2),
                "rentabilidad_candidata": round(rentabilidad_candidata, 2),
                "diferencia_rentabilidad": round(diferencia, 2),
                "predominante": True,
                "motivo": "Similitud >= 70% y rentabilidad superior a la ruta base.",
            })

        return sorted(candidatos, key=lambda item: item["score"], reverse=True)

    def buscarCoincidencias(self, ruta_actual):
        coincidencias = []

        if not ruta_actual.polyline:
            logger.warning(
                "Ruta %s no tiene polyline; no se pueden buscar coincidencias.",
                ruta_actual.idRuta
            )
            return coincidencias

        rutas = Ruta.query.filter(
            Ruta.idRuta != ruta_actual.idRuta
        ).all()

        for ruta in rutas:
            if not ruta.polyline:
                continue

            try:
                resultado = self.similitud.compare_routes(
                    ruta_actual.polyline,
                    ruta.polyline
                )
            except (ValueError, TypeError, AttributeError, KeyError, ZeroDivisionError) as error:
                logger.exception(
                    "Error comparando ruta %s con ruta %s: %s",
                    ruta_actual.idRuta,
                    ruta.idRuta,
                    error
                )
                continue

            if resultado["score"] >= self.umbral:
                coincidencias.append({
                    "ruta": ruta,
                    "score": resultado["score"],
                    "frechet": resultado["frechet"],
                    "origen": resultado["origen"],
                    "destino": resultado["destino"]
                })

        return sorted(
            coincidencias,
            key=lambda coincidencia: coincidencia["score"],
            reverse=True
        )
