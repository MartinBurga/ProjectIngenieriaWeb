from utils.db import db

class Costo(db.Model):
    __tablename__ = 'costo'

    idCosto = db.Column(db.Integer, primary_key=True)
    id_viaje = db.Column(db.Integer, db.ForeignKey('viaje_registro.idViaje'), nullable=False)
    precioCombustible = db.Column(db.Float, nullable=False)
    sueldoConductor = db.Column(db.Float, nullable=False)
    valorMantenimiento = db.Column(db.Float, nullable=False)