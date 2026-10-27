from flask import abort, flash, redirect, render_template, request, session

from flask_app.config.conexion_bd import ErrorBaseDatos
from flask_app.models.peluche import Peluche


def init_peluches(app):
    @app.route("/dashboard")
    def dashboard():
        if "usuario_id" not in session:
            return redirect("/")
        try:
            peluches = Peluche.obtener_todos()
            total_donaciones = Peluche.contar_donaciones(session["usuario_id"])
            error_db = False
        except ErrorBaseDatos:
            peluches = []
            total_donaciones = None
            error_db = True
        return render_template(
            "dashboard.html", peluches=peluches,
            total_donaciones=total_donaciones, error_db=error_db
        )

    @app.route("/nueva_donacion")
    def nueva_donacion():
        if "usuario_id" not in session:
            return redirect("/")
        try:
            total_donaciones = Peluche.contar_donaciones(session["usuario_id"])
        except ErrorBaseDatos:
            total_donaciones = None
        return render_template("nueva_donacion.html", total_donaciones=total_donaciones)

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

        datos = {"nombre": nombre, "descripcion": descripcion}
        if errores:
            for error in errores:
                flash(error, "danger")
            try:
                total = Peluche.contar_donaciones(session["usuario_id"])
            except ErrorBaseDatos:
                total = None
            return render_template("nueva_donacion.html", datos=datos, total_donaciones=total)

        try:
            exito = Peluche.crear({
                "nombre": nombre,
                "descripcion": descripcion,
                "usuario_id": session["usuario_id"],
            })
            if not exito:
                raise ErrorBaseDatos("No se pudo crear el peluche")
        except ErrorBaseDatos:
            flash("No se pudo publicar el peluche. Intenta más tarde.", "danger")
            try:
                total = Peluche.contar_donaciones(session["usuario_id"])
            except ErrorBaseDatos:
                total = None
            return render_template("nueva_donacion.html", datos=datos, total_donaciones=total)

        flash("Peluche publicado exitosamente.", "success")
        return redirect("/dashboard")

    @app.route("/editar/<int:peluche_id>")
    def editar(peluche_id):
        if "usuario_id" not in session:
            return redirect("/")
        try:
            peluche = Peluche.obtener_por_id(peluche_id)
        except ErrorBaseDatos:
            flash("Servicio temporalmente no disponible.", "danger")
            return redirect("/dashboard")
        if not peluche:
            abort(404)
        if peluche.usuario_id != session["usuario_id"]:
            abort(403)
        try:
            total = Peluche.contar_donaciones(session["usuario_id"])
        except ErrorBaseDatos:
            total = None
        return render_template("editar_donacion.html", peluche=peluche, total_donaciones=total)

    @app.route("/actualizar/<int:peluche_id>", methods=["POST"])
    def actualizar(peluche_id):
        if "usuario_id" not in session:
            return redirect("/")
        try:
            peluche = Peluche.obtener_por_id(peluche_id)
        except ErrorBaseDatos:
            flash("Servicio temporalmente no disponible.", "danger")
            return redirect("/dashboard")
        if not peluche:
            abort(404)
        if peluche.usuario_id != session["usuario_id"]:
            abort(403)

        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        errores = []
        if len(nombre) < 3 or len(nombre) > 100:
            errores.append("El nombre debe tener entre 3 y 100 caracteres.")
        if len(descripcion) < 10 or len(descripcion) > 1000:
            errores.append("La descripción debe tener entre 10 y 1000 caracteres.")

        if errores:
            for error in errores:
                flash(error, "danger")
            datos_temp = {
                "id": peluche.id, "nombre": nombre, "descripcion": descripcion,
                "usuario_id": peluche.usuario_id, "adoptado": peluche.adoptado,
                "adoptado_por": peluche.adoptado_por, "visitas": peluche.visitas,
                "creado_en": peluche.creado_en, "donante": peluche.donante,
                "adoptante": peluche.adoptante,
            }
            peluche_editado = Peluche(datos_temp)
            try:
                total = Peluche.contar_donaciones(session["usuario_id"])
            except ErrorBaseDatos:
                total = None
            return render_template(
                "editar_donacion.html", peluche=peluche_editado,
                total_donaciones=total
            )

        try:
            resultado = Peluche.actualizar(peluche_id, {
                "nombre": nombre,
                "descripcion": descripcion,
                "usuario_id": session["usuario_id"],
            })
        except ErrorBaseDatos:
            flash("No se pudo actualizar el peluche.", "danger")
            return redirect(f"/editar/{peluche_id}")

        if resultado == "no_encontrado":
            abort(404)
        if resultado == "sin_permiso":
            abort(403)
        if resultado == "ok":
            flash("Peluche actualizado.", "success")
        elif resultado == "sin_cambios":
            flash("No se detectaron cambios.", "info")
        return redirect("/dashboard")

    @app.route("/detalle/<int:peluche_id>")
    def detalle(peluche_id):
        if "usuario_id" not in session:
            return redirect("/")
        try:
            peluche = Peluche.obtener_por_id(peluche_id)
        except ErrorBaseDatos:
            flash("Servicio temporalmente no disponible.", "danger")
            return redirect("/dashboard")
        if not peluche:
            abort(404)

        if peluche.usuario_id != session["usuario_id"]:
            try:
                visita_registrada = Peluche.registrar_visita(peluche_id)
                if visita_registrada:
                    peluche.visitas += 1
            except ErrorBaseDatos:
                pass

        try:
            total = Peluche.contar_donaciones(session["usuario_id"])
        except ErrorBaseDatos:
            total = None
        return render_template("detalle_peluche.html", peluche=peluche, total_donaciones=total)

    @app.route("/adoptar/<int:peluche_id>", methods=["POST"])
    def adoptar(peluche_id):
        if "usuario_id" not in session:
            return redirect("/")
        try:
            peluche = Peluche.obtener_por_id(peluche_id)
            if not peluche:
                abort(404)
            if peluche.usuario_id == session["usuario_id"]:
                abort(403)
            adoptado = Peluche.adoptar(peluche_id, session["usuario_id"])
        except ErrorBaseDatos:
            flash("No se pudo completar la adopción.", "danger")
            return redirect("/dashboard")

        if adoptado:
            flash("Has adoptado este peluche.", "success")
        else:
            flash("Este peluche ya fue adoptado o no está disponible.", "warning")
        return redirect("/dashboard")

    @app.route("/eliminar/<int:peluche_id>", methods=["POST"])
    def eliminar(peluche_id):
        if "usuario_id" not in session:
            return redirect("/")
        try:
            eliminado = Peluche.eliminar(peluche_id, session["usuario_id"])
        except ErrorBaseDatos:
            flash("No se pudo eliminar el peluche. Intenta más tarde.", "danger")
            return redirect("/dashboard")

        if eliminado:
            flash("Peluche eliminado exitosamente.", "success")
        else:
            flash("No tienes permiso para eliminar este peluche o ya no existe.", "danger")
        return redirect("/dashboard")
