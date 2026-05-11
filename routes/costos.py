from flask import Blueprint, request, redirect, url_for, render_template, flash
from models.costo import Costo
from models.viajeRegistro import ViajeRegistro
from utils.db import db
from utils.auth import login_required

costos_bp = Blueprint('costos', __name__)


@costos_bp.route('/viaje/<int:id_viaje>/registrar-costos', methods=['GET', 'POST'])
@login_required
def registrar_costos(id_viaje):  # ← mismo nombre que la URL
    viaje = ViajeRegistro.query.get_or_404(id_viaje)
    ruta  = viaje.ruta

    if viaje.costos:
        flash("Este viaje ya tiene costos registrados.", "info")
        return redirect(url_for('costos.editar_costos', id_viaje=id_viaje))

    if request.method == 'POST':
        def parse_float(campo):
            try:
                valor = float(request.form.get(campo, '0').strip())
                if valor < 0:
                    raise ValueError
                return valor
            except ValueError:
                return None

        combustible   = parse_float('precioCombustible')
        sueldo        = parse_float('sueldoConductor')
        mantenimiento = parse_float('valorMantenimiento')

        if None in (combustible, sueldo, mantenimiento):
            flash("Los costos deben ser valores numéricos no negativos.", "danger")
            return render_template("form_costo.html", viaje=viaje, ruta=ruta, edit_mode=False)

        nuevo_costo = Costo(
            id_viaje=id_viaje,
            precioCombustible=combustible,
            sueldoConductor=sueldo,
            valorMantenimiento=mantenimiento
        )
        db.session.add(nuevo_costo)
        db.session.commit()

        flash("Costos registrados correctamente.", "success")
        return redirect(url_for('rutas.ver_detalle', id=ruta.idRuta))

    return render_template("form_costos.html", viaje=viaje, ruta=ruta, edit_mode=False)


@costos_bp.route('/viaje/<int:id_viaje>/editar-costos', methods=['GET', 'POST'])
@login_required
def editar_costos(id_viaje):  # ← mismo nombre que la URL
    viaje = ViajeRegistro.query.get_or_404(id_viaje)
    costos = viaje.costos
    ruta  = viaje.ruta

    if not costos:
        return redirect(url_for('costos.registrar_costos', id_viaje=id_viaje))

    if request.method == 'POST':
        try:
            costos.precioCombustible  = max(0.0, float(request.form.get('precioCombustible', 0)))
            costos.sueldoConductor    = max(0.0, float(request.form.get('sueldoConductor', 0)))
            costos.valorMantenimiento = max(0.0, float(request.form.get('valorMantenimiento', 0)))
            db.session.commit()
            flash("Costos actualizados.", "success")
        except ValueError:
            flash("Valores inválidos.", "danger")
        return redirect(url_for('rutas.ver_detalle', id=ruta.idRuta))

    return render_template("form_costos.html", viaje=viaje, ruta=ruta, edit_mode=True)