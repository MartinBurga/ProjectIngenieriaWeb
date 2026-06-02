from dotenv import load_dotenv

from services.pronostico_services import pronosticarRentabilidadRuta
load_dotenv()
from flask import Flask, render_template, Blueprint
from utils.db import db
import pymysql, os


from utils.auth import login_required

from models.ruta import Ruta
from models.viajeRegistro import ViajeRegistro
from models.costo import Costo

from routes.rutas import rutas_bp
from routes.usuarios import usuarios_bp
from routes.costos import costos_bp
from routes.viajeRegistros import viaje_registros_bp

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.register_blueprint(rutas_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(costos_bp)
app.register_blueprint(viaje_registros_bp)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = os.getenv('SECRET_KEY')

db.init_app(app) 

@app.route("/")
def home():
    return render_template('login.html')

@app.route("/index")
@login_required
def index():
    rutas = Ruta.query.all()
    total_viajes = sum(len(ruta.viajes) for ruta in rutas)

    rentabilidad_rutas = {}

    for ruta in rutas:

        if not ruta.viajes:
            continue

        rentabilidad_ruta = {
            "registros_semanales": []
        }

        for v in ruta.viajes:

            costo = (
                getattr(v.costos, "monto", None)
                or getattr(v.costos, "valor", None)
                or getattr(v.costos, "costo", None)
                or getattr(v.costos, "total", None)
                or 0
            )

            rentabilidad_ruta["registros_semanales"].append({
                "fecha_fin": v.fechaFin,
                "rentabilidad": (v.pasajerosSemanal * ruta.precio_pasaje) - costo
            })

        pronostico_ruta = pronosticarRentabilidadRuta(rentabilidad_ruta)

        if (
            pronostico_ruta["estado"] == "ok"
            and pronostico_ruta["pronosticos"]
        ):

            promedio_futuro = sum(
                p["rentabilidad_estimada"]
                for p in pronostico_ruta["pronosticos"]
            ) / len(pronostico_ruta["pronosticos"])

            rentabilidad_rutas[ruta.idRuta] = {
                "valor": promedio_futuro,
                "es_rentable": promedio_futuro > 0
            }

    return render_template(
        "index.html",
        rutas=rutas,
        total_viajes=total_viajes,
        rentabilidad_rutas=rentabilidad_rutas
    )
if __name__ == "__main__":
    app.run(debug=True)