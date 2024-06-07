from flask import Blueprint, render_template, request, url_for, redirect, flash, make_response, send_file, session
from db import mysql
from fpdf import FPDF
from funciones import getPerPage
import os
import shutil 
from cuentas import loguear_requerido, administrador_requerido
from werkzeug.utils import secure_filename
traslado = Blueprint("traslado", __name__, template_folder="app/templates")

PDFS_DIR = r'C:\Users\Junji\Downloads\Junji_inventario-main1\Junji_inventario-main\Junji_inventario-main\app\pdf'

@traslado.route("/traslado")
@traslado.route("/traslado/<page>")
@loguear_requerido
def Traslado(page = 1):
    if "user" not in session:
        flash("Se nesesita ingresar para acceder a esa ruta")
        return redirect("/ingresar")
    page = int(page)
    perpage = getPerPage()
    offset = (page -1) * perpage
    cur = mysql.connection.cursor()
    cur.execute(
        """
                SELECT t.idTraslado, t.fechatraslado, t.rutadocumentoTraslado, 
                    origen.nombreUnidad as nombreOrigen, 
                    destino.nombreUnidad as nombreDestino,
                    t.estaFirmadoTraslado
                FROM traslado t
                INNER JOIN unidad origen on origen.idUnidad = t.idUnidadOrigen
                INNER JOIN unidad destino on destino.idUnidad = t.idUnidadDestino
                ORDER BY idTraslado DESC
                LIMIT %s OFFSET %s
        """, (perpage, offset)
    )
    data = cur.fetchall()
    cur.execute('SELECT COUNT(*) FROM traslado')
    total = cur.fetchone()
    #estraer el numero del mensaje
    total = int(str(total).split(':')[1].split('}')[0])
    cur.execute(
        """
        SELECT * 
        FROM unidad u
        ORDER BY u.nombreUnidad
                 """
    )
    unidades = cur.fetchall()
    return render_template("traslado.html", traslado=data, unidades=unidades,
                           page=page, lastpage= page < (total/perpage)+1)



@traslado.route("/traslado/add_traslado", methods=["GET", "POST"])
@administrador_requerido
def add_traslado():
    if "user" not in session:
        flash("Se nesesita ingresar para acceder a esa ruta")
        return redirect("/ingresar")
    if request.method == 'POST':

        Origen = int(request.form['Origen'])
        print(Origen)
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT *
                FROM equipo e
                INNER JOIN unidad u on u.idUnidad = e.idUnidad
                INNER JOIN modelo_equipo me on me.idModelo_equipo = e.idModelo_equipo 
                INNER JOIN tipo_equipo te on te.idTipo_equipo = me.idTipo_equipo
                WHERE e.idUnidad = %s
                        """, (Origen,))
                    
            equipos_data = cur.fetchall()
            cur.execute(
                """
                SELECT * 
                FROM unidad u
                ORDER BY u.nombreUnidad
                        """
            )
            print("equipos: ")
            print(equipos_data)
            unidades = cur.fetchall()
            if len(equipos_data) == 0:
                equipos_data = []
                flash("no hay equipos en esta Unidad")
                return redirect(url_for('traslado.Traslado'))
            return render_template("add_traslado.html", equipos=equipos_data, unidades=unidades)

        except Exception as e:
            flash(e.args[1])
            return redirect(url_for('traslado.Traslado'))

@traslado.route("/traslado/edit_traslado/<id>", methods=["POST", "GET"])
@administrador_requerido
def edit_traslado(id):
    if "user" not in session:
        flash("Se nesesita ingresar para acceder a esa ruta")
        return redirect("/ingresar")
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
            INNER JOIN modelo_equipo me on e.idModelo_Equipo = me.idModelo_Equipo
            INNER JOIN tipo_equipo te on te.idTipo_equipo = me.idTipo_equipo
            ORDER BY e.idEquipo
                    """
        )
        equipos = cur.fetchall()
        return render_template('editTraslado.html', traslado=data[0], agregar=True, unidades=unidades, equipo= equipos)

    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('traslado.Traslado'))

