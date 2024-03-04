from flask import Blueprint, render_template, request, url_for, redirect, flash
from db import mysql
from fpdf import FPDF
from funciones import getPerPage

asignacion = Blueprint("asignacion", __name__, template_folder="app/templates")


@asignacion.route("/asignacion")
@asignacion.route("/asignacion/<page>")
def Asignacion(page=1):
    page = int(page)
    perpage = getPerPage()
    offset = (page - 1) * perpage
    cur = mysql.connection.cursor()
    #para la tabla
    cur.execute(
        """ 
    SELECT  
        a.idAsignacion,
        te.nombreidTipoequipo,
        a.fecha_inicioAsignacion,
        a.observacionAsignacion,
        a.rutaactaAsignacion,
        f.nombreFuncionario,
        d.fechaDevolucion
    FROM asignacion a
    INNER JOIN Funcionario f ON a.rutFuncionario = f.rutFuncionario
    INNER JOIN Devolucion d ON a.idDevolucion = d.idDevolucion
    INNER JOIN Equipo_asignacion eha ON a.idAsignacion = eha.idAsignacion
    INNER JOIN Equipo eq ON eha.idEquipo = eq.idEquipo
    INNER JOIN Tipo_Equipo te ON eq.idTipo_Equipo = te.idTipo_equipo
    LIMIT {} OFFSET {}
        """.format(perpage, offset)
    )
    data = cur.fetchall()
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
    cur.execute('SELECT COUNT(*) FROM asignacion')
    total = cur.fetchone()
    total = int(str(total).split(':')[1].split('}')[0])
    return render_template("asignacion.html",  funcionarios=funcionarios, asignacion=data,
        page=page, lastpage= page < (total/perpage)+1
    )



@asignacion.route("/add_asignacion", methods=["POST"])
def add_asignacion():
    if request.method == "POST":
        rutFuncionario = request.form["rutFuncionario"]
        
        cur = mysql.connection.cursor()
        cur.execute("""
                    SELECT *
                    FROM funcionario f
                    WHERE f.rutFuncionario = %s
                    """, (rutFuncionario,))
        funcionario = cur.fetchone()

        cur.execute("""
                    SELECT * 
                    FROM equipo e
                    WHERE e.idUnidad = %s
                    """, (funcionario['idUnidad']))

        return render_template("add_asignacion.html", )



