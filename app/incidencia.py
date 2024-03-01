from flask import Blueprint, render_template, request, url_for, redirect, flash, make_response, send_file
from db import mysql
from fpdf import FPDF
from funciones import getPerPage
import os
import shutil 
from werkzeug.utils import secure_filename
incidencia = Blueprint("incidencia", __name__, template_folder="app/templates")
PDFS_INCIDENCIAS = r'C:\Users\Junji\Downloads\Junji_inventario-main1\Junji_inventario-main\Junji_inventario-main\app\pdf'

#pestaña principal de incidencias
@incidencia.route("/incidencia")
@incidencia.route("/incidencia/<page>")
def Incidencia(page = 1):
    page = int(page)
    perpage = getPerPage()
    offset = (page -1) * perpage
    cur = mysql.connection.cursor()
    cur.execute(
        """
                SELECT i.idIncidencia, i.nombreIncidencia, i.observacionIncidencia,
                    i.rutaactaIncidencia, i.fechaIncidencia, i.idEquipo,
                    e.cod_inventarioEquipo, e.Num_serieEquipo, te.nombreidTipoequipo, me.nombreModeloEquipo
                FROM incidencia i 
                INNER JOIN equipo e on i.idEquipo = e.idEquipo
                INNER JOIN tipo_equipo te on e.idTipo_Equipo = te.idTipo_Equipo
                INNER JOIN modelo_equipo me on e.idModelo_Equipo = me.idModelo_Equipo
                LIMIT {} OFFSET {}
        """.format(perpage, offset)
    )
    data = cur.fetchall()
    cur.execute('SELECT COUNT(*) FROM incidencia')
    total = cur.fetchone()
    total = int(str(total).split(':')[1].split('}')[0])
    unidades = cur.fetchall()
    return render_template("incidencia.html", Incidencia=data,
                           page=page, lastpage= page < (total/perpage)+1)

#form que se accede desde equipo para crear incidencia
@incidencia.route("/incidencia/form/<idEquipo>")
def incidencia_form(idEquipo):
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT *
                FROM equipo e
                WHERE e.idEquipo = idEquipo
                """)
    equipo = cur.fetchone()
    return render_template("add_incidencia.html", equipo=equipo)

#recibe el form de la incidencia y crea la fila de una incidencia en la bbdd, redirige a la pestaña de agregar documentos
@incidencia.route("/incidencia/add_incidencia", methods = ['POST'])
def add_incidencia():
    if request.method == "POST":
         nombreIncidencia = request.form['nombreIncidencia']
         observacionIncidencia = request.form['observacionIncidencia']
         fechaIncidencia = request.form['fechaIncidencia']
         idEquipo = request.form['idEquipo']
         cur = mysql.connection.cursor()
         cur.execute("""
                    INSERT INTO incidencia (
                        nombreIncidencia,
                        observacionIncidencia,
                        rutaActaIncidencia,
                        fechaIncidencia,
                        idEquipo
                        )
                     VALUES (%s, %s, %s, %s, %s)
                    """, (nombreIncidencia, observacionIncidencia, "ruta", fechaIncidencia, idEquipo,)
                    )
         mysql.connection.commit()
         flash("Incidencia Agregada Corectamante")
         idIncidencia = cur.lastrowid 
         cur.execute("""
                    SELECT *
                     FROM incidencia i
                     WHERE i.idIncidencia = %s
                     """, (idIncidencia,))
         obj_incidencia = cur.fetchone()
    return redirect("/incidencia/listar_pdf/" + str(obj_incidencia['idIncidencia']))

@incidencia.route("/incidencia/delete_incidencia/<id>")
def delete_incidencia(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM incidencia WHERE idIncidencia = %s", (id,))
    mysql.connection.commit()
    flash("Incidencia eliminada correctamente")
    return redirect(url_for("incidencia.Incidencia"))

@incidencia.route("/incidencia/edit_incidencia/<id>", methods=["GET", "POST"])
def edit_incidencia(id):
    cur = mysql.connection.cursor()
    cur.execute("""
            SELECT *
            FROM incidencia
            WHERE incidencia.idIncidencia = %s
                """, (id,))
    incidencia = cur.fetchone()
    return render_template("edit_incidencia.html", incidencia=incidencia)

     
@incidencia.route("/incidencia/update_incidencia/<id>", methods=["POST"])
def update_incidencia(id):
   nombreIncidencia = request.form['nombreIncidencia'] 
   ObservacionIncidencia = request.form['observacionIncidencia']
   fechaIncidencia = request.form['fechaIncidencia']

   
   cur = mysql.connection.cursor()
   cur.execute("""
        UPDATE incidencia
        SET nombreIncidencia = %s,
            observacionIncidencia = %s,
            fechaIncidencia = %s
        WHERE idIncidencia = %s
               """, (nombreIncidencia, ObservacionIncidencia, fechaIncidencia, id)) 
   mysql.connection.commit()
   flash("Incidencia actualizada correctamente")
   return redirect(url_for("incidencia.Incidencia"))
 
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@incidencia.route("/incidencia/adjuntar_pdf/<id>", methods=["POST"])
def adjuntar_pdf(id):
    #guardar pdf
    file = request.files["file"]
    dir = PDFS_INCIDENCIAS
    carpeta_incidencias = os.path.join(dir, "incidencia_" + str(id))
    try:
        os.mkdir(os.path.join(dir, carpeta_incidencias))
    except:
        pass
    fileName = file.filename
    file.save(os.path.join(
        carpeta_incidencias,
        secure_filename(fileName)
    ))
    
    #obtener incidencia

    cur = mysql.connection.cursor()
    cur.execute("""
                    SELECT *
                     FROM incidencia i
                     WHERE i.idIncidencia = %s
                """, (id,))
    obj_incidencia = cur.fetchone()
    #redirigir a si add_pdf_incidencia
    flash("se subio correctamente")
    return redirect("/incidencia/listar_pdf/" + str(obj_incidencia['idIncidencia']))

@incidencia.route("/incidencia/listar_pdf/<id>")
def listar_pdf(id):
    #verificar la existencia de la carpeta incidencia
    #try:
    dir = PDFS_INCIDENCIAS
    carpeta_incidencias = os.path.join(dir, "incidencia_" + str(id))
    if(not os.path.exists(carpeta_incidencias)):
        return render_template("mostrar_pdf_incidencia.html", idIncidencia=id, documentos=())

        
    #except:
        #flash("ERROR")
        #return redirect(url_for("incidencia.Incidencia"))

    #obtener un listado de los nombres de la carpeta
    #generar las tuplas tal que se pueda abrir en otra ventana
    pdfTupla = ()
    for fileName in os.listdir(carpeta_incidencias):
        print(fileName)
        if(fileName.endswith('.pdf') or fileName.endswith('.PDF')): #¿pueden existir .pDf?, se podria arreglar con un split . y la segunda parte toLower asi siempre en minuscula
            pdfTupla = pdfTupla + (fileName,)
    #print(pdfTupla)
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT *
                FROM equipo e
                WHERE e.idEquipo = %s
                """, (id,))
    data_equipo = cur.fetchone()


    return render_template("mostrar_pdf_incidencia.html", idIncidencia=id, documentos=pdfTupla, equipo=data_equipo)
            
