from flask import Blueprint, render_template, request
from db import mysql
buscar = Blueprint("buscar", __name__, template_folder="app/templates")

@buscar.route("/buscar", methods=["GET", "POST"])
def Buscar():
    busqueda_data = request.args.get('busqueda') 

    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT e.Cod_inventarioEquipo as clave,
            e.Num_serieEquipo as nombre,
            e.idEquipo as id, "equipo" as tipo
    FROM equipo e
    UNION
    SELECT f.rutFuncionario, f.nombreFuncionario, f.rutFuncionario,
                "funcionario"
    FROM funcionario f
    UNION
    SELECT u.direccionUnidad, u.nombreUnidad, u.idUnidad, "unidad"
    FROM unidad u
                """)
    items_data = cur.fetchall()

    return render_template("buscar.html", busqueda=busqueda_data, 
                items=items_data)