# enviar datos a vista editar
@asignacion.route("/asignacion/edit_asignacion/<id>", methods=["POST", "GET"])
def edit_asignacion(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            """ 
        SELECT a.idAsignacion, a.fecha_inicioAsignacion, 
                a.observacionAsignacion, a.rutaactaAsignacion , a.ActivoAsignacion, 
                a.rutFuncionario, f.rutFuncionario, a.idEquipo, eq.idEquipo
                FROM asignacion a
                INNER JOIN funcionario f on d.rutFuncionario = f.rutFuncionario
                INNER JOIN Equipo_asignacion eha ON a.idAsignacion = eha.idAsignacion
                INNER JOIN Equipo eq ON eha.idEquipo = eq.idEquipo
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
@asignacion.route("/asignacion/update_asignacion/<id>", methods=["POST"])
def update_asignacion(id):
    if request.method == "POST":
        fechaasignacion = request.form["fechaasignacion"]
        observacionasignacion = request.form["observacionasignacion"]
        rutaactaasignacion = request.form["rutaactaasignacion"]
        ActivoAsignacion = request.form["Activoasignacion"]
        rutFuncionario = request.form["rutFuncionario"]
        try:
            cur = mysql.connection.cursor()
            cur.execute(
                """
            UPDATE asignacion
            SET fecha_inicioAsignacion = %s,
                ObservacionAsignacion = %s
                rutaactaAsignacion = %s,
                ActivoAsignacion = %s,
                rutFuncionario = %s
            WHERE idAsignacion = %s
            """,
                (
                    fechaasignacion,
                    observacionasignacion,
                    rutaactaasignacion,
                    ActivoAsignacion,
                    rutFuncionario,
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
        cur.execute("""
                    SELECT *
                    FROM asignacion
                    WHERE idAsignacion = %s
                    """, (id,))
        asignacionAborrar = cur.fetchall()
        cur.execute("""SELECT *
                        FROM equipo_asignacion
                        WHERE idAsignacion= %s
        """, (id,))
        asignaciones = cur.fetchall()
        for asignacion in asignaciones:
            cur.execute(""" 
                        UPDATE equipo
                        SET idTipo_equipo= %s
                        WHERE idEquipo= %s""", (asignacionAborrar[1]['idAsignacion'],asignacion['idEquipo']))
        cur.execute("DELETE FROM equipo_asignacion WHERE idAsignacion = %s", (id,))
        mysql.connection.commit()
        cur.execute("DELETE FROM asignacion WHERE idAsignacion = %s", (id,))
        mysql.connection.commit()
        flash("asignacion eliminado correctamente")
        return redirect(url_for("asignacion.Asignacion"))
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for("asignacion.Asignacion"))
    
@asignacion.route("/asignacion/create_asignacion/<rut>", methods=["POST"])
def create_asignacion(rut):
    if request.method == "POST":
        # Extraer datos del formulario
        fecha_inicio_asignacion = request.form['fecha_inicio_asignacion']
        observacion_asignacion = request.form['observacion_asignacion']
        ruta_acta_asignacion = request.form['ruta_acta_asignacion']
        activo_asignacion = request.form['activo_asignacion']
        id_devolucion = request.form['id_devolucion']
        rut=rut
        # Conectarse a la base de datos y realizar la inserción en la tabla ASIGNACION
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO ASIGNACION (
                fecha_inicioAsignacion,
                ObservacionAsignacion,
                rutaactaAsignacion, 
                ActivoAsignacion,
                rutFuncionario,
                idDevolucion
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (fecha_inicio_asignacion, observacion_asignacion, ruta_acta_asignacion, activo_asignacion, rut, id_devolucion))
        mysql.connection.commit()

        # Recuperar el ID de la asignación recién insertada
        asignacion_id = cur.lastrowid

        # Obtener la lista de equipos asignados desde el formulario
        equipos = request.form.getlist('equipos[]')

        # Iterar sobre los equipos y realizar las operaciones necesarias
        for equipo_id in equipos:
            # Insertar en la tabla Equipo_asignacion
            cur.execute("""
                INSERT INTO equipo_asignacion (idEquipo, idAsignacion)
                VALUES (%s, %s)
                """, (equipo_id, asignacion_id))
            mysql.connection.commit()

        flash("Asignación creada correctamente")
        return redirect(url_for('traslado.Traslado'))
    return redirect(url_for('traslado.Traslado'))




@asignacion.route("/test")
def crear_pdf(Funcionario, Unidad, Asignacion, Equipos):

    class PDF(FPDF):
        def header(self):
            # logo
            # imageUrl = url_for('static', filename='img/logo_junji.png')
            # print(imageUrl)
            self.image("logo_junji.png", 10, 8, 25)
            # font
            self.set_font("times", "B", 12)
            self.set_text_color(170, 170, 170)
            # Title
            self.cell(0, 30, "", border=False, ln=1, align="L")
            self.cell(0, 5, "JUNTA NACIONAL", border=False, ln=1, align="L")
            self.cell(0, 5, "INFANTILES", border=False, ln=1, align="L")
            self.cell(0, 5, "Unidad de Inventarios", border=False, ln=1, align="L")
            # line break
            self.ln(10)

        def footer(self):
            self.set_y(-30)
            self.set_font("times", "B", 12)
            self.set_text_color(170, 170, 170)
            self.cell(0, 0, "", ln=1)
            self.cell(0, 0, "Junta Nacional de Jardines Infantiles-JUNJI", ln=1)
            self.cell(
                0, 12, "OHiggins Poniente 77 Concepción. 041-2125541", ln=1
            )  # problema con el caracter ’
            self.cell(0, 12, "www.junji.cl", ln=1)

    pdf = PDF("P", "mm", "A4")
    pdf.add_page()
    titulo = "ACTA De Asignacion de Equipo Informatico N°" + str(1)

    pdf.set_font("times", "", 20)
    pdf.cell(0, 10, titulo, ln=True, align="C")
    pdf.set_font("times", "", 12)
    presentacion1 = "Por el presente se hace entrega a: "
    presentacion2 = "Dependiente de la Unidad: "
    presentacion22 = "En la Fecha: "
    presentacion3 = "Del siguiente equipo computacional"

    nombreFuncionario = Funcionario["nombreFuncionario"]
    nombreUnidad = Unidad["nombreUnidad"]
    fechaAsignacion = Asignacion["fecha_inicioAsignacion"]

    pdf.ln(10)
    with pdf.text_columns(text_align="J", ncols=2, gutter=20) as cols:
        cols.write(presentacion1)
        cols.ln()
        cols.write(presentacion2)
        cols.ln()
        cols.write(presentacion22)
        cols.ln()
        cols.ln()
        cols.write(presentacion3)
        cols.ln()
        cols.new_column()
        cols.write(nombreFuncionario)
        cols.ln()
        cols.write(nombreUnidad)
        cols.ln()
        cols.write(fechaAsignacion)

    pdf.ln(20)
    TABLE_DATA = (
        ("id", "Tipo_Equipo", "Marca", "Modelo", "N° Serie", "N° Inventario"),
    )
    for equipo in Equipos:
        id = str(equipo["idEquipo"])
        tipo_equipo = equipo["nombreidTipoEquipo"]
        marca = equipo["nombreMarcaEquipo"]
        modelo = equipo["nombreModeloEquipo"]
        num_serie = str(equipo["Num_serieEquipo"])
        num_inventario = str(equipo["Cod_inventarioEquipo"])

        TABLE_DATA = TABLE_DATA + (
            (id, tipo_equipo, marca, modelo, num_serie, num_inventario),
        )

    with pdf.table() as table:
        for datarow in TABLE_DATA:
            row = table.row()
            for datum in datarow:
                row.cell(datum)

    observacion = "Esta es una observacion"

    pdf.ln(10)
    nombreEncargado = "Nombre Encargado TI:"
    rutEncargado = "Numero de RUT:"
    firmaEncargado = "Firma:"
    nombreMinistro = "Nombre Funcionario:"
    rutMinistro = "Numero de RUT:"
    firma = "Firma"
    with pdf.text_columns(text_align="J", ncols=2, gutter=20) as cols:
        cols.write(nombreEncargado)
        cols.ln()
        cols.ln()
        cols.write(rutEncargado)
        cols.ln()
        cols.ln()
        cols.write(firmaEncargado)
        cols.ln()
        cols.ln()
        cols.ln()
        cols.ln()

        cols.write(nombreMinistro)
        cols.ln()
        cols.ln()
        cols.write(rutMinistro)
        cols.ln()
        cols.ln()
        cols.write(firma)
        cols.ln()
        cols.ln()
        cols.new_column()
        for i in range(0, 3):
            cols.write(text="_________________________")
            cols.ln()
            cols.ln()
        cols.ln()
        cols.ln()
        for i in range(0, 3):
            cols.write(text="_________________________")
            cols.ln()
            cols.ln()
    nombrePdf = "asignacion_" + str(
        Funcionario["nombreFuncionario"]
        + "_"
        + str(Asignacion["fecha_inicioAsignaion"])
        + "_"
        + str(Asignacion["idAsignacion"])
    )
    pdf.output(nombrePdf)
    return redirect(url_for("asignacion.Asignacion"))

