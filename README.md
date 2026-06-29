# Sistema de Gestion y Rentabilidad de Rutas

Aplicacion web desarrollada con Flask para registrar rutas de transporte, controlar viajes semanales, calcular costos operativos, medir rentabilidad y recomendar la unificacion de rutas similares. El proyecto usa una base de datos relacional con SQLAlchemy, consume Google Maps Routes API para calcular distancias y polylines, y puede generar pronosticos de rentabilidad con modelos SARIMA.

## Objetivo del proyecto

El sistema ayuda a analizar rutas de transporte desde una perspectiva operativa y financiera. Permite:

- Registrar rutas con origen, destino, distancia, precio de pasaje y polyline.
- Registrar viajes semanales por ruta con fechas y numero de pasajeros.
- Registrar costos por viaje: combustible, sueldo del conductor y mantenimiento.
- Calcular ingresos, costos totales y rentabilidad semanal.
- Consultar detalles de cada ruta y su historial de registros.
- Pronosticar rentabilidad futura cuando existe suficiente informacion historica.
- Detectar rutas similares y sugerir unificacion si otra ruta es mas rentable.
- Proteger pantallas internas mediante login.

## Tecnologias principales

- Python
- Flask
- Flask-SQLAlchemy
- MySQL o una base compatible con SQLAlchemy
- PyMySQL
- Jinja2
- Google Maps Routes API
- Requests
- Pandas
- Statsmodels
- Polyline, Shapely, PyProj y librerias geograficas auxiliares
- Python Dotenv

## Estructura del proyecto

```text
.
|-- app.py
|-- requirements.txt
|-- models/
|   |-- ruta.py
|   |-- viajeRegistro.py
|   |-- costo.py
|   `-- usuario.py
|-- routes/
|   |-- rutas.py
|   |-- usuarios.py
|   |-- costos.py
|   `-- viajeRegistros.py
|-- services/
|   |-- costo_services.py
|   |-- googlemaps_services.py
|   |-- pronostico_services.py
|   |-- unificacion_services.py
|   `-- similitud_services.py
|-- utils/
|   |-- auth.py
|   `-- db.py
|-- templates/
|   |-- login.html
|   |-- index.html
|   |-- form_ruta.html
|   |-- detalle_ruta.html
|   |-- form_viaje.html
|   `-- form_costos.html
`-- static/
```

## Configuracion inicial

### 1. Crear entorno virtual

```bash
python -m venv venv
```

En Windows PowerShell:

```bash
venv\Scripts\Activate.ps1
```

En Linux/macOS:

