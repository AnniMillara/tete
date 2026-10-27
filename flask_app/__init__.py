import os

from dotenv import load_dotenv
from flask import Flask, render_template

load_dotenv()


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    secret_key = os.getenv("SECRET_KEY")
    clave_de_ejemplo = "reemplaza_esto_por_una_clave_aleatoria"
    if (
        not secret_key
        or len(secret_key) < 32
        or clave_de_ejemplo in secret_key.lower()
    ):
        raise RuntimeError(
            "Configura SECRET_KEY en .env con una clave propia de al menos "
            "32 caracteres aleatorios; no uses el valor de ejemplo."
        )

    app.config["SECRET_KEY"] = secret_key
    app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = (
        os.getenv("COOKIE_SECURE", "false").lower() == "true"
    )

    from flask_app.config import bcrypt, csrf
    bcrypt.init_app(app)
    csrf.init_app(app)

    from flask_app.controllers.usuarios import init_usuarios
    from flask_app.controllers.peluches import init_peluches
    init_usuarios(app)
    init_peluches(app)

    @app.errorhandler(403)
    def prohibido(error):
        return render_template(
            "error.html", codigo=403,
            mensaje="No tienes permiso para acceder aquí."
        ), 403

    @app.errorhandler(404)
    def no_encontrado(error):
        return render_template(
            "error.html", codigo=404,
            mensaje="La página que buscas no existe."
        ), 404

    @app.errorhandler(413)
    def solicitud_demasiado_grande(error):
        return render_template(
            "error.html", codigo=413,
            mensaje="La solicitud supera el tamaño permitido."
        ), 413

    @app.errorhandler(500)
    def error_interno(error):
        return render_template(
            "error.html", codigo=500,
            mensaje="Ocurrió un error inesperado. Intenta más tarde."
        ), 500

    return app
