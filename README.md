# Nido de Peluches

Aplicación web para donar y adoptar peluches. Desarrollada con Flask, Jinja2,
Bootstrap 5 y MySQL. Permite registrarse, iniciar sesión, publicar peluches,
editarlos y adoptar los de otros usuarios.

## Tecnologías

- Python 3.10+
- Flask 3.0.3
- Flask-Bcrypt
- Flask-WTF (CSRF)
- PyMySQL
- python-dotenv
- Bootstrap 5 (CDN)
- MySQL

## Estructura

```
NidoDePeluches/
├── flask_app/
│   ├── controllers/
│   ├── models/
│   ├── templates/
│   └── static/
├── server.py
├── db.py
├── extensions.py
├── esquema.sql
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Requisitos previos

- Python 3.10 o superior
- MySQL Server en ejecución
- pip

## Instalación en Windows

1. Abre CMD o PowerShell y sitúate en la carpeta del proyecto.
2. Crea y activa un entorno virtual:

   ```bat
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Instala dependencias:

   ```bat
   python -m pip install -r requirements.txt
   ```

4. Copia `.env.example` como `.env` y edita los valores:

   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=tu_usuario
   DB_PASSWORD=tu_contraseña
   DB_NAME=nido_peluches
   SECRET_KEY=una_clave_aleatoria_de_al_menos_32_caracteres
   COOKIE_SECURE=false
   ```

   `SECRET_KEY` debe tener al menos 32 caracteres aleatorios.

5. Ejecuta `esquema.sql` en MySQL para crear la base de datos y tablas.

6. Inicia la aplicación:

   ```bat
   python server.py
   ```

7. Abre `http://127.0.0.1:5000` en el navegador.

## Funcionalidades

- Registro e inicio de sesión con contraseñas hasheadas con Bcrypt.
- Cierre de sesión mediante POST con CSRF.
- Publicación de peluches para donación.
- Listado y detalle de peluches.
- Edición restringida al dueño.
- Adopción de peluches de otros usuarios.
- Contador de donaciones propias.
- Contador de visitas que excluye al donante.
- Visualización del nombre del adoptante.
- Mensajes de validación claros.
- Manejo de errores 403, 404 y 500.

## Bonus incluidos

1. Persistencia de datos del formulario ante errores de validación (registro,
   nueva donación y edición).
2. Contador de donaciones visible en el panel, en nueva donación, en edición
   y en el detalle.
3. Ocultación del botón de adoptar cuando el usuario es el dueño.
4. Registro del adoptante y visualización de su nombre.
5. Contador de visitas que no suma las visitas del donante.
6. Adopción única mediante `UPDATE ... WHERE adoptado = FALSE`.

## Bonus omitidos

No se incluyó eliminación de publicaciones ni de cuentas porque no formaban
parte de los requisitos evaluados.

## Seguridad

- Contraseñas limitadas a 72 bytes UTF-8 por el límite de Bcrypt.
- Todas las operaciones que modifican datos usan POST y token CSRF.
- Conexiones cerradas siempre con `finally`; `rollback` en errores.
- Excepción controlada `ErrorBaseDatos` que impide mostrar detalles de MySQL.
- Consultas parametrizadas.
- `SECRET_KEY` obligatoria de al menos 32 caracteres.

## Verificación realizada durante la preparación

- Se comprobó la sintaxis de los 10 archivos Python mediante `ast.parse`.
- Se comprobó la sintaxis Jinja de las 7 plantillas.
- Se verificó que estén presentes los archivos principales esperados.
- Se localizaron las 11 rutas Flask declaradas en los controladores.
- Se comprobaron los 6 formularios HTML y todos incluyen `csrf_token`.
- Se creó el ZIP y se verificó su integridad.
- **No se pudo iniciar la aplicación ni ejecutar pruebas funcionales**: este entorno no tiene instalados Flask, Flask-Bcrypt, Flask-WTF ni PyMySQL, y no se conectó a un servidor MySQL real. Registro, inicio de sesión, publicación, edición, adopción y contador de visitas deben probarse después de instalar las dependencias y configurar MySQL.

Estas comprobaciones son estáticas; no garantizan por sí solas que todos los flujos funcionen en ejecución.
