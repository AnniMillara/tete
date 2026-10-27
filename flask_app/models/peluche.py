import pymysql

from flask_app.config.conexion_bd import ErrorBaseDatos, obtener_conexion


class Peluche:
    # Convierte los datos de una fila en un objeto Peluche.
    def __init__(self, data):
        self.id = data.get("id")
        self.nombre = data.get("nombre")
        self.descripcion = data.get("descripcion")
        self.usuario_id = data.get("usuario_id")
        self.adoptado = data.get("adoptado", False)
        self.adoptado_por = data.get("adoptado_por")
        self.visitas = data.get("visitas", 0)
        self.creado_en = data.get("creado_en")
        self.donante = data.get("donante")
        self.adoptante = data.get("adoptante")

    @staticmethod
    def crear(datos):
        conexion = None
        try:
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO peluches (nombre, descripcion, usuario_id) VALUES (%s, %s, %s)",
                    (datos["nombre"], datos["descripcion"], datos["usuario_id"]),
                )
                insertado = cursor.rowcount == 1
            if not insertado:
                conexion.rollback()
                return False
            conexion.commit()
            return True
        except pymysql.MySQLError as exc:
            if conexion:
                conexion.rollback()
            raise ErrorBaseDatos("Error al crear el peluche") from exc
        finally:
            if conexion:
                conexion.close()

    @classmethod
    def obtener_todos(cls):
        conexion = None
        try:
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                cursor.execute("""
                    SELECT p.id, p.nombre, p.descripcion, p.usuario_id,
                           p.adoptado, p.adoptado_por, p.visitas, p.creado_en,
                           u.nombre AS donante
                    FROM peluches p
                    JOIN usuarios u ON p.usuario_id = u.id
                    ORDER BY p.creado_en DESC
                """)
                return [cls(fila) for fila in cursor.fetchall()]
        except pymysql.MySQLError as exc:
            raise ErrorBaseDatos("Error al obtener los peluches") from exc
        finally:
            if conexion:
                conexion.close()

    @classmethod
    def obtener_por_id(cls, peluche_id):
        conexion = None
        try:
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                cursor.execute("""
                    SELECT p.id, p.nombre, p.descripcion, p.usuario_id,
                           p.adoptado, p.adoptado_por, p.visitas, p.creado_en,
                           u.nombre AS donante, a.nombre AS adoptante
                    FROM peluches p
                    JOIN usuarios u ON p.usuario_id = u.id
                    LEFT JOIN usuarios a ON p.adoptado_por = a.id
                    WHERE p.id = %s
                """, (peluche_id,))
                fila = cursor.fetchone()
                return cls(fila) if fila else None
        except pymysql.MySQLError as exc:
            raise ErrorBaseDatos("Error al obtener el peluche") from exc
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def actualizar(peluche_id, datos):
        conexion = None
        try:
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                cursor.execute("SELECT usuario_id FROM peluches WHERE id = %s", (peluche_id,))
                fila = cursor.fetchone()
                if not fila:
                    return "no_encontrado"
                if fila["usuario_id"] != datos["usuario_id"]:
                    return "sin_permiso"

                cursor.execute(
                    "UPDATE peluches SET nombre = %s, descripcion = %s "
                    "WHERE id = %s AND usuario_id = %s",
                    (datos["nombre"], datos["descripcion"], peluche_id, datos["usuario_id"]),
                )
                filas_modificadas = cursor.rowcount
                conexion.commit()
                return "sin_cambios" if filas_modificadas == 0 else "ok"
        except pymysql.MySQLError as exc:
            if conexion:
                conexion.rollback()
            raise ErrorBaseDatos("Error al actualizar el peluche") from exc
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def adoptar(peluche_id, usuario_id):
        conexion = None
        try:
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                cursor.execute(
                    "UPDATE peluches SET adoptado = TRUE, adoptado_por = %s "
                    "WHERE id = %s AND adoptado = FALSE AND usuario_id <> %s",
                    (usuario_id, peluche_id, usuario_id),
                )
                conexion.commit()
                return cursor.rowcount > 0
        except pymysql.MySQLError as exc:
            if conexion:
                conexion.rollback()
            raise ErrorBaseDatos("Error al adoptar el peluche") from exc
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def registrar_visita(peluche_id):
        conexion = None
        try:
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                cursor.execute(
                    "UPDATE peluches SET visitas = visitas + 1 WHERE id = %s",
                    (peluche_id,),
                )
                actualizada = cursor.rowcount == 1
            conexion.commit()
            return actualizada
        except pymysql.MySQLError as exc:
            if conexion:
                conexion.rollback()
            raise ErrorBaseDatos("Error al registrar la visita") from exc
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def contar_donaciones(usuario_id):
        conexion = None
        try:
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) AS total FROM peluches WHERE usuario_id = %s",
                    (usuario_id,),
                )
                fila = cursor.fetchone()
                return fila["total"] if fila else 0
        except pymysql.MySQLError as exc:
            raise ErrorBaseDatos("Error al contar las donaciones") from exc
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def eliminar(peluche_id, usuario_id):
        conexion = None
        try:
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM peluches WHERE id = %s AND usuario_id = %s",
                    (peluche_id, usuario_id),
                )
                eliminado = cursor.rowcount > 0
            conexion.commit()
            return eliminado
        except pymysql.MySQLError as exc:
            if conexion:
                conexion.rollback()
            raise ErrorBaseDatos("Error al eliminar el peluche") from exc
        finally:
            if conexion:
                conexion.close()
