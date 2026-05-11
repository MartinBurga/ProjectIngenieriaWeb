from utils.db import db
from datetime import datetime

class ViajeRegistro(db.Model):
    __tablename__ = 'viaje_registro'

    idViaje = db.Column(db.Integer, primary_key=True)
    idRuta = db.Column(db.Integer, db.ForeignKey('ruta.idRuta'), nullable=False)
    pasajerosSemanal = db.Column(db.Integer, nullable=False)
    fechaInicio = db.Column(db.Date, nullable=False)
    fechaFin = db.Column(db.Date, nullable=False)
    # Relacion FK
    costos = db.relationship('Costo', backref='viaje', uselist=False, cascade="all, delete-orphan")