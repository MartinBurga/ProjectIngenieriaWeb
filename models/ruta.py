from utils.db import db

class Ruta(db.Model):
    __tablename__ = 'ruta'

    id = db.Column(db.Integer, primary_key=True)
    nombreRuta = db.Column(db.String(100), nullable=False)
    origen = db.Column(db.String(100), nullable=False)
    destino = db.Column(db.String(100), nullable=False)
    distancia = db.Column(db.Float, nullable=False)
    precio_pasaje = db.Column(db.Float, nullable=False)
    pasajeros_Semanal = db.Column(db.Integer, nullable=False)