from flask import Blueprint, request, render_template, redirect, url_for, flash
from utils.auth import login_required
from factories.ruta_factory import RutaFactory, RutaTransporteFactory
from repositories.ruta_repository import DbRutaRepository, IRutaRepository
from services.googlemaps_services import calcularDistancia
from services.costo_services import determinarRentabilidadRuta
from services.pronostico_services import pronosticarRentabilidadRuta
from services.unificacion_services import unificarRuta


rutas_bp = Blueprint('rutas', __name__)
ruta_repository: IRutaRepository = DbRutaRepository()
ruta_factory: RutaFactory = RutaTransporteFactory()

@rutas_bp.route('/detalles/<int:ruta_id>')
@login_required
def ver_detalle(ruta_id):
    ruta_seleccionada = ruta_repository.obtenerId(ruta_id)
    unificacion = unificarRuta()
    coincidencias = unificacion.buscarCoincidencias(ruta_seleccionada)
    rutas_unibles = unificacion.determinarRutasUnibles(ruta_seleccionada)
    rentabilidad_ruta = determinarRentabilidadRuta(
        precio_combustible=0.0, 
        sueldo_conductor=0.0,   
        valor_mantenimiento=0.0,  
        precio_pasaje=ruta_seleccionada.precio_pasaje,
        pasajeros=0,  
        distancia=ruta_seleccionada.distancia,
        ruta=ruta_seleccionada,
    )
    pronostico_ruta = pronosticarRentabilidadRuta(rentabilidad_ruta)
    rentabilidades = {
        registro["id_viaje"]: registro
        for registro in rentabilidad_ruta["registros_semanales"]
    }
    
    return render_template(
        "detalle_ruta.html",
        ruta=ruta_seleccionada,
        coincidencias=coincidencias,
        rutas_unibles=rutas_unibles,
        rentabilidades=rentabilidades,
        rentabilidad_ruta=rentabilidad_ruta,
        pronostico_ruta=pronostico_ruta,
    )
@rutas_bp.route('/registrar', methods=['GET', 'POST'])
@login_required
def registrar_ruta():
    if request.method == 'POST':
        origen = request.form.get('origen')
        destino = request.form.get('destino')

        nueva_ruta = ruta_factory.crear(
            nombre_ruta=request.form.get('nombre_ruta'),
            origen=origen,
            destino=destino,
            precio_pasaje=float(request.form.get('precio_pasaje') or 0),
        )

        ruta_repository.agregar(nueva_ruta)
        return redirect(url_for('rutas.ver_detalle', ruta_id=nueva_ruta.idRuta))

    total_rutas = ruta_repository.contar()
    return render_template("form_ruta.html", total_rutas=total_rutas, edit_mode=False, ruta=None)

@rutas_bp.route('/editar/<int:ruta_id>', methods=['GET', 'POST'])
@login_required
def editar_ruta(ruta_id):
    ruta = ruta_repository.obtenerId(ruta_id)

    if request.method == 'POST':
        nuevo_origen = request.form.get('origen')
        nuevo_destino = request.form.get('destino')
        
        if ruta.origen != nuevo_origen or ruta.destino != nuevo_destino:
            totalDistancia, polyline = calcularDistancia(
                nuevo_origen,
                nuevo_destino
            )
            ruta.distancia = totalDistancia
            ruta.polyline = polyline

        ruta.nombreRuta = request.form.get('nombre_ruta')
        ruta.origen = nuevo_origen
        ruta.destino = nuevo_destino
        ruta.precio_pasaje = float(request.form.get('precio_pasaje') or 0)

        ruta_repository.guardar()
        return redirect(url_for('rutas.ver_detalle', ruta_id=ruta.idRuta))

    return render_template("form_ruta.html", ruta=ruta, edit_mode=True)

@rutas_bp.route('/unificar/<int:ruta_id>/<int:id_ruta_candidata>', methods=['POST'])
@login_required
def unificar_ruta(ruta_id, id_ruta_candidata):
    ruta_base = ruta_repository.obtenerId(ruta_id)
    ruta_ganadora = ruta_repository.obtenerId(id_ruta_candidata)

    unificacion = unificarRuta()
    candidatos = unificacion.determinarRutasUnibles(ruta_base)

    candidato = next(
        (item for item in candidatos if item["ruta"].idRuta == id_ruta_candidata),
        None,
    )

    if not candidato:
        flash('No existe una recomendación válida para unificar esta ruta.', 'danger')
        return redirect(url_for('rutas.ver_detalle', ruta_id=ruta_id))

    ruta_repository.eliminar(ruta_base)

    flash(
        f'Ruta "{ruta_base.nombreRuta}" eliminada. Se mantuvo la ruta más rentable: "{ruta_ganadora.nombreRuta}".',
        'success',
    )
    return redirect(url_for('rutas.ver_detalle', ruta_id=id_ruta_candidata))


@rutas_bp.route('/eliminar/<int:ruta_id>')
@login_required
def eliminar_ruta(ruta_id):
    ruta = ruta_repository.obtenerId(ruta_id)

    ruta_repository.eliminar(ruta)

    return redirect(url_for('index'))
