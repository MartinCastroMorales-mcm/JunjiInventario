from flask import Blueprint, flash, redirect, render_template, url_for, request, session
from db import mysql
from funciones import getPerPage
from cuentas import loguear_requerido, administrador_requerido

modelo_equipo = Blueprint("modelo_equipo", __name__, template_folder="app/templates")


@modelo_equipo.route("/modelo_equipo")
@modelo_equipo.route("/modelo_equipo/<page>")
@loguear_requerido
def modeloEquipo(page=1):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    page = int(page)
    perpage = getPerPage()
    offset = (page - 1) * perpage

    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT *
    FROM modelo_equipo me
    INNER JOIN tipo_equipo te ON te.idTipo_equipo = me.idTipo_equipo
    INNER JOIN marca_equipo mae ON mae.idMarca_Equipo = me.idMarca_Equipo
                """)
    data = cur.fetchall()
    print("data")
    print(data)
    #cur.execute(
        #""" 
    #SELECT *
    #FROM modelo_equipo moe
    #INNER JOIN tipo_equipo te ON te.idTipo_equipo = moe.idTipo_equipo
    #INNER JOIN marca_tipo_equipo mte ON mte.idTipo_equipo = te.idTipo_equipo
    #INNER JOIN marca_equipo me ON me.idMarca_Equipo = mte.idMarca_Equipo
    #LIMIT {} OFFSET {} 
    #""".format(
            #perpage, offset
        #)
    #)
    #data = cur.fetchall()
    #cur.execute("SELECT * FROM marca_equipo")
    #mae_data = cur.fetchall()
    #marcas_con_tipo_equipo = None
    #for i in range(0, len(mae_data)):
        #marca = mae_data[i]
        ##añadir la tupla de tipo como elemento de la tupla de marca
        #cur.execute("""
            #SELECT te.idTipo_equipo, te.nombreTipo_equipo, observacionTipoEquipo
            #FROM marca_tipo_equipo mte
            #INNER JOIN tipo_equipo te ON te.idTipo_equipo = mte.idTipo_equipo
            #WHERE mte.idMarca_Equipo = %s
                    #""", (marca['idMarca_Equipo'],))
        #tipo_equipo_data = cur.fetchall()

        #if marcas_con_tipo_equipo == None:
            #newdict = marca
            #newdict.update({'tipo_equipo': tipo_equipo_data})
            #marcas_con_tipo_equipo = (newdict,)
        #else:
            #newdict = marca
            #newdict.update({'tipo_equipo': tipo_equipo_data})
            #marcas_con_tipo_equipo += (newdict,)
    #print("marcas_con_tipo_equipo")
    #print(marcas_con_tipo_equipo)

    cur.execute("SELECT * FROM marca_equipo")
    marca_data = cur.fetchall()
    #marca_data = ({id: x, nombre:y, valor:z})
    marca_con_tipo = []
    for i in range(0, len(marca_data)):
        marca = marca_data[i]
        cur.execute("""
        SELECT *
        FROM marca_tipo_equipo mte
        INNER JOIN tipo_equipo te ON te.idTipo_equipo = mte.idTipo_equipo
        WHERE mte.idMarca_Equipo = %s
                    """, (marca['idMarca_Equipo'],))
        tipos_asociados = cur.fetchall()
        #tipo_asociado = ({id: x, nombre: y, valor:z})

        #print('marca')
        #print(marca)
        #print('tipos_asociados')
        #print(tipos_asociados)
        nueva_marca = ingresar_elemento_a_tupla(marca, tipos_asociados, 'tipo_equipo')
        #agregar nueva marca a marca con tipo. ¿pasar de lista a tupla?
        marca_con_tipo.append(nueva_marca)

    marca_con_tipo = tuple(marca_con_tipo)
    #print("marca_con_tipo")
    #print(marca_con_tipo)


    #tiene que ser de tipo 
    #({dato_marca, ..., tipo_equipo})
        
    cur.execute("SELECT * FROM tipo_equipo")
    tipo_data = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM modelo_equipo")
    total = cur.fetchone()
    total = int(str(total).split(":")[1].split("}")[0])

    return render_template(
        "modelo_equipo.html",
        marca_equipo=marca_con_tipo,
        modelo_equipo=data,
        tipo_equipo=tipo_data,
        page=page,
        lastpage=page < (total / perpage) + 1,
    )
def ingresar_elemento_a_tupla(tupla_mayor, tupla_a_agregar, nombre_tupla_agregar):
    tupla_mayor.update({nombre_tupla_agregar: tupla_a_agregar})
    return tupla_mayor


