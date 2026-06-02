from models.ruta import Ruta
from services.similitud_services import similitud_services
import logging


logger = logging.getLogger(__name__)


class unificarRuta:

    def __init__(self, umbral=75):
        self.umbral = umbral
        self.similitud = similitud_services()

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
            except Exception as error:
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
