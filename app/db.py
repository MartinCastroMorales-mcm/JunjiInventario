from app import app
from flask_mysqldb import MySQL
from dotenv import load_dotenv

import os

load_dotenv()  

# Configuramos la conexion a base de datosx
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER') or 'root'
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD') or ''
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST') or 'localhost' # localhost
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB') or 'inventariofinal'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# A traves de mysql llamaremos a la funcion
mysql = MySQL(app)