from flask import Blueprint, render_template, request, url_for, redirect, flash, make_response
from db import mysql
from fpdf import FPDF
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
            print("###############")
            print(trasladoABorrar)
            print("###############")
            print(traslacion)
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


@traslado.route("/traslado/create_pdf")
def create_pdf():
    #(Orientacion, unidades, formato)
    #Orientacion P(portrait) o L(landscape)
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
            self.image('logo_inferior.jpg', 10, 8, 25)
            self.cell(0,0, "", ln=1)
            self.cell(0,0, "Junta Nacional de Jardines Infantiles-JUNJI", ln=1)
            self.cell(0,5, "OHiggins Poniente 77 Concepción. 041-2125541", ln=1) #problema con el caracter ’
            self.cell(0,5, "www.junji.cl", ln=1)



    pdf = PDF('P', 'mm', 'A4')

    pdf.add_page()


    titulo = "ACTA DE TRASLADO N° 'n'"
    parrafo_1 = "En Concepción 'fecha' se procede al traslado de bienes JUNJI de registro inventario desde 'Origen' hasta 'Destino' el siguiente detalle: "
    TABLE_DATA = (
    ("N°", "Articulos", "Serie", "Código Inventario", "Estado"),
    ("1", "EpsonI5190", "X5NS117668", "8042812", "MAL"),
    ("2", "EpsonI5190", "X5NS117668", "8042813", "MAL"),
    ("3", "EpsonI5190", "X5NS117668", "8042814", "MAL"),
    ("4", "EpsonI5190", "X5NS117668", "8042815", "MAL"),
    )
                
    pdf.set_font('times', '', 20)
    pdf.cell(0, 10, titulo, ln=True, align='C')            
            
    pdf.set_font('times', '', 12)
    pdf.multi_cell(0, 10, parrafo_1)
    with pdf.table() as table:
        for datarow in TABLE_DATA:
            row = table.row()
            for datum in datarow:
                row.cell(datum)
    parrafo_2 = "Se ecuentran X en Bien, Y Regular y Z Mal"
    pdf.multi_cell(0,10,parrafo_2, ln=True)
    parrafo_3 = "Nombre Encargado:____________________"
    pdf.multi_cell(0,10,parrafo_3, ln=True)
    parrafo_4 = "Numero de RUT:____________________"
    pdf.multi_cell(0,10,parrafo_4, ln=True)
    parrafo_5 = "Nombre Ministro de Fe:____________________"
    pdf.multi_cell(0,10,parrafo_5, ln=True)
    parrafo_6 = "Firma:____________________"
    pdf.multi_cell(0,10,parrafo_6, ln=True)
    pdf.output('pdf_1.pdf')
    return redirect(url_for('traslado.Traslado'))

