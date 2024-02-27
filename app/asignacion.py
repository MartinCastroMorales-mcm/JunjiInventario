from flask import Blueprint, render_template, request, url_for, redirect, flash
from db import mysql
from fpdf import FPDF
from funciones import getPerPage

asignacion = Blueprint("asignacion", __name__, template_folder="app/templates")


@asignacion.route("/asignacion")
@asignacion.route("/asignacion/<page>")
def Asignacion(page = 1):
    page = int(page)
    perpage = getPerPage()
    offset = (page-1) * perpage
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
    LIMIT {} OFFSET {}
        """.format(perpage, offset)
    )
    data = cur.fetchall()
    cur.execute('SELECT COUNT(*) FROM asignacion')
    total = cur.fetchone()
    total = int(str(total).split(':')[1].split('}')[0])
    return render_template("asignacion.html", asignacion=data,
        page=page, lastpage= page < (total/perpage)+1
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

@asignacion.route("/test")
def crear_pdf(Funcionario, Unidad, Asignacion, Equipos):

    class PDF(FPDF):
        def header(self):
            #logo
            #imageUrl = url_for('static', filename='img/logo_junji.png')
            #print(imageUrl)
            self.image('logo_junji.png', 10, 8, 25)
            #font
            self.set_font('times', 'B', 12)
            self.set_text_color(170,170,170)
            #Title
            self.cell(0, 30, '', border=False, ln=1, align='L')
            self.cell(0, 5, 'JUNTA NACIONAL', border=False, ln=1, align='L')
            self.cell(0, 5, 'INFANTILES', border=False, ln=1, align='L')
            self.cell(0, 5, 'Unidad de Inventarios', border=False, ln=1, align='L')
            #line break
            self.ln(10)

        def footer(self):
                self.set_y(-30)
                self.set_font('times', 'B', 12)
                self.set_text_color(170,170,170)
                self.cell(0,0, "", ln=1)
                self.cell(0,0, "Junta Nacional de Jardines Infantiles-JUNJI", ln=1)
                self.cell(0,12, "OHiggins Poniente 77 Concepción. 041-2125541", ln=1) #problema con el caracter ’
                self.cell(0,12, "www.junji.cl", ln=1)
        
    pdf = PDF('P', 'mm', 'A4')
    pdf.add_page()
    titulo = "ACTA De Asignacion de Equipo Informatico N°" + str(1)

    pdf.set_font('times', '', 20)
    pdf.cell(0, 10, titulo, ln=True, align='C')
    pdf.set_font('times', '', 12)
    presentacion1 = "Por el presente se hace entrega a: "
    presentacion2 = "Dependiente de la Unidad: "
    presentacion22 = "En la Fecha: "
    presentacion3 = "Del siguiente equipo computacional"

    nombreFuncionario = Funcionario['nombreFuncionario'] 
    nombreUnidad = Unidad['nombreUnidad']
    fechaAsignacion = Asignacion['fecha_inicioAsignacion']


    pdf.ln(10)
    with pdf.text_columns(text_align='J', ncols=2, gutter=20) as cols:
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
        id = str(equipo['idEquipo']) 
        tipo_equipo = equipo['nombreidTipoEquipo']
        marca = equipo['nombreMarcaEquipo']
        modelo = equipo['nombreModeloEquipo']
        num_serie = str(equipo['Num_serieEquipo']) 
        num_inventario = str(equipo['Cod_inventarioEquipo']) 

        TABLE_DATA = TABLE_DATA + ((id, tipo_equipo, marca, modelo, num_serie,
                                    num_inventario),)
    
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
    nombrePdf = "asignacion_" + str(Funcionario['nombreFuncionario'] + "_" + str(Asignacion['fecha_inicioAsignaion']) + "_" + str(Asignacion['idAsignacion']))
    pdf.output(nombrePdf)
    return redirect(url_for("asignacion.Asignacion"))



         