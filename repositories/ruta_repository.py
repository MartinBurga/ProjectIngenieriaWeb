from abc import ABC, abstractmethod

from models.ruta import Ruta
from utils.db import db


class IRutaRepository(ABC):
    @abstractmethod
    def listar(self):
        pass

    @abstractmethod
    def contar(self):
        pass

    @abstractmethod
    def obtenerId(self, ruta_id):
        pass

    @abstractmethod
    def agregar(self, ruta):
        pass

    @abstractmethod
    def eliminar(self, ruta):
        pass

    @abstractmethod
    def guardar(self):
        pass


class DbRutaRepository(IRutaRepository):
    def listar(self):
        return Ruta.query.all()

    def contar(self):
        return Ruta.query.count()

    def obtenerId(self, ruta_id):
        return Ruta.query.get_or_404(ruta_id)

    def agregar(self, ruta):
        db.session.add(ruta)
        self.guardar()
        return ruta

    def eliminar(self, ruta):
        db.session.delete(ruta)
        self.guardar()

    def guardar(self):
        db.session.commit()