@traslado.route("/traslado/delete_traslado/<id>", methods = ["POST", "GET"])
@administrador_requerido
def delete_traslado(id):
    if "user" not in session:
        flash("Se nesesita ingresar para acceder a esa ruta")
        return redirect("/ingresar")
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
                    SELECT *
                    FROM traslado
                    WHERE idTraslado = %s
                    """, (id,))
        trasladoABorrar = cur.fetchall()
        cur.execute("""
                    SELECT *
                    FROM traslacion
                    WHERE idTraslado = %s
                    """, (id,))
        traslaciones = cur.fetchall()
        for traslacion in traslaciones:
            cur.execute("""
                        UPDATE equipo
                        SET idUnidad = %s
                        WHERE idEquipo = %s 
                        """, (trasladoABorrar[0]['idUnidadOrigen'], traslacion['idEquipo']))
        
        cur.execute("""DELETE 
                        FROM traslacion
                        WHERE idTraslado = %s
        """, (id,))
        mysql.connection.commit()
        cur.execute('DELETE FROM traslado WHERE idTraslado = %s', (id,))
        mysql.connection.commit()
        flash('Traslado eliminado correctamente')
        return redirect(url_for('traslado.Traslado'))
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('traslado.Traslado'))

@traslado.route("/traslado/create_traslado/<origen>", methods=["POST"])
@administrador_requerido
def create_traslado(origen):
    if "user" not in session:
        flash("Se nesesita ingresar para acceder a esa ruta")
        return redirect("/ingresar")
    if request.method == "POST":
        fechatraslado = request.form['fechatraslado']
        #rutadocumento = request.form['']
        Destino = request.form['Destino']
        #trasladar[] es la notacion para obtener un array con todos los outputs de las checklist
        equipos = request.form.getlist('trasladar[]')
        crear_traslado_generico(fechatraslado, Destino, origen, equipos)

        return redirect(url_for('traslado.Traslado'))
    return redirect(url_for('traslado.Traslado'))

def crear_traslado_generico(fechatraslado, Destino, Origen, equipos):
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
        TuplaEquipos = ()
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

            cur.execute("""
                        SELECT *
                        FROM equipo e
                        INNER JOIN modelo_equipo me ON me.idModelo_equipo = e.idModelo_equipo
                        INNER JOIN tipo_equipo te on me.idTipo_equipo = me.idTipo_equipo
                        INNER JOIN estado_equipo ee on ee.idEstado_equipo = e.idEstado_equipo
                        WHERE e.idEquipo = %s
                        """, (idEquipo,))
            equipoTupla = cur.fetchone()
            TuplaEquipos = TuplaEquipos + (equipoTupla,)

        #nombre origen y destino
        cur.execute("""
                    SELECT *
                    FROM traslado
                    WHERE traslado.idTraslado = %s 
                    """, (str(trasladoid),))
        traslado = cur.fetchone()
        cur.execute("""
                    SELECT *
                    FROM unidad
                    WHERE unidad.idUnidad = %s
                    """, (traslado['idUnidadOrigen'],))
        UnidadOrigen = cur.fetchone()

        cur.execute("""
                    SELECT *
                    FROM unidad
                    WHERE unidad.idUnidad = %s
                    """, (traslado['idUnidadDestino'],))
        UnidadDestino = cur.fetchone()

        flash("traslado agregado correctamente")
        create_pdf(traslado, TuplaEquipos, UnidadOrigen, UnidadDestino)


def create_pdf(traslado, equipos, UnidadOrigen, UnidadDestino):
    if "user" not in session:
        flash("Se nesesita ingresar para acceder a esa ruta")
        return redirect("/ingresar")

    #se añade el encabezado y footer creando una clase PDF que hereda de FPDF y sobreescribe los
    #metodos
    class PDF(FPDF):
        def header(self):
            #logo
            #imageUrl = url_for('static', filename='img/logo_junji.png')
            #print(imageUrl)
            self.image('logo_junji.jpg', 10, 8, 25)
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
            #self.image('logo_inferior.jpg', 30, -30, 25) Las imagenes en el Footer no parecen funcionar correctamente



    #(Orientacion, unidades, formato)
    #Orientacion P(portrait) o L(landscape)
    pdf = PDF('P', 'mm', 'A4')

    pdf.add_page()


    titulo = "ACTA DE TRASLADO N°" + str(traslado['idTraslado']) 
    parrafo_1 = "En Concepción {} se procede al traslado de bienes JUNJI de registro inventario desde {} hasta {} el siguiente detalle: ".format(traslado['fechatraslado'], UnidadOrigen['nombreUnidad'], UnidadDestino['nombreUnidad'])
    #encabezado de la tabla
    TABLE_DATA = (
    ("N°", "Articulos", "Serie", "Código Inventario", "Estado", "Modelo"),
    )
    #print("$$$$$$$$$$$$$$$$$$$$$$$$$")
    #print(equipos) 
    #contadores de estado
    
    #ingresa los datos de la tabla como una tupla, donde la primera tupla es el encabezado
    i = 0
    for equipo in equipos:
        i += 1
        TABLE_DATA = TABLE_DATA + ((str((i)), equipo['nombreTipo_equipo'],
                        equipo['nombreModeloequipo'],
                        str(equipo['Num_serieEquipo']),
                        str(equipo['Cod_inventarioEquipo']),
                        equipo['nombreEstado_equipo']
                        ),)
    
    #print("#$$$$$$#############")
    #print(TABLE_DATA)

    #TABLE_DATA2 = (('N°', 'Articulos', 'Serie', 'Código Inventario', 'Estado'), 
                   #(str(3), 'AIO', str(0), str(8013913), 'EN USO'),)
    #("1", "EpsonI5190", "X5NS117668", "8042812", "MAL"),
    #("2", "EpsonI5190", "X5NS117668", "8042813", "MAL"),
    #("3", "EpsonI5190", "X5NS117668", "8042814", "MAL"),
    #("4", "EpsonI5190", "X5NS117668", "8042815", "MAL"),
    pdf.set_font('times', '', 20)
    pdf.cell(0, 10, titulo, ln=True, align='C')            
    pdf.set_font('times', '', 12)
            
    pdf.multi_cell(0, 10, parrafo_1)
    #crea una tabla en base a los datos anteriores
    with pdf.table() as table:
        for datarow in TABLE_DATA:
            row = table.row()
            for datum in datarow:
                row.cell(datum)
    #parrafo_2 = "Se ecuentran X en Bien, Y Regular y Z Mal"


    #pdf.multi_cell(0,10,parrafo_2, ln=True)
    pdf.ln(10)
    nombreEncargado = "Nombre Encargado:"
    rutEncargado = "Numero de RUT:"
    firmaEncargado = "Firma:"
    nombreMinistro = "Nombre Ministro de Fe:"
    rutMinistro = "Numero de RUT:"
    firma = "Firma"
    nombreEncargadoUnidadTI = "Nombre Encargado TI " + session["user"]
    rutMinistro = "Numero de RUT:"
    firma = "Firma"
    #crea dos columnas una para el espacio de firma y otra para los nombres
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
        cols.ln()
        cols.ln()

        cols.write(nombreEncargadoUnidadTI)
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
        cols.ln()
        cols.ln()
        for i in range(0, 3):
            cols.write(text="_________________________")
            cols.ln()
            cols.ln()
    #crear pdf con la id para diferenciar pdfs

    nombrePdf = "traslado" + "_" + str(traslado['idTraslado']) + ".pdf"
    pdf.output(nombrePdf)
    #print("test")
    #print(str(os.curdir)) 

    #mover pdf a la carpeta
    shutil.move(nombrePdf, "app/pdf")
    return redirect(url_for('traslado.Traslado'))

@traslado.route("/traslado/mostrar_pdf/<id>")
@traslado.route("/traslado/mostrar_pdf/<id>/<firmado>")
@loguear_requerido
def mostrar_pdf(id, firmado="0"):
    if "user" not in session:
        flash("Se nesesita ingresar para acceder a esa ruta")
        return redirect("/ingresar")
    print(firmado)
    try:
        if firmado == "0":
            nombrePdf = "traslado_" + str(id) + ".pdf"
        else:
            nombrePdf = "traslado_" + str(id) + "_firmado.pdf"
            print("se encontro el firmado" + nombrePdf)
        dir = r"C:\Users\Junji\Downloads\Junji_inventario-main1\Junji_inventario-main\Junji_inventario-main\app\pdf"
        file = os.path.join(dir, nombrePdf)
        return send_file(file, as_attachment=True)
    except:
        flash("no se encontro el pdf")
        return redirect(url_for('traslado.Traslado'))

@traslado.route("/traslado/buscar/<idTraslado>")
@loguear_requerido
def buscar(idTraslado):
    if "user" not in session:
        flash("Se nesesita ingresar para acceder a esa ruta")
        return redirect("/ingresar")
    cur = mysql.connection.cursor()
    cur.execute(
        """
                SELECT t.idTraslado, t.fechatraslado, t.rutadocumentoTraslado, 
                    origen.nombreUnidad as nombreOrigen, 
                    destino.nombreUnidad as nombreDestino,
                    t.estaFirmadoTraslado
                FROM traslado t
                INNER JOIN unidad origen on origen.idUnidad = t.idUnidadOrigen
                INNER JOIN unidad destino on destino.idUnidad = t.idUnidadDestino
                WHERE t.idTraslado = %s
                ORDER BY idTraslado DESC
        """, (idTraslado,)
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
    
    return render_template("traslado.html", traslado=data, unidades=unidades,
                           page=1, lastpage= True)

@traslado.route("/traslado/listar_pdf/<idTraslado>")
@loguear_requerido
def listar_pdf(idTraslado):
    if "user" not in session:
        flash("Se nesesita ingresar para acceder a esa ruta")
        return redirect("/ingresar")
    dir = PDFS_DIR   
    nombreFirmado = "traslado_" + str(idTraslado) + "_" + "firmado.pdf"
    #revisa si el archivo esta firmado
    if not os.path.exists(os.path.join(dir, nombreFirmado)):
        #mostrar
        print("#####NombreFirmado = None #######")
        nombreFirmado = "None"
    print("exists")
    return render_template("firma.html", 
        nombreFirmado=nombreFirmado, id=idTraslado, location="traslado")

@traslado.route("/traslado/adjuntar_pdf/<idTraslado>", methods=["POST"])
@administrador_requerido
def adjuntar_firmado(idTraslado):
    if "user" not in session:
        flash("Se nesesita ingresar para acceder a esa ruta")
        return redirect("/ingresar")
    #TODO: revisar que sea pdf
    file = request.files["file"]
    #subir archivo
    dir = PDFS_DIR
    #renombrar archivo
    filename = file.filename
    sfilename = secure_filename(filename)
    file.save(os.path.join(
        dir, secure_filename(sfilename)
    ))
    os.rename(os.path.join(dir, sfilename), 
              os.path.join(dir, "traslado_" + str(idTraslado) + "_firmado.pdf"))
    return redirect("/traslado/listar_pdf/" + str(idTraslado))
