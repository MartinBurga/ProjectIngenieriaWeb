from datetime import timedelta
import warnings


def _serie_rentabilidad(registros_semanales):
    return [
        {
            "fecha": registro["fecha_fin"],
            "rentabilidad": float(registro["rentabilidad"]),
        }
        for registro in registros_semanales
        if registro.get("fecha_fin") and registro.get("rentabilidad") is not None
    ]


def pronosticarRentabilidadRuta(
    rentabilidad_ruta,
    semanas=4,
    order=(1, 1, 1),
    seasonal_order=(1, 0, 1, 4),
):

    serie = _serie_rentabilidad(rentabilidad_ruta["registros_semanales"])
    if len(serie) < 8:
        return {
            "estado": "sin_datos_suficientes",
            "mensaje": "Se necesitan al menos 8 registros semanales con costos para pronosticar.",
            "modelo": None,
            "pronosticos": [],
        }

    try:
        import pandas as pd
        from statsmodels.tsa.statespace.sarimax import SARIMAX
    except ImportError:
        return {
            "estado": "dependencias_faltantes",
            "modelo": None,
            "pronosticos": [],
        }

    datos = pd.DataFrame(serie).sort_values("fecha")
    datos["fecha"] = pd.to_datetime(datos["fecha"])
    datos = datos.groupby("fecha", as_index=True)["rentabilidad"].sum()

    if datos.nunique() <= 1:
        return {
            "estado": "serie_sin_variacion",
            "mensaje": "La serie de rentabilidad no tiene variacion suficiente para SARIMA.",
            "modelo": None,
            "pronosticos": [],
        }

    modelo_usado = {
        "order": order,
        "seasonal_order": seasonal_order,
    }

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            modelo = SARIMAX(
                datos,
                order=order,
                seasonal_order=seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False,
            )
            resultado = modelo.fit(disp=False)
        except Exception:
            modelo_usado = {
                "order": (1, 1, 0),
                "seasonal_order": (0, 0, 0, 0),
            }
            modelo = SARIMAX(
                datos,
                order=modelo_usado["order"],
                seasonal_order=modelo_usado["seasonal_order"],
                enforce_stationarity=False,
                enforce_invertibility=False,
            )
            resultado = modelo.fit(disp=False)

    prediccion = resultado.get_forecast(steps=semanas)
    media = prediccion.predicted_mean
    intervalos = prediccion.conf_int()
    ultima_fecha = datos.index.max().date()

    pronosticos = []
    for indice in range(semanas):
        fecha = ultima_fecha + timedelta(days=7 * (indice + 1))
        intervalo = intervalos.iloc[indice]
        pronosticos.append({
            "semana": indice + 1,
            "fecha": fecha,
            "rentabilidad_estimada": round(float(media.iloc[indice]), 2),
            "limite_inferior": round(float(intervalo.iloc[0]), 2),
            "limite_superior": round(float(intervalo.iloc[1]), 2),
        })
        
        promedio_futuro = sum(p["rentabilidad_estimada"] for p in pronosticos) / len(pronosticos)
        rentabilidad = promedio_futuro > 0

    return {
    "estado": "ok",
    "mensaje": "Pronostico generado correctamente.",
    "modelo": modelo_usado,
    "pronosticos": pronosticos,
    "rentabilidad_futura": promedio_futuro,
    "rentabilidad": rentabilidad,
    }   
    