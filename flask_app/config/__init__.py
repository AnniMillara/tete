from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect

# Instancias globales para las extensiones
bcrypt = Bcrypt()
csrf = CSRFProtect()