# agregar un regisro para modelo de equipo
@modelo_equipo.route("/add_modelo_equipo", methods=["POST"])
@administrador_requerido
def add_modelo_equipo():
    if request.method == "POST":
        nombre_modelo_equipo = request.form['nombre_modelo_equipo']
        id_tipo_equipo = request.form['nombre_tipo_equipo']
        id_marca_equipo = request.form['nombre_marca_equipo']
        #print("add")
        #print(id_tipo_equipo)
        #print(nombre_modelo_equipo)
        try:
            cur = mysql.connection.cursor()
            cur.execute(
                """
            INSERT INTO modelo_equipo 
                (nombreModeloequipo, idTipo_equipo, idMarca_Equipo) 
            VALUES (%s, %s, %s)
            """,
                (nombre_modelo_equipo, id_tipo_equipo, id_marca_equipo)
            )
            cur.connection.commit()
            flash("Modelo agregado correctamente")
            return redirect(url_for("modelo_equipo.modeloEquipo"))
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for("modelo_equipo.modeloEquipo"))


# Envias datos a formulario editar
@modelo_equipo.route("/edit_modelo_equipo/<id>", methods=["POST", "GET"])
@administrador_requerido
def edit_modelo_equipo(id):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    cur = mysql.connection.cursor()
    cur.execute(
        """ 
    SELECT *
    FROM modelo_equipo moe
    LEFT OUTER JOIN tipo_equipo te ON te.idTipo_Equipo = moe.idTipo_Equipo
    LEFT OUTER JOIN marca_tipo_equipo mte ON mte.idTipo_equipo = te.idTipo_Equipo  
    LEFT OUTER JOIN marca_equipo mae on mte.idMarca_equipo = mae.idMarca_Equipo
    WHERE idModelo_Equipo = %s AND moe.idMarca_Equipo = mte.idMarca_Equipo
    """,
        (id,)
    )
    data = cur.fetchone()
    cur.execute("SELECT * FROM marca_equipo")
    mae_data = cur.fetchall()
    #print("mae_data")
    #print(mae_data)
    #print(len(mae_data))
    marcas_con_tipo_equipo = None
    for i in range(0, len(mae_data)):
        #print("marca_iterada" + str(i))
        #print(marcas_con_tipo_equipo)
        marca = mae_data[i]
        #añadir la tupla de tipo como elemento de la tupla de marca
        cur.execute("""
            SELECT te.idTipo_equipo, te.nombreTipo_equipo, observacionTipoEquipo
            FROM marca_tipo_equipo mte
            INNER JOIN tipo_equipo te ON te.idTipo_equipo = mte.idTipo_equipo
            WHERE mte.idMarca_Equipo = %s
                    """, (marca['idMarca_Equipo'],))
        tipo_equipo_data = cur.fetchall()

        if marcas_con_tipo_equipo == None:
            newdict = marca
            newdict.update({'tipo_equipo': tipo_equipo_data})
            marcas_con_tipo_equipo = (newdict,)
        else:
            newdict = marca
            newdict.update({'tipo_equipo': tipo_equipo_data})
            marcas_con_tipo_equipo += (newdict,)
        
    cur.close()
    curs = mysql.connection.cursor()
    curs.execute("SELECT * FROM tipo_equipo")
    tipo_data = curs.fetchall()
    curs.close()
    return render_template(
        "editModelo_equipo.html", modelo_equipo=data, id=id,
        marca_equipo=marcas_con_tipo_equipo, tipo_equipo=tipo_data)


# actualizar
@modelo_equipo.route("/update_modelo_equipo/<id>", methods=["POST"])
@administrador_requerido
def update_modelo_equipo(id):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    if request.method == "POST":
        nombre_modelo_equipo = request.form["nombre_modelo_equipo"]
        nombre_tipo_equipo = request.form["nombre_tipo_equipo"]
        idMarca_Equipo = request.form['nombre_marca_equipo']
        print("marca")
        print(idMarca_Equipo)
        print("nombre tipo equipo")
        print(nombre_tipo_equipo)
        try:
            cur = mysql.connection.cursor()
            cur.execute(
                """
            UPDATE modelo_equipo 
            SET nombreModeloequipo = %s,
                idTipo_Equipo = %s,
                idMarca_Equipo = %s
            WHERE idModelo_Equipo = %s
            """,
                (nombre_modelo_equipo, nombre_tipo_equipo, idMarca_Equipo, id),
            )
            print('id')
            print(id)
            mysql.connection.commit()
            flash("Modelo actualizado correctamente")
            return redirect(url_for("modelo_equipo.modeloEquipo"))
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for("modelo_equipo.modeloEquipo"))


# eliminar
@modelo_equipo.route("/delete_modelo_equipo/<id>", methods=["POST", "GET"])
@administrador_requerido
def delete_modelo_equipo(id):
    if "user" not in session:
        flash("you are NOT authorized")
        return redirect("/ingresar")
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM modelo_equipo WHERE idModelo_Equipo = %s", (id,))
        mysql.connection.commit()
        flash("Modelo eliminado correctamente")
        return redirect(url_for("modelo_equipo.modeloEquipo"))
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for("modelo_equipo.modeloEquipo"))
