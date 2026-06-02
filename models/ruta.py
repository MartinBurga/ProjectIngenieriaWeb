from utils.db import db

class Ruta(db.Model):
    __tablename__ = 'ruta'

    idRuta = db.Column(db.Integer, primary_key=True)
    nombreRuta = db.Column(db.String(100), nullable=False)
    origen = db.Column(db.String(100), nullable=False)
    destino = db.Column(db.String(100), nullable=False)
    distancia = db.Column(db.Float, nullable=False)
    precio_pasaje = db.Column(db.Float, nullable=False)
    polyline = db.Column(db.Text, nullable=True)
    # Relacion FK
    viajes = db.relationship('ViajeRegistro', backref='ruta', cascade="all, delete-orphan")

    def __init__(self, nombreRuta, origen, destino, distancia, precio_pasaje, polyline=""):
        self.nombreRuta = nombreRuta
        self.origen = origen
        self.destino = destino
        self.distancia = distancia
        self.precio_pasaje = precio_pasaje
        self.polyline = polyline