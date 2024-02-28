from flask import Blueprint, render_template, request, url_for, redirect, flash, make_response, send_file
from db import mysql
from fpdf import FPDF
from funciones import getPerPage
import os
import shutil 
incidencia = Blueprint("incidencia", __name__, template_folder="app/templates")


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
                    e.cod_inventarioEquipo, e.Num_serieEquipo, te.nombreidTipoequipo
                FROM incidencia i 
                INNER JOIN equipo e on i.idEquipo = e.idEquipo
                INNER JOIN tipo_equipo te on e.idTipo_Equipo = te.idTipo_Equipo
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

@incidencia.route("/incidencia/form/<idEquipo>")
def incidencia_form(idEquipo):
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT *
                FROM equipo e
                WHERE e.idEquipo = idEquipo
                """)
    equipo = cur.fetchone()
    return render_template("edit_incidencia.html", equipo=equipo)

@incidencia.route("/incidencia/add_incidencia", methods = ['POST'])
def add_incidencia():
    if request.method == "POST":
         nombreIncidencia = request.form['nombreIncidencia']
         observacionIncidencia = request.form['observacionIncidencia']
         fechaIncidencia = request.form['fechaIncidencia']
         idEquipo = request.form['idEquipo']
         print("#############################")
         print("id: " + idEquipo)

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
                


    return redirect(url_for('equipo.Equipo'))

@incidencia.route("/incidencia/delete_incidencia/<id>")
def delete_incidencia(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM incidencia WHERE idIncidencia = %s", (id,))
    mysql.connection.commit()
    flash("Incidencia eliminada correctamente")
    return redirect(url_for("incidencia.Incidencia"))

@incidencia.route("/incidencia/edit_incidencia/<id>", methods=["POST"])
def edit_incidencia(id):
    cur = mysql.connection.cursor()
    cur.execute("""
            SELECT *
            FROM incidencia
            WHERE incidencia.idIncidencia = %s
                """, (id,))
    incidencia = cur.fetchone()
    
     

def create_pdf(Incidencia):
    
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


    nombrePdf = "incidencia_" + str(Incidencia['idIncidencia']) + ".pdf"
    pdf.output(nombrePdf)
    shutil.move(nombrePdf, "app/pdf")
    return

@incidencia.route("/incidencia/mostrar_pdf/<id>")
def mostrar_pdf(id):
    pass
    
