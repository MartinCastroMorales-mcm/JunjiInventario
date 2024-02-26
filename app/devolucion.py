from flask import Blueprint, render_template, request, url_for, redirect, flash
from db import mysql
from fpdf import FPDF

devolucion = Blueprint('devolucion', __name__, template_folder='app/templates')

@devolucion.route('/devolucion')
def Devolucion():
    cur = mysql.connection.cursor()
    cur.execute(""" 
    SELECT d.idDevolucion, d.fechaDevolucion, d.observacionDevolucion, d.rutaactaDevolucion, d.ActivoDevolucion, d.rutFuncionario, f.rutFuncionario
    FROM devolucion d
    INNER JOIN funcionario f on d.rutFuncionario = f.rutFuncionario
    """)
    data = cur.fetchall()
    cur.execute('SELECT rutFuncionario FROM funcionario')
    f_data = cur.fetchall()
    return render_template('devolucion.html', devolucion = data, funcionario= f_data)

@devolucion.route('/add_devolucion', methods = ['POST'])
def add_estado_equipo():
    if request.method == 'POST':
       # idDevolucion = request.form['idDevolucion']
        fechaDevolucion = request.form['fechaDevolucion']
        observacionDevolucion= request.form['observacionDevolucion']
        rutaactaDevolucion= request.form['rutaactaDevolucion']
        ActivoDevolucion= request.form['ActivoDevolucion']
        rutFuncionario= request.form['rutFuncionario']
        try:
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO devolucion (fechaDevolucion,observacionDevolucion,rutaactaDevolucion,ActivoDevolucion,rutFuncionario) VALUES (%s, %s,%s,%s,%s)', 
                        ( fechaDevolucion,observacionDevolucion,rutaactaDevolucion,ActivoDevolucion,rutFuncionario))
            mysql.connection.commit()
            flash('Estado de equipo agregado correctamente')
            return redirect(url_for('devolucion.Devolucion'))
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for('devolucion.Devolucion'))
    
#enviar datos a vista editar
@devolucion.route('/edit_devolucion/<id>', methods = ['POST', 'GET'])
def edit_devolucion(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute(""" 
    SELECT d.idDevolucion, d.fechaDevolucion, d.observacionDevolucion, d.rutaactaDevolucion, d.ActivoDevolucion, d.rutFuncionario, f.rutFuncionario
    FROM devolucion d
    INNER JOIN funcionario f on d.rutFuncionario = f.rutFuncionario
    WHERE idDevolucion = %s""", (id,))
        data = cur.fetchall()
        cur.execute('SELECT rutFuncionario FROM funcionario')
        f_data = cur.fetchall()
        return render_template('editdevolucion.html', devolucion = data[0], funcionario= f_data)
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('devolucion.Devolucion'))

#actualizar
@devolucion.route('/update_devolucion/<id>', methods = ['POST'])
def update_devolucion(id):
    
    if request.method == 'POST':
        fechaDevolucion = request.form['fechaDevolucion']
        observacionDevolucion= request.form['observacionDevolucion']
        rutaactaDevolucion= request.form['rutaactaDevolucion']
        try:
            ActivoDevolucion= request.form['ActivoDevolucion']
        except:
            ActivoDevolucion = 0
        finally:
            rutFuncionario= request.form['rutFuncionario']
            try:
                cur = mysql.connection.cursor()
                cur.execute("""
                UPDATE devolucion
                SET fechaDevolucion = %s,
                    observacionDevolucion = %s,
                    rutaactaDevolucion = %s,
                    ActivoDevolucion = %s,
                    rutFuncionario = %s
                WHERE iddevolucion = %s
                """, (fechaDevolucion, observacionDevolucion,rutaactaDevolucion,ActivoDevolucion,rutFuncionario,id))
                mysql.connection.commit()
                flash('devolucion actualizado correctamente')
                return redirect(url_for('devolucion.Devolucion'))
            except Exception as e:
                flash(e.args[1])
                return redirect(url_for('devolucion.Devolucion'))

#eliminar    
@devolucion.route('/delete_devolucion/<id>', methods = ['POST', 'GET'])
def delete_devolucion(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM devolucion WHERE iddevolucion = %s', (id,))
        mysql.connection.commit()
        flash('devolucion eliminado correctamente')
        return redirect(url_for('devolucion.Devolucion'))
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('devolucion.Devolucion'))

@devolucion.route("/test1")
def crear_pdf():
    nombreFuncionario = "CRISTINA CARBAJAL FERNANDEZ" 
    nombreUnidad = "LA LEONORA"
    fechaAsignacion = "01-01-2024"
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
    titulo = "ACTA De Devolucion de Equipo Informatico N°" + str(1)

    pdf.set_font('times', '', 20)
    pdf.cell(0, 10, titulo, ln=True, align='C')
    pdf.set_font('times', '', 12)
    presentacion1 = "Por el presente se hace entrega a: "
    presentacion2 = "Dependiente de la Unidad: "
    presentacion22 = "En la Fecha: "
    presentacion3 = "Del siguiente equipo computacional"



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
        ("1", "IMPRESORA", "LENOVO", "1", "123", "137"),
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
    pdf.output('pdf_devolucion_1.pdf')
    return redirect(url_for("asignacion.Asignacion"))