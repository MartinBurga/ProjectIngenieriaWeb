from abc import ABC, abstractmethod

from models.ruta import Ruta
from services.googlemaps_services import calcularDistancia


class RutaFactory(ABC):
    def crear(self, nombre_ruta, origen, destino, precio_pasaje):
        distancia, polyline = calcularDistancia(origen, destino)
        return self._crear(nombre_ruta, origen, destino, distancia, precio_pasaje, polyline)

    @abstractmethod
    def _crear(self, nombre_ruta, origen, destino, distancia, precio_pasaje, polyline):
        pass


class RutaTransporteFactory(RutaFactory):
    def _crear(self, nombre_ruta, origen, destino, distancia, precio_pasaje, polyline):
        return Ruta(
            nombreRuta=nombre_ruta,
            origen=origen,
            destino=destino,
            distancia=distancia,
            precio_pasaje=precio_pasaje,
            polyline=polyline,
        )
