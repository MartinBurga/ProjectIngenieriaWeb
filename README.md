# 🚍 Sistema de Gestión de Rutas "Rootz" - Flask + MySQL

Aplicación web desarrollada con Flask que permite gestionar rutas de transporte, incluyendo registro, edición, eliminación y autenticación de usuarios (Ver. 1.0)

---

## 📌 Características

* 🔐 Sistema de autenticación (login con sesiones)
* 🛡️ Protección de rutas (solo usuarios autenticados)
* 📍 Gestión de rutas:

  * Crear rutas
  * Editar rutas
  * Eliminar rutas
  * Listar rutas desde base de datos
* 🗄️ Integración con MySQL usando SQLAlchemy
* 🎨 Interfaz básica con HTML + CSS

---

## 🧱 Tecnologías utilizadas

* Python 3
* Flask
* Flask SQLAlchemy
* MySQL
* PyMySQL
* HTML5 / CSS3

---

## 📂 Estructura del proyecto

```
ProyectoIngenieriaWeb/
│
├── app.py
├── index.py
│
├── models/
│   ├── ruta.py
│   └── usuario.py
│
├── routes/
│   ├── rutas.py
│   └── usuarios.py
│
├── utils/
│   ├── db.py
│   └── auth.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   └── form_ruta.html
│
├── static/
│   ├── styles.css
│   └── images/
│
└── README.md
```

---

## ⚙️ Instalación

### 1. Clonar repositorio

```bash
git clone https://github.com/tuusuario/tu-repo.git
cd tu-repo
```

---

### 2. Crear entorno virtual

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

---

### 3. Instalar dependencias

```bash
pip install flask flask_sqlalchemy pymysql
```

---

### 4. Configurar base de datos

Asegúrate de tener MySQL activo y crea la base de datos:

```sql
CREATE DATABASE rootzdb;
```

---

### 5. Configurar conexión

En `app.py`:

```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost:3306/rootzdb'
```

---

### 6. Crear tablas

```bash
python index.py
```

---

### 7. Ejecutar proyecto

```bash
python app.py
```

---

## 🔐 Credenciales de prueba

```plaintext
Usuario: admin1
Contraseña: rootz
```

---

## 🚀 Funcionalidades principales

| Función             | Descripción                     |
| ------------------- | ------------------------------- |
| Login               | Validación contra base de datos |
| CRUD rutas          | Gestión completa                |
| Protección de rutas | Acceso restringido              |

---

## 🧠 Aprendizajes clave

* Manejo de Blueprints en Flask
* Conexión a MySQL con SQLAlchemy
* Implementación de autenticación
* Manejo de sesiones
* Estructuración de proyectos Flask

---

## 👨‍💻 Autor

**Martin Burga**
Proyecto académico - Ingeniería Web

---
