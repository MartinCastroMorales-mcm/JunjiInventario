from flask import Blueprint, flash, redirect, render_template, url_for, request
from db import mysql
from funciones import getPerPage

modelo_equipo = Blueprint("modelo_equipo", __name__, template_folder="app/templates")


@modelo_equipo.route("/modelo_equipo")
@modelo_equipo.route("/modelo_equipo/<page>")
def modeloEquipo(page=1):
    page = int(page)
    perpage = getPerPage()
    offset = (page - 1) * perpage

    cur = mysql.connection.cursor()
    cur.execute(
        """ 
    SELECT *
    FROM modelo_equipo moe
    LEFT OUTER JOIN tipo_equipo te on moe.idTipo_equipo = te.idTipo_equipo
    LEFT OUTER JOIN marca_equipo mae on te.idMarca_equipo = mae.idMarca_equipo
    LIMIT {} OFFSET {} 
    """.format(
            perpage, offset
        )
    )
    data = cur.fetchall()
    cur.execute("SELECT * FROM marca_equipo")
    mae_data = cur.fetchall()
    cur.execute("SELECT * FROM tipo_equipo")
    tipo_data = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM modelo_equipo")
    total = cur.fetchone()
    total = int(str(total).split(":")[1].split("}")[0])
    return render_template(
        "modelo_equipo.html",
        modelo_equipo=data,
        tipo_equipo=tipo_data,
        marca_equipo=mae_data,
        page=page,
        lastpage=page < (total / perpage) + 1,
    )


# agregar un regisro para modelo de equipo
@modelo_equipo.route("/add_modelo_equipo", methods=["POST"])
def add_modelo_equipo():
    if request.method == "POST":
        nombre_modelo_equipo = request.form["nombre_modelo_equipo"]
        nombre_marca_equipo = request.form["nombre_marca_equipo"]
        try:
            cur = mysql.connection.cursor()
            cur.execute(
                """
            INSERT INTO modelo_equipo (nombreModeloequipo, idMarca_equipo) VALUES (%s,%s)
            """,
                (nombre_modelo_equipo, nombre_marca_equipo),
            )
            cur.connection.commit()
            flash("Modelo agregado correctamente")
            return redirect(url_for("modelo_equipo.modeloEquipo"))
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for("modelo_equipo.modeloEquipo"))


# Envias datos a formulario editar
@modelo_equipo.route("/edit_modelo_equipo/<id>", methods=["POST", "GET"])
def edit_modelo_equipo(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            """ 
        SELECT moe.idModelo_Equipo, moe.nombreModeloequipo, mae.idMarca_Equipo,
        mae.nombreMarcaEquipo, te.idTipo_equipo, te.nombreTipo_equipo
        FROM modelo_equipo moe
        LEFT OUTER JOIN tipo_equipo te ON te.idTipo_Equipo = moe.idTipo_Equipo
        LEFT OUTER JOIN marca_equipo mae on te.idMarca_equipo = mae.idMarca_Equipo
        WHERE idModelo_Equipo = %s
        """,
            (id,),
        )
        data = cur.fetchall()
        #print("#####################")
        print(data)
        #print("$$$$$$$$$$$$$$$$$")
        cur.close()
        curs = mysql.connection.cursor()
        curs.execute("SELECT * FROM marca_equipo")
        mae_data = curs.fetchall()
        #print(mae_data)
        #print("&&&&&&&&&&&&&&&&&&&&&&&")
        cur.close()
        curs.execute("SELECT * FROM tipo_equipo")
        tipo_data = curs.fetchall()
        #print(tipo_data)
        #print("00000000000000000000000")
        curs.close()
        return render_template(
            "editModelo_equipo.html", modelo_equipo=data[0], 
            marca_equipo=mae_data, tipo_equipo=tipo_data)
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for("modelo_equipo.modeloEquipo"))


# actualizar
@modelo_equipo.route("/update_modelo_equipo/<id>", methods=["POST"])
def update_modelo_equipo(id):
    if request.method == "POST":
        nombre_modelo_equipo = request.form["nombre_modelo_equipo"]
        nombre_tipo_equipo = request.form["nombre_tipo_equipo"]
        try:
            cur = mysql.connection.cursor()
            cur.execute(
                """
            UPDATE modelo_equipo 
            SET nombreModeloequipo = %s,
                idTipo_Equipo = %s
            WHERE idModelo_Equipo = %s
            """,
                (nombre_modelo_equipo, nombre_tipo_equipo, id),
            )
            mysql.connection.commit()
            flash("Modelo actualizado correctamente")
            return redirect(url_for("modelo_equipo.modeloEquipo"))
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for("modelo_equipo.modeloEquipo"))


# eliminar
@modelo_equipo.route("/delete_modelo_equipo/<id>", methods=["POST", "GET"])
def delete_modelo_equipo(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM modelo_equipo WHERE idModelo_Equipo = %s", (id,))
        mysql.connection.commit()
        flash("Modelo eliminado correctamente")
        return redirect(url_for("modelo_equipo.modeloEquipo"))
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for("modelo_equipo.modeloEquipo"))
