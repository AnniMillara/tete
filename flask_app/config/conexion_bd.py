import os
import pymysql
from dotenv import load_dotenv

load_dotenv()


class ErrorBaseDatos(Exception):
    """Fallo controlado de conexión o consulta a MySQL."""


def obtener_conexion():
    try:
        return pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME", "nido_peluches"),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
            connect_timeout=5,
        )
    except (pymysql.MySQLError, TypeError, ValueError) as exc:
        raise ErrorBaseDatos("No se pudo conectar a la base de datos") from exc
