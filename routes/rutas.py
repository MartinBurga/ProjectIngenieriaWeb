from flask import Blueprint, request, render_template, redirect, url_for
from utils.auth import login_required
from models.ruta import Ruta
from utils.db import db

rutas_bp = Blueprint('rutas', __name__) 

@rutas_bp.route('/registrar', methods=['GET', 'POST'])
@login_required
def registrar_ruta():
    if request.method == 'POST':
        nueva_ruta = Ruta(
            nombreRuta=request.form.get('nombre_ruta'),
            origen=request.form.get('origen'),
            destino=request.form.get('destino'),
            distancia=float(request.form.get('distancia') or 0),
            precio_pasaje=float(request.form.get('precio_pasaje') or 0),
            pasajeros_Semanal=int(request.form.get('pasajeros_Semanal') or 0)
        )

        db.session.add(nueva_ruta)
        db.session.commit()

        return redirect(url_for('index'))

    total_rutas = Ruta.query.count()
    return render_template("form_ruta.html", total_rutas=total_rutas, edit_mode=False)

@rutas_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_ruta(id):
    ruta = Ruta.query.get_or_404(id)

    if request.method == 'POST':
        ruta.nombreRuta = request.form.get('nombre_ruta')
        ruta.origen = request.form.get('origen')
        ruta.destino = request.form.get('destino')
        ruta.distancia = float(request.form.get('distancia') or 0)
        ruta.precio_pasaje = float(request.form.get('precio_pasaje') or 0)
        ruta.pasajeros_Semanal = int(request.form.get('pasajeros_Semanal') or 0)

        db.session.commit()

        return redirect(url_for('index'))

    return render_template("form_ruta.html", ruta=ruta, edit_mode=True)


@rutas_bp.route('/eliminar/<int:id>')
@login_required
def eliminar_ruta(id):
    ruta = Ruta.query.get_or_404(id)

    db.session.delete(ruta)
    db.session.commit()

    return redirect(url_for('index'))