```bash
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Crear archivo `.env`

El proyecto carga variables de entorno con `python-dotenv`. Crea un archivo `.env` en la raiz del proyecto con valores similares a estos:

```env
DATABASE_URL=mysql+pymysql://usuario:password@localhost/nombre_base_datos
SECRET_KEY=clave-secreta-para-flask
GOOGLE_MAPS_API_KEY=tu-api-key-de-google-maps
```

### 4. Preparar base de datos

El proyecto espera estas entidades:

- `usuario`
- `ruta`
- `viaje_registro`
- `costo`

Los modelos estan definidos en `models/`. La aplicacion no incluye, en los archivos revisados, un comando automatico de migraciones, por lo que la base debe crearse manualmente o mediante un script adicional si se agrega al proyecto.

### 5. Ejecutar la aplicacion

```bash
python app.py
```

Por defecto Flask inicia en:

```text
http://127.0.0.1:5000
```

## Variables de entorno

| Variable | Descripcion |
| --- | --- |
| `DATABASE_URL` | Cadena de conexion usada por SQLAlchemy. |
| `SECRET_KEY` | Clave secreta de Flask para manejar sesiones. |
| `GOOGLE_MAPS_API_KEY` | API key usada para consultar Google Maps Routes API. |

## Flujo general de uso

1. El usuario entra a `/` o `/login`.
2. Inicia sesion con un usuario existente en la base de datos.
3. Accede al panel principal en `/index`.
4. Registra una ruta desde `/registrar`.
5. El sistema calcula distancia y polyline con Google Maps.
6. Desde el detalle de la ruta se registran viajes semanales.
7. Despues de cada viaje se registran los costos.
8. El sistema calcula la rentabilidad semanal.
9. Con suficientes registros, se genera un pronostico de rentabilidad.
10. El detalle de ruta muestra coincidencias con otras rutas y posibles unificaciones.

## Rutas principales de la aplicacion

### Autenticacion

| Metodo | Ruta | Descripcion |
| --- | --- | --- |
| `GET` | `/` | Muestra la pantalla de login. |
| `GET/POST` | `/login` | Inicia sesion validando usuario y password. |
| `GET` | `/index` | Muestra el panel principal. Requiere sesion. |

### Rutas de transporte

| Metodo | Ruta | Descripcion |
| --- | --- | --- |
| `GET/POST` | `/registrar` | Registra una nueva ruta. |
| `GET` | `/detalles/<ruta_id>` | Muestra detalle, rentabilidad, pronostico y coincidencias. |
| `GET/POST` | `/editar/<ruta_id>` | Edita una ruta existente. |
| `POST` | `/unificar/<ruta_id>/<id_ruta_candidata>` | Elimina la ruta base y conserva la candidata mas rentable. |
| `GET` | `/eliminar/<ruta_id>` | Elimina una ruta. |

### Registros semanales

| Metodo | Ruta | Descripcion |
| --- | --- | --- |
| `GET/POST` | `/ruta/<id_ruta>/registro-semanal` | Crea un registro semanal de pasajeros. |
| `GET` | `/registro/<id_viaje>/eliminar` | Elimina un registro semanal. |

### Costos

| Metodo | Ruta | Descripcion |
| --- | --- | --- |
| `GET/POST` | `/viaje/<id_viaje>/registrar-costos` | Registra costos de un viaje. |
| `GET/POST` | `/viaje/<id_viaje>/editar-costos` | Edita costos ya registrados. |

## Modelos de datos

### Usuario

Archivo: `models/usuario.py`

Representa a los usuarios que pueden iniciar sesion.

Campos principales:

- `id`
- `nombre`
- `password`

### Ruta

Archivo: `models/ruta.py`

Representa una ruta de transporte.

Campos principales:

- `idRuta`
- `nombreRuta`
- `origen`
- `destino`
- `distancia`
- `precio_pasaje`
- `polyline`

Relaciones:

- Una ruta tiene muchos registros semanales (`viajes`).
- Al eliminar una ruta, se eliminan sus viajes asociados por cascada.

### ViajeRegistro

Archivo: `models/viajeRegistro.py`

Representa un registro semanal de operacion para una ruta.

Campos principales:

- `idViaje`
- `idRuta`
- `pasajerosSemanal`
- `fechaInicio`
- `fechaFin`

Relaciones:

- Pertenece a una ruta.
- Tiene un unico registro de costos.

### Costo

Archivo: `models/costo.py`

Representa los costos operativos asociados a un viaje semanal.

Campos principales:

- `idCosto`
- `id_viaje`
- `precioCombustible`
- `sueldoConductor`
- `valorMantenimiento`

## Logica de negocio

### Calculo de distancia

Archivo: `services/googlemaps_services.py`

La funcion `calcularDistancia(origen, destino)` llama a Google Maps Routes API. Devuelve:

- Distancia en kilometros.
- Polyline codificado de la ruta.

Si la API falla o no devuelve rutas, retorna `0.0` y una cadena vacia.

### Calculo de rentabilidad

Archivo: `services/costo_services.py`

La rentabilidad se calcula a partir de:

```text
ingresos = precio_pasaje * pasajeros_semanales
costo_combustible = distancia * precio_combustible
costo_mantenimiento = (distancia / 100) * valor_mantenimiento
costo_total = costo_combustible + sueldo_conductor + costo_mantenimiento
rentabilidad = ingresos - costo_total
```

Funciones principales:

- `calcularRentabilidadCostos(...)`: calcula rentabilidad para un viaje.
- `determinarRentabilidadRuta(...)`: calcula rentabilidad acumulada para una ruta y sus registros.

### Pronostico de rentabilidad

Archivo: `services/pronostico_services.py`

La funcion `pronosticarRentabilidadRuta(...)` usa SARIMAX para estimar rentabilidad futura.

Condiciones importantes:

- Se necesitan al menos 8 registros semanales con rentabilidad.
- Si faltan dependencias como `pandas` o `statsmodels`, devuelve estado `dependencias_faltantes`.
- Si la serie no tiene variacion suficiente, devuelve estado `serie_sin_variacion`.
- Por defecto pronostica 4 semanas.

### Unificacion de rutas

Archivo: `services/unificacion_services.py`

La clase `unificarRuta` compara rutas mediante similitud de polylines. Usa un umbral por defecto de 70%.

Una ruta puede sugerirse para unificacion cuando:

- Su similitud con la ruta actual es igual o superior al 70%.
- La ruta candidata es mas rentable que la ruta base.

Cuando se confirma la unificacion, el sistema elimina la ruta base y conserva la ruta candidata.

## Validaciones importantes

### Registro semanal

En `routes/viajeRegistros.py` se valida que:

- Fecha de inicio, fecha de fin y pasajeros sean obligatorios.
- Las fechas usen formato `YYYY-MM-DD`.
- La fecha final sea posterior a la fecha inicial.
- El periodo no supere 7 dias.
- Los pasajeros sean un entero no negativo.
- No exista otro registro de la misma ruta con fechas solapadas.

### Costos

En `routes/costos.py` se valida que:

- Los costos sean numericos.
- Los costos no sean negativos.
- Un viaje no duplique registros de costos.
- Si ya existen costos, se redirige a edicion.

### Autenticacion

El decorador `login_required` en `utils/auth.py` protege las rutas internas. Si no existe `user_id` en la sesion, redirige al login.

## Pantallas principales

- `login.html`: formulario de inicio de sesion.
- `index.html`: panel principal con rutas y resumen.
- `form_ruta.html`: formulario para crear o editar rutas.
- `detalle_ruta.html`: detalle de ruta, rentabilidad, pronosticos y recomendaciones.
- `form_viaje.html`: registro semanal de pasajeros.
- `form_costos.html`: registro o edicion de costos.

## Consideraciones de seguridad

Actualmente el login compara el password directamente contra el valor guardado en la base de datos. Para un entorno real se recomienda:

- Guardar passwords con hash usando Werkzeug, bcrypt o Argon2.
- Agregar cierre de sesion.
- Validar permisos por usuario si hay multiples roles.
- Proteger acciones destructivas con metodo `POST` y CSRF tokens.
- No subir el archivo `.env` al repositorio.

## Posibles mejoras
- Encriptar contraseñas.


## Estado general

El proyecto ya cuenta con una arquitectura modular:

- `app.py` inicializa Flask, configura la base de datos y registra blueprints.
- `routes/` contiene las rutas HTTP.
- `models/` contiene las entidades de base de datos.
- `services/` concentra la logica de negocio.
- `utils/` contiene utilidades compartidas.
- `templates/` contiene las vistas HTML renderizadas con Jinja2.

Esta separacion facilita mantener la aplicacion, probar reglas de negocio y extender nuevas funcionalidades.

## Buenas practicas aplicadas: SOLID y patrones de diseno

Se aplicaron buenas practicas en el modulo de rutas:

- **DIP**: `routes/rutas.py` y `app.py` dependen de `IRutaRepository`, no directamente de SQLAlchemy.
- **OCP**: la creacion de rutas se delega a `RutaFactory`, permitiendo extender nuevos tipos de ruta sin cambiar el controlador.
- **Repository Pattern**: `DbRutaRepository` encapsula las operaciones de base de datos sobre `Ruta`.
- **Factory Method**: `RutaTransporteFactory` centraliza la creacion de rutas, incluyendo distancia y polyline.

Archivos principales: `repositories/ruta_repository.py`, `factories/ruta_factory.py`, `routes/rutas.py` y `app.py`.
