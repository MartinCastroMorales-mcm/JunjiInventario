from flask import Blueprint, render_template, request, url_for, redirect, flash
from db import mysql

asignacion = Blueprint("asignacion", __name__, template_folder="app/templates")


@asignacion.route("/asignacion")
def Asignacion():
    cur = mysql.connection.cursor()
    cur.execute(
        """ 
    SELECT  
    	te.nombreidTipoequipo,
        a.fecha_inicioAsignacion,
        a.observacionAsignacion,
        a.rutaactaAsignacion,
        f.nombreFuncionario,
        d.fechaDevolucion
    FROM asignacion a
    INNER JOIN funcionario f on a.rutFuncionario = f.rutFuncionario
    INNER JOIN equipo eq on a.idEquipo = eq.idEquipo
    INNER JOIN tipo_equipo te on eq.idTipo_Equipo = te.idTipo_equipo 
    INNER JOIN devolucion d on a.idDevolucion = d.idDevolucion
    """
    )
    data = cur.fetchall()
    return render_template(
        "asignacion.html", asignacion=data, agregar=False, tiposEquipos=None
    )


@asignacion.route("/try_add_asignacion")
def try_add_asignacion():
    cur = mysql.connection.cursor()
    cur.execute(
        """ 
    SELECT  
    	te.nombreidTipoequipo,
        a.fecha_inicioAsignacion,
        a.observacionAsignacion,
        a.rutaactaAsignacion,
        f.nombreFuncionario,
        d.fechaDevolucion
    FROM asignacion a
    INNER JOIN funcionario f on a.rutFuncionario = f.rutFuncionario
    INNER JOIN equipo eq on a.idEquipo = eq.idEquipo
    INNER JOIN tipo_equipo te on eq.idTipo_Equipo = te.idTipo_equipo 
    INNER JOIN devolucion d on a.idDevolucion = d.idDevolucion
    """
    )

    data = cur.fetchall()
    cur.execute(
        """
        SELECT * 
        FROM tipo_equipo te
        ORDER BY te.nombreidTipoequipo
                 """
    )
    tipos = cur.fetchall()
    cur.execute(
        """
        SELECT 
                f.rutFuncionario,
                f.nombreFuncionario 
        FROM funcionario f
        ORDER BY f.nombreFuncionario
                 """
    )
    funcionarios = cur.fetchall()
    return render_template(
        "asignacion.html",
        asignacion=data,
        agregar=True,
        tiposEquipos=tipos,
        funcionarios=funcionarios,
    )


@asignacion.route("/add_asignacion", methods=["POST"])
def add_estado_equipo():
    if request.method == "POST":
        # idasignacion = request.form['idasignacion']
        tipoEquipo = request.form["fechaasignacion"]
        fechaInicio = request.form["observacionasignacion"]
        Observaciones = request.form["rutaactaasignacion"]
        Acta = request.form["Activoasignacion"]
        rutFuncionario = request.form["rutFuncionario"]
        idequipo = request.form["idequipo"]
        try:
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO asignacion (fecha_inicioAsignacion,ObservacionAsignacion,rutaactaAsignacion,ActivoAsignacion,rutFuncionario,idEquipo) VALUES (%s, %s,%s,%s,%s,%s)",
                (
                    fechaasignacion,
                    observacionasignacion,
                    rutaactaasignacion,
                    Activoasignacion,
                    rutFuncionario,
                    idequipo,
                ),
            )
            mysql.connection.commit()
            flash("Estado de equipo agregado correctamente")
            return redirect(url_for("asignacion.Asignacion"))
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for("asignacion.Asignacion"))


# enviar datos a vista editar
@asignacion.route("/edit_asignacion/<id>", methods=["POST", "GET"])
def edit_asignacion(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            """ 
    SELECT d.idAsignacion, d.fecha_inicioAsignacion, 
        d.ObservacionAsignacion, d.rutaactaAsignacion , d.ActivoAsignacion, 
        d.rutFuncionario, f.rutFuncionario, d.idEquipo, eq.idEquipo
    FROM asignacion d
    INNER JOIN funcionario f on d.rutFuncionario = f.rutFuncionario
    INNER JOIN equipo eq on d.idEquipo = eq.idEquipo
    WHERE idAsignacion = %s""",
            (id,),
        )
        data = cur.fetchall()
        cur.execute("SELECT rutFuncionario FROM funcionario")
        f_data = cur.fetchall()
        cur.execute("SELECT idEquipo FROM equipo")
        eq_data = cur.fetchall()
        return render_template(
            "editasignacion.html", asignacion=data, funcionario=f_data, equipo=eq_data
        )
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for("asignacion.Asignacion"))


# actualizar
@asignacion.route("/update_asignacion/<id>", methods=["POST"])
def update_asignacion(id):
    if request.method == "POST":
        fechaasignacion = request.form["fechaasignacion"]
        observacionasignacion = request.form["observacionasignacion"]
        rutaactaasignacion = request.form["rutaactaasignacion"]
        ActivoAsignacion = request.form["Activoasignacion"]
        rutFuncionario = request.form["rutFuncionario"]
        idequipo = request.form["idequipo"]
        try:
            cur = mysql.connection.cursor()
            cur.execute(
                """
            UPDATE asignacion
            SET fecha_inicioAsignacion = %s,
                ObservacionAsignacion = %s
                rutaactaAsignacion = %s,
                ActivoAsignacion = %s,
                rutFuncionario = %s,
                idEquipo=%s
            WHERE idAsignacion = %s
            """,
                (
                    fechaasignacion,
                    observacionasignacion,
                    rutaactaasignacion,
                    ActivoAsignacion,
                    rutFuncionario,
                    idequipo,
                    id,
                ),
            )
            mysql.connection.commit()
            flash("asignacion actualizado correctamente")
            return redirect(url_for("asignacion.Asignacion"))
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for("asignacion.Asignacion"))


# eliminar
@asignacion.route("/delete_asignacion/<id>", methods=["POST", "GET"])
def delete_asignacion(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM asignacion WHERE idasignacion = %s", (id,))
        mysql.connection.commit()
        flash("asignacion eliminado correctamente")
        return redirect(url_for("asignacion.Asignacion"))
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for("asignacion.Asignacion"))
