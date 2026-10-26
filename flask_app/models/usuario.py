import pymysql
from config.conexion_bd import obtener_conexion, ErrorBaseDatos


class Usuario:

    @staticmethod
    def crear(datos):
        conexion = None
        try:
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO usuarios (nombre, apellido, email, password) "
                    "VALUES (%s, %s, %s, %s)",
                    (
                        datos["nombre"],
                        datos["apellido"],
                        datos["email"],
                        datos["password"],
                    ),
                )
            conexion.commit()
            return True, None
        except pymysql.err.IntegrityError:
            if conexion:
                conexion.rollback()
            return False, "El correo ya está registrado."
        except pymysql.MySQLError as exc:
            if conexion:
                conexion.rollback()
            raise ErrorBaseDatos("Error al crear el usuario") from exc
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def buscar_por_email(email):
        conexion = None
        try:
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM usuarios WHERE email = %s", (email,)
                )
                return cursor.fetchone()
        except pymysql.MySQLError as exc:
            raise ErrorBaseDatos("Error al buscar el usuario") from exc
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def buscar_por_id(usuario_id):
        conexion = None
        try:
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT id, nombre, apellido FROM usuarios WHERE id = %s",
                    (usuario_id,),
                )
                return cursor.fetchone()
        except pymysql.MySQLError as exc:
            raise ErrorBaseDatos("Error al buscar el usuario") from exc
        finally:
            if conexion:
                conexion.close()
