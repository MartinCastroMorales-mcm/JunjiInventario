from app import app
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

import os


# Configuramos la conexion a base de datos
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER') or 'root'
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD') or ''
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST') or 'localhost' # localhost
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB') or 'inventariofinal'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Print or log the environment variables

MYSQL_USER = app.config['MYSQL_USER'] = os.getenv('MYSQL_USER') or 'root'
MYSQL_PASSWORD = app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD') or ''
MYSQL_HOST = app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST') or 'localhost' # localhost
MYSQL_DB = app.config['MYSQL_DB'] = os.getenv('MYSQL_DB') or 'inventariofinal'

#print("MYSQL_USER:", MYSQL_USER)
#print("MYSQL_PASSWORD:", MYSQL_PASSWORD)
#print("MYSQL_HOST:", MYSQL_HOST)
#print("MYSQL_DB:", MYSQL_DB)

# A traves de mysql llamaremos a la funcion

#.connection.cursor tiene que ser en una ruta
mysql = MySQL(app)
bcrypt = Bcrypt(app)