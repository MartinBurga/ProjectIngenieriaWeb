from utils.db import db

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
    
    def __init__(self, nombre, password):
        self.nombre = nombre
        self.password = password