@incidencia.route("/incidencia/mostrar_pdf/<id>/<nombrePdf>")
def mostrar_pdf(id, nombrePdf):
    try:
        nombrePdf = nombrePdf
        dir = PDFS_INCIDENCIAS
        #busca la carpeta de la incidencia asociada a la id
        carpeta_incidencias = os.path.join(dir, "incidencia_" + str(id))
        file = os.path.join(carpeta_incidencias, nombrePdf)
        return send_file(file, as_attachment=True)
    except:
        flash("no se encontro pdf")
        return redirect(url_for("insicencia.Incidencia"))
#def create_pdf(Incidencia):
    
    #class PDF(FPDF):
        #def header(self):
            ##logo
            ##imageUrl = url_for('static', filename='img/logo_junji.png')
            ##print(imageUrl)
            #self.image('logo_junji.png', 10, 8, 25)
            ##font
            #self.set_font('times', 'B', 12)
            #self.set_text_color(170,170,170)
            ##Title
            #self.cell(0, 30, '', border=False, ln=1, align='L')
            #self.cell(0, 5, 'JUNTA NACIONAL', border=False, ln=1, align='L')
            #self.cell(0, 5, 'INFANTILES', border=False, ln=1, align='L')
            #self.cell(0, 5, 'Unidad de Inventarios', border=False, ln=1, align='L')
            ##line break
            #self.ln(10)
        
        #def footer(self):
            #self.set_y(-30)
            #self.set_font('times', 'B', 12)
            #self.set_text_color(170,170,170)
            #self.cell(0,0, "", ln=1)
            #self.cell(0,0, "Junta Nacional de Jardines Infantiles-JUNJI", ln=1)
            #self.cell(0,12, "OHiggins Poniente 77 Concepción. 041-2125541", ln=1) #problema con el caracter ’
            #self.cell(0,12, "www.junji.cl", ln=1)
     
    #pdf = PDF('P', 'mm', 'A4')
    #pdf.add_page()


    #nombrePdf = "incidencia_" + str(Incidencia['idIncidencia']) + ".pdf"
    #pdf.output(nombrePdf)
    #shutil.move(nombrePdf, "app/pdf")
    #return

#@incidencia.route("/incidencia/mostrar_pdf/<id>")
#def mostrar_pdf(id):
    #pass
    
