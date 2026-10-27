import re

from flask import flash, redirect, render_template, request, session

from flask_app.config import bcrypt
from flask_app.config.conexion_bd import ErrorBaseDatos
from flask_app.models.usuario import Usuario

PATRON_EMAIL = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
MAX_BYTES_PASSWORD = 72


def _password_es_valida(password):
    if not password:
        return False, "La contraseña es obligatoria."
    if len(password.encode("utf-8")) > MAX_BYTES_PASSWORD:
        return False, "La contraseña no puede superar los 72 bytes (límite de Bcrypt)."
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres."
    return True, None


def init_usuarios(app):
    @app.route("/")
    def index():
        if "usuario_id" in session:
            return redirect("/dashboard")
        return render_template("index.html")

    @app.route("/registro", methods=["POST"])
    def registrar():
        nombre = request.form.get("nombre", "").strip()
        apellido = request.form.get("apellido", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirmar = request.form.get("confirmar", "")

        errores = []
        if len(nombre) < 2 or len(nombre) > 50:
            errores.append("El nombre debe tener entre 2 y 50 caracteres.")
        if len(apellido) < 2 or len(apellido) > 50:
            errores.append("El apellido debe tener entre 2 y 50 caracteres.")
        if len(email) > 100 or not PATRON_EMAIL.fullmatch(email):
            errores.append("El correo electrónico no es válido.")

        ok_pw, msg_pw = _password_es_valida(password)
        if not ok_pw:
            errores.append(msg_pw)
        elif password != confirmar:
            errores.append("Las contraseñas no coinciden.")

        datos_form = {"nombre": nombre, "apellido": apellido, "email": email}
        if errores:
            for error in errores:
                flash(error, "danger")
            return render_template("index.html", reg_data=datos_form)

        hash_pw = bcrypt.generate_password_hash(password).decode("utf-8")
        try:
            exito, mensaje = Usuario.crear({
                "nombre": nombre,
                "apellido": apellido,
                "email": email,
                "password": hash_pw,
            })
        except ErrorBaseDatos:
            flash("Servicio temporalmente no disponible. Intenta más tarde.", "danger")
            return render_template("index.html", reg_data=datos_form)

        if exito:
            flash("Registro exitoso. Ya puedes iniciar sesión.", "success")
            return redirect("/")

        flash(mensaje, "danger")
        return render_template("index.html", reg_data=datos_form)

    @app.route("/login", methods=["POST"])
    def login():
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Debes ingresar correo y contraseña.", "danger")
            return render_template("index.html", login_email=email)

        if len(email) > 100 or not PATRON_EMAIL.fullmatch(email):
            flash("Credenciales incorrectas.", "danger")
            return render_template("index.html", login_email=email)

        if len(password.encode("utf-8")) > MAX_BYTES_PASSWORD:
            flash("Credenciales incorrectas.", "danger")
            return render_template("index.html", login_email=email)

        try:
            usuario = Usuario.buscar_por_email(email)
        except ErrorBaseDatos:
            flash("Servicio temporalmente no disponible. Intenta más tarde.", "danger")
            return render_template("index.html", login_email=email)

        if usuario and usuario.password and bcrypt.check_password_hash(usuario.password, password):
            session.clear()
            session["usuario_id"] = usuario.id
            session["usuario_nombre"] = usuario.nombre
            return redirect("/dashboard")

        flash("Credenciales incorrectas.", "danger")
        return render_template("index.html", login_email=email)

    @app.route("/logout", methods=["POST"])
    def logout():
        session.clear()
        return redirect("/")
