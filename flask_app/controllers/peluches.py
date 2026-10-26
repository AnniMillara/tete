from flask import render_template, request, redirect, session, flash, abort
from flask_app.models.peluche import Peluche
from config.conexion_bd import ErrorBaseDatos


def init_peluches(app):

    @app.route("/dashboard")
    def dashboard():
        if "usuario_id" not in session:
            return redirect("/")
        try:
            peluches = Peluche.obtener_todos()
            total_donaciones = Peluche.contar_donaciones(session["usuario_id"])
        except ErrorBaseDatos:
            flash("Servicio temporalmente no disponible. Intenta más tarde.", "danger")
            return render_template("dashboard.html", peluches=[], total_donaciones=0)
        return render_template(
            "dashboard.html",
            peluches=peluches,
            total_donaciones=total_donaciones,
        )

    @app.route("/nueva_donacion")
    def nueva_donacion():
        if "usuario_id" not in session:
            return redirect("/")
        try:
            total_donaciones = Peluche.contar_donaciones(session["usuario_id"])
        except ErrorBaseDatos:
            flash("Servicio temporalmente no disponible. Intenta más tarde.", "danger")
            total_donaciones = 0
        return render_template(
            "nueva_donacion.html", total_donaciones=total_donaciones
        )

    @app.route("/crear_peluche", methods=["POST"])
    def crear_peluche():
        if "usuario_id" not in session:
            return redirect("/")
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()

        errores = []
        if len(nombre) < 3 or len(nombre) > 100:
            errores.append("El nombre debe tener entre 3 y 100 caracteres.")
        if len(descripcion) < 10 or len(descripcion) > 1000:
            errores.append("La descripción debe tener entre 10 y 1000 caracteres.")

        if errores:
            for e in errores:
                flash(e, "danger")
            try:
                total_donaciones = Peluche.contar_donaciones(session["usuario_id"])
            except ErrorBaseDatos:
                total_donaciones = 0
            return render_template(
                "nueva_donacion.html",
                datos={"nombre": nombre, "descripcion": descripcion},
                total_donaciones=total_donaciones,
            )

        try:
            Peluche.crear({
                "nombre": nombre,
                "descripcion": descripcion,
                "usuario_id": session["usuario_id"],
            })
        except ErrorBaseDatos:
            flash("No se pudo publicar el peluche. Intenta más tarde.", "danger")
            try:
                total_donaciones = Peluche.contar_donaciones(session["usuario_id"])
            except ErrorBaseDatos:
                total_donaciones = 0
            return render_template(
                "nueva_donacion.html",
                datos={"nombre": nombre, "descripcion": descripcion},
                total_donaciones=total_donaciones,
            )

        flash("Peluche publicado exitosamente.", "success")
        return redirect("/dashboard")

    @app.route("/editar/<int:peluche_id>")
    def editar(peluche_id):
        if "usuario_id" not in session:
            return redirect("/")
        try:
            peluche = Peluche.obtener_por_id(peluche_id)
            total_donaciones = Peluche.contar_donaciones(session["usuario_id"])
        except ErrorBaseDatos:
            flash("Servicio temporalmente no disponible. Intenta más tarde.", "danger")
            return redirect("/dashboard")
        if not peluche:
            abort(404)
        if peluche["usuario_id"] != session["usuario_id"]:
            abort(403)
        return render_template(
            "editar_donacion.html",
            peluche=peluche,
            total_donaciones=total_donaciones,
        )

    @app.route("/actualizar/<int:peluche_id>", methods=["POST"])
    def actualizar(peluche_id):
        if "usuario_id" not in session:
            return redirect("/")
        try:
            peluche = Peluche.obtener_por_id(peluche_id)
        except ErrorBaseDatos:
            flash("Servicio temporalmente no disponible. Intenta más tarde.", "danger")
            return redirect("/dashboard")
        if not peluche:
            abort(404)
        if peluche["usuario_id"] != session["usuario_id"]:
            abort(403)

        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()

        errores = []
        if len(nombre) < 3 or len(nombre) > 100:
            errores.append("El nombre debe tener entre 3 y 100 caracteres.")
        if len(descripcion) < 10 or len(descripcion) > 1000:
            errores.append("La descripción debe tener entre 10 y 1000 caracteres.")

        if errores:
            for e in errores:
                flash(e, "danger")
            try:
                total_donaciones = Peluche.contar_donaciones(session["usuario_id"])
            except ErrorBaseDatos:
                total_donaciones = 0
            peluche_editado = dict(peluche)
            peluche_editado["nombre"] = nombre
            peluche_editado["descripcion"] = descripcion
            return render_template(
                "editar_donacion.html",
                peluche=peluche_editado,
                total_donaciones=total_donaciones,
            )

        try:
            resultado = Peluche.actualizar(peluche_id, {
                "nombre": nombre,
                "descripcion": descripcion,
                "usuario_id": session["usuario_id"],
            })
        except ErrorBaseDatos:
            flash("No se pudo actualizar el peluche. Intenta más tarde.", "danger")
            try:
                total_donaciones = Peluche.contar_donaciones(session["usuario_id"])
            except ErrorBaseDatos:
                total_donaciones = 0
            peluche_editado = dict(peluche)
            peluche_editado["nombre"] = nombre
            peluche_editado["descripcion"] = descripcion
            return render_template(
                "editar_donacion.html",
                peluche=peluche_editado,
                total_donaciones=total_donaciones,
            )

        if resultado == "ok":
            flash("Peluche actualizado.", "success")
        elif resultado == "sin_cambios":
            flash("No se detectaron cambios.", "info")
        elif resultado == "no_encontrado":
            abort(404)
        elif resultado == "sin_permiso":
            abort(403)
        return redirect("/dashboard")

    @app.route("/detalle/<int:peluche_id>")
    def detalle(peluche_id):
        if "usuario_id" not in session:
            return redirect("/")
        try:
            peluche = Peluche.obtener_por_id(peluche_id)
            total_donaciones = Peluche.contar_donaciones(session["usuario_id"])
        except ErrorBaseDatos:
            flash("Servicio temporalmente no disponible. Intenta más tarde.", "danger")
            return redirect("/dashboard")
        if not peluche:
            abort(404)

        # Bonus: visitas no cuentan al donante
        if peluche["usuario_id"] != session["usuario_id"]:
            try:
                Peluche.registrar_visita(peluche_id)
                peluche["visitas"] += 1
            except ErrorBaseDatos:
                pass

        return render_template(
            "detalle_peluche.html",
            peluche=peluche,
            total_donaciones=total_donaciones,
        )

    @app.route("/adoptar/<int:peluche_id>", methods=["POST"])
    def adoptar(peluche_id):
        if "usuario_id" not in session:
            return redirect("/")
        try:
            peluche = Peluche.obtener_por_id(peluche_id)
        except ErrorBaseDatos:
            flash("Servicio temporalmente no disponible. Intenta más tarde.", "danger")
            return redirect("/dashboard")
        if not peluche:
            abort(404)
        if peluche["usuario_id"] == session["usuario_id"]:
            abort(403)

        try:
            adoptado = Peluche.adoptar(peluche_id, session["usuario_id"])
        except ErrorBaseDatos:
            flash("No se pudo completar la adopción. Intenta más tarde.", "danger")
            return redirect("/dashboard")

        if adoptado:
            flash("Has adoptado este peluche.", "success")
        else:
            flash("Este peluche ya fue adoptado.", "warning")
        return redirect("/dashboard")
