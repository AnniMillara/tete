import pymysql

from flask_app.config.conexion_bd import ErrorBaseDatos, obtener_conexion


class Usuario:
    # Convierte los datos de una fila en un objeto Usuario.
    def __init__(self, data):
        self.id = data.get("id")
        self.nombre = data.get("nombre")
        self.apellido = data.get("apellido")
        self.email = data.get("email")
        self.password = data.get("password")
        self.creado_en = data.get("creado_en")

    @staticmethod
    def crear(datos):
        conexion = None
        try:
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO usuarios (nombre, apellido, email, password) "
                    "VALUES (%s, %s, %s, %s)",
                    (datos["nombre"], datos["apellido"], datos["email"], datos["password"]),
                )
                insertado = cursor.rowcount == 1
            if not insertado:
                conexion.rollback()
                return False, "No se pudo crear la cuenta. Intenta nuevamente."
            conexion.commit()
            return True, None
        except pymysql.err.IntegrityError as exc:
            if conexion:
                conexion.rollback()
            if exc.args and exc.args[0] == 1062:
                return False, "El correo ya está registrado."
            raise ErrorBaseDatos("Error de integridad al crear el usuario") from exc
        except pymysql.MySQLError as exc:
            if conexion:
                conexion.rollback()
            raise ErrorBaseDatos("Error al crear el usuario") from exc
        finally:
            if conexion:
                conexion.close()

    @classmethod
    def buscar_por_email(cls, email):
        conexion = None
        try:
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
                fila = cursor.fetchone()
                return cls(fila) if fila else None
        except pymysql.MySQLError as exc:
            raise ErrorBaseDatos("Error al buscar el usuario") from exc
        finally:
            if conexion:
                conexion.close()
