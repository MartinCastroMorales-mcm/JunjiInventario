from flask import Blueprint, render_template, request, url_for, redirect, flash
from db import mysql
from funciones import getPerPage

Unidad = Blueprint('Unidad', __name__, template_folder = 'app/templates')

#ruta para poder enviar datos a la pagina principal de Unidad
@Unidad.route('/Unidad')
@Unidad.route('/Unidad/<page>')
def UNIDAD(page=1):
    page = int(page)
    perpage = getPerPage()
    offset = (page-1) * perpage
    cur = mysql.connection.cursor()
    cur.execute(""" 
        SELECT u.idUnidad, u.nombreUnidad, u.contactoUnidad,
               u.direccionUnidad, u.idComuna, co.nombreComuna,
               co.idComuna, COUNT(e.idEquipo) as num_equipos,
               mo.nombreModalidad
        FROM Unidad u
        INNER JOIN comuna co on u.idComuna = co.idComuna
        LEFT JOIN modalidad mo on mo.idModalidad = u.idModalidad
        LEFT JOIN equipo e on u.idUnidad = e.idUnidad
        GROUP BY u.idUnidad, u.nombreUnidad, u.contactoUnidad, u.direccionUnidad, u.idComuna, co.nombreComuna, co.idComuna
        LIMIT {} OFFSET {}
    
    """.format(perpage, offset))
    data = cur.fetchall()
    cur.execute('SELECT * FROM comuna')
    c_data = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM unidad")
    total = cur.fetchone()
    total = int(str(total).split(':')[1].split('}')[0])
    
    cur.execute("SELECT * FROM modalidad")
    modalidades_data = cur.fetchall()

   
    cur.close()
    return render_template('Unidad.html', Unidad = data, comuna = c_data, 
                           page=page, lastpage= page < (total/perpage)+1, Modalidades=modalidades_data)

#ruta y metodo para poder agregar una Unidad
@Unidad.route('/add_Unidad', methods = ['POST'])
def add_Unidad():
    if request.method == 'POST':
        nombreUnidad = request.form['nombreUnidad']
        contactoUnidad = request.form['contactoUnidad']
        direccionUnidad = request.form['direccionUnidad']
        idComuna= request.form['idComuna']
        idModalidad = request.form['idModalidad']
        try:
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO Unidad (nombreUnidad, contactoUnidad, direccionUnidad, idComuna, idModalidad) VALUES (%s, %s, %s, %s, %s)'
            , (nombreUnidad, contactoUnidad, direccionUnidad, idComuna, idModalidad))
            mysql.connection.commit()
            flash('Unidad agregada correctamente')
            return redirect(url_for('Unidad.UNIDAD'))
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for('Unidad.UNIDAD'))

#ruta para poder enviar los datos a la vista de edicion segun el id correspondiente
@Unidad.route('/edit_Unidad/<id>', methods = ['POST', 'GET'])
def edit_Unidad(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute(""" 
        SELECT u.idUnidad, u.nombreUnidad, u.contactoUnidad, u.direccionUnidad, u.idComuna, co.nombreComuna, co.idComuna
        FROM Unidad u
        INNER JOIN comuna co on u.idComuna = co.idComuna
        WHERE idUnidad = %s
        """, (id,))
        data = cur.fetchall()
        curs = mysql.connection.cursor()
        curs.execute('SELECT idComuna, nombreComuna FROM comuna')
        c_data = curs.fetchall()
        #poner la comuna en primero NO FUNDIONA
       # tmp = c_data[0]
       # for i in range(0, len(c_data)):
       #     if(data[0].idComuna == c_data[i].idComuna):
       #         c_data[0] = c_data[i]
       #         c_data[i] = tmp
       #         break
        cur.execute("SELECT * FROM modalidad")
        modalidades_data = cur.fetchall()
        curs.close()
        return render_template('editUnidad.html', Unidad = data[0], 
                comuna = c_data, Modalidades=modalidades_data)
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('Unidad.UNIDAD'))

#actualiza los datos de Unidad segun el id correspondiente   
@Unidad.route('/update_Unidad/<id>', methods = ['POST'])
def update_Unidad(id):
    if request.method == 'POST':
        codigo_Unidad = request.form['codigo_Unidad']
        nombreUnidad = request.form['nombreUnidad']
        contactoUnidad = request.form['contactoUnidad']
        direccionUnidad = request.form['direccionUnidad']
        idComuna = request.form['nombreComuna']
        idModalidad = request.form['idModalidad']

        try:
            cur = mysql.connection.cursor()
            cur.execute(""" 
            UPDATE Unidad
            SET idUnidad = %s,
                nombreUnidad = %s,
                contactoUnidad = %s,
                direccionUnidad = %s,
                idComuna = %s,
                idModalidad = %s
                WHERE idUnidad = %s
            """, (codigo_Unidad, nombreUnidad, contactoUnidad, 
                  direccionUnidad, idComuna, idModalidad ,id))
            mysql.connection.commit()
            flash('Unidad actualizada correctamente')
            return redirect(url_for('Unidad.UNIDAD'))
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for('Unidad.UNIDAD'))
        
#Elimina un registro segun el id
@Unidad.route('/delete_Unidad/<id>', methods = ['POST', 'GET'])
def delete_Unidad(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM Unidad WHERE idUnidad = %s', (id,))
        mysql.connection.commit()
        flash('Unidad eliminada correctamente')
        return redirect(url_for('Unidad.UNIDAD'))
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('Unidad.UNIDAD'))