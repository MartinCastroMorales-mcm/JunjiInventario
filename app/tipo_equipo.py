from flask import Blueprint, render_template, request, url_for, redirect,flash
from db import mysql
from funciones import getPerPage

tipo_equipo = Blueprint('tipo_equipo', __name__, template_folder='app/templates')

#ruta para enviar los datos y visualizar la pagina principal para tipo de equipo
@tipo_equipo.route('/tipo_equipo')
@tipo_equipo.route('/tipo_equipo/<page>')
def tipoEquipo(page = 1):
    perpage = getPerPage()
    offset = (int(page)-1) * perpage
    cur = mysql.connection.cursor()
    total = 0
    cur.execute('SELECT COUNT(*) FROM TIPO_EQUIPO')
    total = cur.fetchone()
    total = int(str(total).split(':')[1].split('}')[0])
    cur.execute('SELECT * FROM tipo_equipo LIMIT {} OFFSET {}'.format(perpage, offset))
    data = cur.fetchall()
    cur.execute('SELECT * FROM marca_equipo')
    marcas = cur.fetchall()
    page = int(page)
    return render_template('tipo_equipo.html', tipo_equipo = data, marcas=marcas,
                            page=page, lastpage = page < (total/perpage)+1)

#agrega un tipo de equipo
@tipo_equipo.route('/add_tipo_equipo', methods = ['POST'])
def add_tipo_equipo():
    if request.method == 'POST':
        nombreidTipoequipo = request.form['nombreTipo_equipo']
        id = request.form['nombre_marca_equipo']

        try:

            cur = mysql.connection.cursor()
            cur.execute("""
                        INSERT INTO tipo_equipo (nombreTipo_equipo, idMarca_Equipo) 
                        VALUES (%s, %s)""", (nombreidTipoequipo, id,))
            mysql.connection.commit()
            flash('Tipo de equipo agregado correctamente')
            return redirect(url_for('tipo_equipo.tipoEquipo'))
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for('tipo_equipo.tipoEquipo'))

#enviar datos a formulario editar para tipo de equipo segun el ide correspondiente
@tipo_equipo.route('/edit_tipo_equipo/<id>', methods = ['POST', 'GET'])
def edit_tipo_equipo(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM tipo_equipo WHERE idTipo_equipo = %s', (id,))
        data = cur.fetchall()
        cur.execute('SELECT * FROM marca_equipo')
        marca_data = cur.fetchall()
        return render_template('editTipo_equipo.html', tipo_equipo = data[0], 
                marca_equipo=marca_data)
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('tipo_equipo.tipoEquipo'))

#actualiza un elemento de tipo de equipo segun el id correspondiente
@tipo_equipo.route('/update_tipo_equipo/<id>', methods = ['POST'])
def update_tipo_equipo(id):
    if request.method == 'POST':
        nombre_tipo_equipo = request.form['nombre_tipo_equipo']
        id_marca = request.form['nombre_marca_equipo']
        try:             
            cur = mysql.connection.cursor()
            cur.execute(""" 
            UPDATE tipo_equipo
            SET nombreTipo_equipo = %s,
            idMarca_Equipo = %s
            WHERE idTipo_equipo = %s
            """, (nombre_tipo_equipo, id_marca, id))
            mysql.connection.commit()
            flash('Tipo de equipo actualizado correctamente')
            return redirect(url_for('tipo_equipo.tipoEquipo'))
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for('tipo_equipo.tipoEquipo'))

#elimina el registro segun el id
@tipo_equipo.route('/delete_tipo_equipo/<id>', methods = ['POST', 'GET'])
def delete_tipo_equipo(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM tipo_equipo WHERE idTipo_equipo = %s', (id,))
        mysql.connection.commit()
        flash('Tipo de equipo eliminado correctamente')
        return redirect(url_for('tipo_equipo.tipoEquipo'))
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('tipo_equipo.tipoEquipo'))
        