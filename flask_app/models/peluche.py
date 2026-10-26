import pymysql
from config.conexion_bd import obtener_conexion, ErrorBaseDatos


class Peluche:

    @staticmethod
    def crear(datos):
        conexion = None
        try:
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO peluches (nombre, descripcion, usuario_id) "
                    "VALUES (%s, %s, %s)",
                    (
                        datos["nombre"],
                        datos["descripcion"],
                        datos["usuario_id"],
                    ),
                )
            conexion.commit()
            return True
        except pymysql.MySQLError as exc:
            if conexion:
                conexion.rollback()
            raise ErrorBaseDatos("Error al crear el peluche") from exc
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def obtener_todos():
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
                return cursor.fetchall()
        except pymysql.MySQLError as exc:
            raise ErrorBaseDatos("Error al obtener los peluches") from exc
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def obtener_por_id(peluche_id):
        conexion = None
        try:
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                cursor.execute("""
                    SELECT p.id, p.nombre, p.descripcion, p.usuario_id,
                           p.adoptado, p.adoptado_por, p.visitas, p.creado_en,
                           u.nombre AS donante,
                           a.nombre AS adoptante
                    FROM peluches p
                    JOIN usuarios u ON p.usuario_id = u.id
                    LEFT JOIN usuarios a ON p.adoptado_por = a.id
                    WHERE p.id = %s
                """, (peluche_id,))
                return cursor.fetchone()
        except pymysql.MySQLError as exc:
            raise ErrorBaseDatos("Error al obtener el peluche") from exc
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def actualizar(peluche_id, datos):
        """Devuelve 'ok', 'sin_cambios', 'no_encontrado' o 'sin_permiso'."""
        conexion = None
        try:
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT usuario_id FROM peluches WHERE id = %s",
                    (peluche_id,),
                )
                fila = cursor.fetchone()
                if not fila:
                    return "no_encontrado"
                if fila["usuario_id"] != datos["usuario_id"]:
                    return "sin_permiso"

                cursor.execute(
                    "UPDATE peluches SET nombre = %s, descripcion = %s "
                    "WHERE id = %s AND usuario_id = %s",
                    (
                        datos["nombre"],
                        datos["descripcion"],
                        peluche_id,
                        datos["usuario_id"],
                    ),
                )
                conexion.commit()
                return "sin_cambios" if cursor.rowcount == 0 else "ok"
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
                    "WHERE id = %s AND adoptado = FALSE",
                    (usuario_id, peluche_id),
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
            conexion.commit()
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
