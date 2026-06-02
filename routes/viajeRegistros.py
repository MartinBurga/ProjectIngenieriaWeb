from flask import Blueprint, request, redirect, url_for, render_template, flash
from models.viajeRegistro import ViajeRegistro
from models.ruta import Ruta
from utils.db import db
from utils.auth import login_required
from datetime import datetime
 
viaje_registros_bp = Blueprint('viaje_registros', __name__)
 
 
@viaje_registros_bp.route('/ruta/<int:id_ruta>/registro-semanal', methods=['GET', 'POST'])
@login_required
def crear_registro(id_ruta):
    ruta = Ruta.query.get_or_404(id_ruta)
 
    if request.method == 'POST':
        f_inicio_str  = request.form.get('fecha_inicio', '').strip()
        f_fin_str     = request.form.get('fecha_fin', '').strip()
        pasajeros_str = request.form.get('pasajeros', '').strip()
 
        # 1. Campos obligatorios
        if not f_inicio_str or not f_fin_str or not pasajeros_str:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template("form_viaje.html", ruta=ruta)
 
        # 2. Parseo seguro de fechas
        try:
            f_inicio = datetime.strptime(f_inicio_str, '%Y-%m-%d').date()
            f_fin    = datetime.strptime(f_fin_str,    '%Y-%m-%d').date()
        except ValueError:
            flash("Formato de fecha inválido.", "danger")
            return render_template("form_viaje.html", ruta=ruta)
 
        # 3. Coherencia: fin debe ser posterior al inicio
        if f_fin <= f_inicio:
            flash("La fecha de fin debe ser posterior a la de inicio.", "danger")
            return render_template("form_viaje.html", ruta=ruta)
 
        # 4. Límite semanal: máximo 7 días
        if (f_fin - f_inicio).days > 7:
            flash("El periodo no puede superar 7 días.", "danger")
            return render_template("form_viaje.html", ruta=ruta)
 
        # 5. Pasajeros: entero no negativo
        try:
            pasajeros = int(pasajeros_str)
            if pasajeros < 0:
                raise ValueError
        except ValueError:
            flash("El número de pasajeros debe ser un entero positivo.", "danger")
            return render_template("form_viaje.html", ruta=ruta)
 
        # 6. No puede haber otra semana que se cruce en fechas
        solapado = ViajeRegistro.query.filter(
            ViajeRegistro.idRuta == id_ruta,
            ViajeRegistro.fechaInicio <= f_fin,
            ViajeRegistro.fechaFin   >= f_inicio
        ).first()
        if solapado:
            flash(
                f"Ya existe un registro entre {solapado.fechaInicio} y {solapado.fechaFin}. "
                f"Las semanas no pueden solaparse.",
                "danger"
            )
            return render_template("form_viaje.html", ruta=ruta)
 
        # Guardar
        nuevo_viaje = ViajeRegistro(
            idRuta=id_ruta,
            pasajerosSemanal=pasajeros,
            fechaInicio=f_inicio,
            fechaFin=f_fin
        )
        db.session.add(nuevo_viaje)
        db.session.commit()
 
        flash("Registro semanal guardado. Ahora ingresa los costos.", "success")
        return redirect(url_for('costos.registrar_costos', id_viaje=nuevo_viaje.idViaje))
 
    return render_template("form_viaje.html", ruta=ruta)
 
 
@viaje_registros_bp.route('/registro/<int:id_viaje>/eliminar')
@login_required
def eliminar_registro(id_viaje):
    viaje = ViajeRegistro.query.get_or_404(id_viaje)
    id_ruta = viaje.idRuta
    db.session.delete(viaje)
    db.session.commit()
    flash("Registro eliminado.", "info")
    return redirect(url_for('rutas.ver_detalle', ruta_id=id_ruta))