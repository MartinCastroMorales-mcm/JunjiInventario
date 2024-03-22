from flask import Blueprint, render_template, request, url_for, redirect, flash, make_response, send_file
from db import mysql
from funciones import getPerPage
import bcrypt

cuentas = Blueprint("cuentas", __name__, template_folder="app/templates")

@cuentas.route("/ingresar")
def Ingresar():
    return render_template("login.html")

@cuentas.route("/registrar", methods=["GET", "POST"])
def registrar():
    return render_template("register.html")

@cuentas.route("/crear_cuenta", methods=["GET", "POST"])
def crear_cuenta():
    nombreUsuario = request.form['nombreUsuario']
    contraseña = request.form['contraseña']
    #agregar el resto de elementos
    
    #añadir sal (ayuda a hacer el hash mas seguro)
    salt = bcrypt.gensalt()
    #Encriptar contraseña
    contraseñaHasheda = bcrypt.hashpw(contraseña, salt)

    #subir datos a la base de datos
    cur = mysql.connection.cursor()
    cur.execute("""

                """)
    mysql.connection.commit()
    return redirect("/")