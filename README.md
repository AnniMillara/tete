# Nido de Peluches

Aplicación web para publicar, donar y adoptar peluches. Está desarrollada con Flask, Jinja2, Bootstrap 5 y MySQL.

## Tecnologías

- Python 3.10+
- Flask
- Flask-Bcrypt
- Flask-WTF para protección CSRF
- PyMySQL
- python-dotenv
- MySQL
- Bootstrap 5 mediante CDN

## Estructura

- `flask_app/config/`: configuración y conexión a la base de datos.
- `flask_app/controllers/`: rutas y lógica de las solicitudes.
- `flask_app/models/`: clases y consultas de los modelos.
- `flask_app/templates/`: plantillas Jinja2.
- `flask_app/static/`: CSS y JavaScript.
- `esquema.sql`: creación de la base de datos y sus tablas.

## Instalación en Windows

1. Abre CMD o PowerShell en la carpeta del proyecto.
2. Crea y activa un entorno virtual:

   ```bat
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Instala las dependencias:

   ```bat
   python -m pip install -r requirements.txt
   ```

4. Copia `.env.example` como `.env` y completa las credenciales de MySQL.
5. Genera una clave secreta con:

   ```bat
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

   Copia el resultado en `SECRET_KEY` dentro de `.env`.
6. Ejecuta `esquema.sql` en MySQL.
7. Inicia la aplicación:

   ```bat
   python server.py
   ```

8. Abre `http://127.0.0.1:5000`.

## Configuración segura y errores comunes

- No subas el archivo `.env` al repositorio. Contiene credenciales locales y `SECRET_KEY`.
- No uses literalmente el valor de ejemplo de `SECRET_KEY`: la aplicación lo rechaza. Genera una clave propia con el comando de instalación.
- Para desplegar con HTTPS, configura `COOKIE_SECURE=true`; para desarrollo local por HTTP, usa `false`.
- Si aparece un mensaje de servicio temporalmente no disponible, revisa que MySQL esté iniciado, que el usuario y la contraseña de `.env` sean correctos y que hayas ejecutado `esquema.sql`. La aplicación muestra mensajes generales y no necesita revelar la excepción interna.
- Las fechas se generan automáticamente en MySQL (`creado_en`); el usuario no introduce fechas en los formularios, por lo que no existe un campo de fecha que validar.

## Comprobación manual antes de entregar

1. Registra una cuenta y confirma que puedes iniciar y cerrar sesión.
2. Intenta registrar dos veces el mismo correo y comprueba que se muestra un mensaje claro.
3. Publica un peluche, edítalo y elimínalo.
4. Inicia sesión con otra cuenta e intenta adoptar ese peluche; comprueba que no se pueda adoptar dos veces ni adoptar una donación propia.
5. Intenta abrir las rutas privadas sin iniciar sesión y editar una donación de otra persona.
6. Prueba nombres/descripciones vacíos y que excedan los límites; los datos deben rechazarse en el servidor.

## Funcionalidades

- Registro e inicio de sesión con contraseñas hasheadas con Bcrypt.
- Publicación, edición, eliminación y visualización de peluches.
- Adopción de peluches de otros usuarios.
- Prevención de adopciones dobles mediante una actualización condicional en MySQL.
- Contador de donaciones y visitas, sin contar las visitas del propio donante.
- Protección CSRF en los formularios POST.
- Diseño adaptable y mensajes de error generales.
- Clave secreta validada al iniciar la aplicación y límite de tamaño para solicitudes.

## Antes de entregar

Ejecuta toda la comprobación manual anterior con tu propia instancia de MySQL. Revisa también que las variables de entorno y los nombres de las tablas y campos coincidan con el entorno de despliegue y con la pauta de evaluación.
