import os
import requests

def calcularDistancia(origen, destino):
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
