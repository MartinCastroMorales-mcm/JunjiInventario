from flask import Blueprint, render_template, request, url_for, redirect, flash, send_file
from db import mysql
from fpdf import FPDF
from funciones import getPerPage
import os
import shutil
from datetime import date

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
        a.fecha_inicioAsignacion,
        a.observacionAsignacion,
        a.rutaactaAsignacion,
        f.nombreFuncionario,
        a.fechaDevolucion,
        a.ActivoAsignacion
    FROM asignacion a
    INNER JOIN Funcionario f ON a.rutFuncionario = f.rutFuncionario
    LIMIT {} OFFSET {}
        """.format(perpage, offset)
    )
    data = cur.fetchall()
    cur.execute(
        """ SELECT 
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



@asignacion.route("/add_asignacion", methods=["GET"])
def add_asignacion():
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT *
                FROM funcionario f
                """)
    funcionarios_data = cur.fetchall()

    cur.execute("""
                SELECT * 
                FROM equipo e
                INNER JOIN modelo_equipo me ON e.idModelo_Equipo = me.idModelo_Equipo
                INNER JOIN Tipo_Equipo te ON e.idTipo_Equipo = te.idTipo_equipo
                INNER JOIN unidad u ON e.idUnidad = u.idUnidad
                INNER JOIN estado_equipo ee ON ee.idEstado_Equipo = e.idEstado_Equipo
                WHERE ee.nombreEstado_equipo = %s
                """, ("SIN ASIGNAR",))
    equipos_data = cur.fetchall()
    return render_template("add_asignacion.html",equipos=equipos_data,
                            funcionarios=funcionarios_data )



# enviar datos a vista editar
@asignacion.route("/asignacion/edit_asignacion/<id>", methods=["POST", "GET"])
def edit_asignacion(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            """ 
           SELECT  
                a.idAsignacion,
                a.fecha_inicioAsignacion,
                a.observacionAsignacion,
                a.rutaactaAsignacion,
                f.nombreFuncionario,
                d.fechaDevolucion
                FROM asignacion a
                INNER JOIN Funcionario f ON a.rutFuncionario = f.rutFuncionario
                LEFT JOIN Devolucion d ON a.idDevolucion = d.idDevolucion
            WHERE idAsignacion = %s""",
            (id,),
        )
        data = cur.fetchall()
        cur.execute("SELECT * FROM funcionario")
        f_data = cur.fetchall()
        cur.execute("SELECT * FROM equipo")
        eq_data = cur.fetchall()
        return render_template(
            "editAsignacion.html", asignacion=data, funcionario=f_data, equipo=eq_data
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
        asignacionAborrar = cur.fetchone()
        cur.execute("""SELECT *
                        FROM equipo_asignacion
                        WHERE idAsignacion= %s
        """, (id,))
        asignaciones = cur.fetchall()
        for asignacion in asignaciones:
            idEquipo = asignacion['idEquipo']
            cur.execute("""
                        SELECT *
                        FROM estado_equipo
                        WHERE nombreEstado_equipo = %s
                        """, ("SIN ASIGNAR",))
            estado_equipo_data = cur.fetchone()
            cur.execute("""
                        UPDATE equipo
                        SET idEstado_equipo = %s
                        WHERE idEquipo = %s
                        """, (estado_equipo_data['idEstado_equipo'], idEquipo))
            mysql.connection.commit()
        cur.execute("DELETE FROM equipo_asignacion WHERE idAsignacion = %s", (id,))
        mysql.connection.commit()
        cur.execute("DELETE FROM asignacion WHERE idAsignacion = %s", (id,))
        mysql.connection.commit()
        flash("asignacion eliminado correctamente")
        return redirect(url_for("asignacion.Asignacion"))
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for("asignacion.Asignacion"))
    
@asignacion.route("/asignacion/create_asignacion", methods=["POST"])
def create_asignacion():
    if request.method == "POST":
        # Extraer datos del formulario
        fechaasignacion = request.form['fechaasignacion']
        observacion = request.form['observacion']
        #rutadocumento = request.form['']
        #activo_asignacion = request.form['activo_asignacion']
        rut=request.form['rut']
        # Conectarse a la base de datos y realizar la inserción en la tabla ASIGNACION
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO ASIGNACION (
                fecha_inicioAsignacion,
                ObservacionAsignacion,
                rutaactaAsignacion, 
                rutFuncionario,
                ActivoAsignacion
            )
            VALUES (%s, %s, %s, %s, 1)
            """, (fechaasignacion, observacion, 'ruta', rut,))
        mysql.connection.commit()

        # Recuperar el ID de la asignación recién insertada
        asignacion_id = cur.lastrowid

        # Obtener la lista de equipos asignados desde el formulario
        equipos = request.form.getlist('asignaciones[]')

        TuplaEquipos = ()
        # Iterar sobre los equipos y realizar las operaciones necesarias
        for equipo_id in equipos:
            # Insertar en la tabla Equipo_asignacion
            cur.execute("""
                INSERT INTO equipo_asignacion (idAsignacion, idEquipo)
                VALUES (%s, %s)
                """, (str(asignacion_id),equipo_id))
            mysql.connection.commit()
            cur.execute("""
                        SELECT *
                        FROM estado_equipo
                        WHERE nombreEstado_equipo = %s
                        """, ("EN USO",))
            estado_equipo_data = cur.fetchone() 
            
            cur.execute("""
                        UPDATE equipo
                        SET idEstado_equipo = %s
                        WHERE idEquipo = %s
                        """, (estado_equipo_data['idEstado_equipo'], equipo_id))
            mysql.connection.commit()
            
            cur.execute("""
                        SELECT *
                        FROM equipo
                        INNER JOIN tipo_equipo te on equipo.idTipo_equipo = te.idTipo_equipo
                        INNER JOIN estado_equipo ee on ee.idEstado_equipo = equipo.idEstado_equipo
                        INNER JOIN modelo_equipo me on me.idModelo_Equipo = equipo.idModelo_Equipo
                        INNER JOIN marca_equipo mae on mae.idMarca_equipo = me.idMarca_equipo
                        WHERE equipo.idEquipo = %s
                        """, (equipo_id,))
            equipoTupla = cur.fetchone()
            TuplaEquipos = TuplaEquipos + (equipoTupla,)

        flash("Asignación creada correctamente")
        #agregar argumentos
        cur.execute("""
                    SELECT *
                    FROM funcionario f
                    WHERE f.rutFuncionario = %s
                    """, (rut,))
        Funcionario = cur.fetchone()
        cur.execute("""
                    SELECT *
                    FROM Unidad u
                    WHERE u.idUnidad = %s
                    """, (Funcionario['idUnidad'],))
        Unidad = cur.fetchone()
        cur.execute("""
                    SELECT *
                    FROM asignacion a
                    WHERE a.idAsignacion = %s
                    """, (asignacion_id,))
        Asignacion = cur.fetchone()


        crear_pdf(Funcionario, Unidad, Asignacion, TuplaEquipos)
        return redirect(url_for('asignacion.Asignacion'))
    return redirect(url_for('asignacion.Asignacion'))



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
    titulo = "ACTA De Asignacion de Equipo Informatico N°" + str(Asignacion['idAsignacion'])

    pdf.set_font("times", "", 20)
    pdf.cell(0, 10, titulo, ln=True, align="C")
    pdf.set_font("times", "", 12)
    presentacion1 = "Por el presente se hace entrega a: "
    presentacion2 = "Dependiente de la Unidad: "
    presentacion22 = "En la Fecha: "
    presentacion3 = "Del siguiente equipo computacional"

    nombreFuncionario = Funcionario["nombreFuncionario"]
    nombreUnidad = Unidad["nombreUnidad"]
    fechaAsignacion = str(Asignacion["fecha_inicioAsignacion"])

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
        ("N°", "Tipo_Equipo", "Marca", "Modelo", "N° Serie", "N° Inventario"),
    )
    i = 0
    for equipo in Equipos:
        id = str(equipo["idEquipo"])
        tipo_equipo = equipo["nombreidTipoequipo"]
        marca = equipo["nombreMarcaEquipo"]
        modelo = equipo["nombreModeloequipo"]
        num_serie = str(equipo["Num_serieEquipo"])
        num_inventario = str(equipo["Cod_inventarioEquipo"])

        i += 1

        TABLE_DATA = TABLE_DATA + (
            (str(i), tipo_equipo, marca, modelo, num_serie, num_inventario),
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
    nombrePdf = "asignacion_" + str(Asignacion["idAsignacion"]) + ".pdf"
    pdf.output(nombrePdf)
    shutil.move(nombrePdf, "app/pdf")
    return redirect(url_for("asignacion.Asignacion"))

@asignacion.route("/asignacion/mostrar_pdf/<id>")
def mostrar_pdf(id):
    try:
        nombrePdf = "asignacion_" + str(id) + ".pdf"
        dir = r"C:\Users\Junji\Downloads\Junji_inventario-main1\Junji_inventario-main\Junji_inventario-main\app\pdf"
        file = os.path.join(dir, nombrePdf)
        return send_file(file, as_attachment=True)
    except:
        flash("no se encontro el pdf")
        return redirect(url_for('asignacion.Asignacion'))

@asignacion.route("/asignacion/devolver/<id>")
def devolver(id):
    today = date.today()
    cur = mysql.connection.cursor()
    cur.execute("""
    UPDATE asignacion a
    SET a.ActivoAsignacion = 0,
        fechaDevolucion = %s
    WHERE a.idAsignacion = %s
                """, (today, id,))
    mysql.connection.commit()

    #buscar argumentos
    cur.execute("""
    SELECT *
    FROM asignacion a
    WHERE a.idAsignacion = %s
                """, (id,))
    Asignacion = cur.fetchone()
    cur.execute("""
    SELECT *
    FROM funcionario f
    WHERE f.rutFuncionario = %s
                """, (Asignacion['rutFuncionario'], ))
    Funcionario = cur.fetchone()
    cur.execute("""
    SELECT *
    FROM Unidad u
    WHERE u.idUnidad = %s
                """, (str(Funcionario['idUnidad']),))
    Unidad = cur.fetchone()
    
    cur.execute("""
    SELECT * 
    FROM equipo_asignacion ea
    WHERE ea.idAsignacion = %s
                """, (str(Asignacion['idAsignacion']),))
    equipo_asignacion_data = cur.fetchall()

    tupla_equipos = ()
    for equipo_asignacion in equipo_asignacion_data:
        cur.execute("""
        SELECT * 
        FROM equipo e
        INNER JOIN modelo_equipo me ON e.idModelo_Equipo = me.idModelo_Equipo
        INNER JOIN Tipo_Equipo te ON e.idTipo_Equipo = te.idTipo_equipo
        INNER JOIN unidad u ON e.idUnidad = u.idUnidad
        INNER JOIN estado_equipo ee ON ee.idEstado_Equipo = e.idEstado_Equipo
        INNER JOIN marca_equipo mae on mae.idMarca_equipo = me.idMarca_equipo
        WHERE e.idEquipo = %s
                    """, (str(equipo_asignacion['idEquipo']),))
        equipo = cur.fetchone()

        cur.execute("""
        SELECT *
        FROM estado_equipo ee
        WHERE ee.nombreEstado_equipo = "SIN ASIGNAR"
                    """)
        estadoEquipo = cur.fetchone()
        cur.execute("""
        UPDATE equipo
        SET idEstado_equipo = %s
        WHERE idEquipo = %s
                    """, (str(estadoEquipo['idEstado_equipo']), str(equipo['idEquipo'])))
        mysql.connection.commit()
        tupla_equipos = tupla_equipos + (equipo,)


    crear_pdf_devolucion(Funcionario, Unidad, Asignacion, tupla_equipos)
    return redirect(url_for('asignacion.Asignacion'))

    

def crear_pdf_devolucion(
        Funcionario,
        Unidad,
        Asignacion,
        Equipos):
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
        
    pdf = PDF("P", "mm", "A4")
    pdf.add_page()
    titulo = "ACTA Devolucion de Equipo Informatico N°" + str(Asignacion['idAsignacion'])

    pdf.set_font("times", "", 20)
    pdf.cell(0, 10, titulo, ln=True, align="C")
    pdf.set_font("times", "", 12)
    presentacion1 = "Por el presente se hace entrega a: "
    presentacion2 = "Dependiente de la Unidad: "
    presentacion22 = "En la Fecha: "
    presentacion3 = "Del siguiente equipo computacional"

    nombreFuncionario = Funcionario["nombreFuncionario"]
    nombreUnidad = Unidad["nombreUnidad"]
    fechaAsignacion = str(Asignacion["fecha_inicioAsignacion"])

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
        ("N°", "Tipo_Equipo", "Marca", "Modelo", "N° Serie", "N° Inventario"),
    )
    i = 0
    for equipo in Equipos:
        id = str(equipo["idEquipo"])
        tipo_equipo = equipo["nombreidTipoequipo"]
        marca = equipo["nombreMarcaEquipo"]
        modelo = equipo["nombreModeloequipo"]
        num_serie = str(equipo["Num_serieEquipo"])
        num_inventario = str(equipo["Cod_inventarioEquipo"])

        i += 1

        TABLE_DATA = TABLE_DATA + (
            (str(i), tipo_equipo, marca, modelo, num_serie, num_inventario),
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
    nombrePdf = "Devolucion_" + str(Asignacion["idAsignacion"]) + ".pdf"
    pdf.output(nombrePdf)
    shutil.move(nombrePdf, "app/pdf")

@asignacion.route("/asignacion/mostrar_pdf_devolucion/<id>")
def mostrar_pdf_devolucion(id):
    try:
        nombrePdf = "devolucion_" + str(id) + ".pdf"
        dir = r"C:\Users\Junji\Downloads\Junji_inventario-main1\Junji_inventario-main\Junji_inventario-main\app\pdf"
        file = os.path.join(dir, nombrePdf)
        return send_file(file, as_attachment=True)
    except:
        flash("no se encontro el pdf")
        return redirect(url_for('asignacion.Asignacion'))