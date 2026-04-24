from flask import Flask, render_template, Blueprint
from utils.db import db
import pymysql
from utils.auth import login_required
from models.ruta import Ruta
from routes.rutas import rutas_bp
from routes.usuarios import usuarios_bp

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.register_blueprint(rutas_bp)
app.register_blueprint(usuarios_bp)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://u4d5alnxxnbo1gwp:yLgfep9D6PtRqRSxAFOr@b1ygrymdoru9zdb7umuw-mysql.services.clever-cloud.com:3306/b1ygrymdoru9zdb7umuw'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = 'SecretKeyForSessionManagement'

db.init_app(app) 

@app.route("/")
def home():
    return render_template('login.html')

@app.route("/index")

def index():
    rutas = Ruta.query.all()
    return render_template("index.html", rutas=rutas)

if __name__ == "__main__":
    app.run(debug=True)