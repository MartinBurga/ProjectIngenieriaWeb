import os
import requests
from flask import Blueprint, request, render_template, redirect, url_for
from utils.auth import login_required
from models.ruta import Ruta
from utils.db import db

rutas_bp = Blueprint('rutas', __name__) 

def calcularDistancia (origen, destino):
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "routes.distanceMeters,routes.polyline.encodedPolyline"
    }

    payload = {
        "origin": {"address": origen},
        "destination": {"address": destino},
        "travelMode": "DRIVE"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        data = response.json()
        if 'routes' in data and len(data['routes']) > 0:
            ruta_data = data['routes'][0]
            distancia = round(ruta_data['distanceMeters'] / 1000.0, 1)
            polyline = ruta_data['polyline']['encodedPolyline']
            return distancia, polyline
    except Exception as e:
        print(f"Error en Google Maps: {e}")
    
    return 0.0, ""

@rutas_bp.route('/detalles/<int:id>')
@login_required
def ver_detalle(id):
    ruta_seleccionada = Ruta.query.get_or_404(id)
    
    return render_template("detalle_ruta.html", ruta=ruta_seleccionada)

@rutas_bp.route('/registrar', methods=['GET', 'POST'])
@login_required
def registrar_ruta():
    if request.method == 'POST':
        origen = request.form.get('origen')
        destino = request.form.get('destino')

        totalDistancia, polyline = calcularDistancia(origen, destino)

        nueva_ruta = Ruta(
            nombreRuta=request.form.get('nombre_ruta'),
            origen=origen,
            destino=destino,
            distancia=totalDistancia,
            precio_pasaje=float(request.form.get('precio_pasaje') or 0),
            polyline=polyline
        )

        db.session.add(nueva_ruta)
        db.session.commit()
        return redirect(url_for('index'))

    total_rutas = Ruta.query.count()
    return render_template("form_ruta.html", total_rutas=total_rutas, edit_mode=False, ruta=None)

@rutas_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_ruta(id):
    ruta = Ruta.query.get_or_404(id)

    if request.method == 'POST':
        nuevo_origen = request.form.get('origen')
        nuevo_destino = request.form.get('destino')
        
        if ruta.origen != nuevo_origen or ruta.destino != nuevo_destino:
            ruta.distancia = calcularDistancia(nuevo_origen, nuevo_destino)

        ruta.nombreRuta = request.form.get('nombre_ruta')
        ruta.origen = nuevo_origen
        ruta.destino = nuevo_destino
        ruta.precio_pasaje = float(request.form.get('precio_pasaje') or 0)

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