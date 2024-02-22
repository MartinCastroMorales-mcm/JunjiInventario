from flask import Blueprint, render_template, request, url_for, redirect, flash
from db import mysql

traslado = Blueprint("traslado", __name__, template_folder="app/templates")


@traslado.route("/traslado")
def Traslado():
    cur = mysql.connection.cursor()
    cur.execute(
        """
                SELECT t.idTraslado, t.fechatraslado, t.rutadocumentoTraslado, 
                    origen.nombreUnidad as nombreOrigen, destino.nombreUnidad as nombreDestino
                FROM traslado t
                INNER JOIN unidad origen on origen.idUnidad = t.idUnidadOrigen
                INNER JOIN unidad destino on destino.idUnidad = t.idUnidadDestino
        """
    )
    data = cur.fetchall()

    return render_template("traslado.html", traslado=data)


@traslado.route("/try_add_traslado")
def try_add_traslado():
    cur = mysql.connection.cursor()
    cur.execute(
        """
                SELECT t.idTraslado, t.fechatraslado, t.rutadocumentoTraslado, 
                    origen.nombreUnidad as nombreOrigen, destino.nombreUnidad as nombreDestino
                FROM traslado t
                INNER JOIN unidad origen on origen.idUnidad = t.idUnidadOrigen
                INNER JOIN unidad destino on destino.idUnidad = t.idUnidadDestino
        """
    )

    data = cur.fetchall()
    cur.execute(
        """
        SELECT * 
        FROM unidad u
        ORDER BY u.nombreUnidad
                 """
    )
    unidades = cur.fetchall()
    cur.execute(
        """
        SELECT * 
        FROM equipo e
        ORDER BY e.idEquipo
                 """
    )
    equipos = cur.fetchall()

    return render_template("traslado.html", traslado=data, agregar=True, unidades=unidades, equipo= equipos)

@traslado.route("/traslado/add_traslado", methods=["GET", "POST"])
def add_traslado():
    if request.method == 'POST':

        Origen = int(request.form['Origen'])
        print(Origen)
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT *
                FROM equipo e
                INNER JOIN unidad u on u.idUnidad = e.idUnidad
                INNER JOIN tipo_equipo te on te.idTipo_equipo = e.idTipo_equipo
                WHERE e.idUnidad = %s
            
                        
                        """, (Origen,))
                    
            equipo = cur.fetchall()
            cur.execute(
                """
                SELECT * 
                FROM unidad u
                ORDER BY u.nombreUnidad
                        """
            )
            print("equipos: ")
            print(equipo)
            unidades = cur.fetchall()
            if len(equipo) == 0:
                equipo = []
                flash("no hay equipos en esta Unidad")
                return redirect(url_for('traslado.Traslado'))
            return render_template("add_traslado.html", equipo=equipo, unidades=unidades)

        except Exception as e:
            flash(e.args[1])
            return redirect(url_for('traslado.Traslado'))

@traslado.route("/traslado/edit_traslado/<id>", methods=["POST", "GET"])
def edit_traslado(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute(
        """
                SELECT t.idTraslado, origen.idUnidad as idUnidadOrigen, destino.idUnidad as idUnidadDestino,
                    t.fechatraslado, t.rutadocumentoTraslado,
                    origen.nombreUnidad as nombreOrigen, destino.nombreUnidad as nombreDestino
                FROM traslado t 
                INNER JOIN unidad origen on origen.idUnidad = t.idUnidadOrigen
                INNER JOIN unidad destino on destino.idUnidad = t.idUnidadDestino
                WHERE t.idTraslado = %s
        """, (id,)
        )
        data = cur.fetchall()
        cur.execute(
            """
            SELECT * 
            FROM unidad u
            ORDER BY u.nombreUnidad
                    """
        )
        unidades = cur.fetchall()
        cur.execute(
            """
            SELECT * 
            FROM equipo e
            INNER JOIN tipo_equipo te on te.idTipo_equipo = e.idTipo_equipo
            ORDER BY e.idEquipo
                    """
        )
        equipos = cur.fetchall()
        return render_template('editTraslado.html', traslado=data[0], agregar=True, unidades=unidades, equipo= equipos)

    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('traslado.Traslado'))

@traslado.route("/traslado/delete_traslado/<id>", methods = ["POST", "GET"])
def delete_traslado(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM traslado WHERE idTraslado = %s', (id,))
        mysql.connection.commit()
        flash('Traslado eliminado correctamente')
        return redirect(url_for('traslado.Traslado'))
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('traslado.Traslado'))

@traslado.route("/traslado/create_traslado/<origen>", methods=["POST"])
def create_traslado(origen):
    if request.method == "POST":
        fechatraslado = request.form['fechatraslado']
        #rutadocumento = request.form['']
        Destino = request.form['Destino']
        Origen = origen
        #trasladar[] es la notacion para obtener un array con todos los outputs de las checklist
        equipos = request.form.getlist('trasladar[]')

        #Añadir fila a traslado
        cur = mysql.connection.cursor()
        cur.execute("""
                    INSERT INTO traslado (
                        fechatraslado,
                        rutadocumentoTraslado,
                        idUnidadDestino,
                        idUnidadOrigen
                    )
                    VALUES (%s, %s, %s, %s)
                    """, (fechatraslado, 'ruta', Destino, Origen), )
        mysql.connection.commit()
        #Encontrar la id de traslado
        trasladoid = cur.lastrowid
        #Añadir las traslaciones para asociar multiples equipos al traslado
        print("equipos:")
        print(len(equipos))
        flash(equipos)
        for idEquipo in equipos:
            print(idEquipo)
            cur.execute("""
                        INSERT INTO traslacion (
                            idTraslado,
                            idEquipo
                        )
                        VALUES (%s, %s)
                       """, (str(trasladoid), idEquipo))
            mysql.connection.commit()
            cur.execute("""
                        UPDATE equipo
                        SET idUnidad = %s
                        WHERE equipo.idEquipo = %s
                        """, (Destino, idEquipo))
            mysql.connection.commit()
        
        flash("traslado agregado correctamente")
        return redirect(url_for('traslado.Traslado'))
    return redirect(url_for('traslado.Traslado'))
