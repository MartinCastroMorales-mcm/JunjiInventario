from flask import Blueprint, render_template, request, url_for, redirect,flash
from db import mysql
from funciones import validarChar

tipo_equipo = Blueprint('tipo_equipo', __name__, template_folder='app/templates')

#ruta para enviar los datos y visualizar la pagina principal para tipo de equipo
@tipo_equipo.route('/tipo_equipo')
def tipoEquipo():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM tipo_equipo')
    data = cur.fetchall()
    return render_template('tipo_equipo.html', tipo_equipo = data)

#agrega un tipo de equipo
@tipo_equipo.route('/add_tipo_equipo', methods = ['POST'])
def add_tipo_equipo():
    if request.method == 'POST':
        nombreidTipoequipo = request.form['nombreidTipoequipo']
        try:
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO tipo_equipo (nombreidTipoequipo) VALUES (%s)', (nombreidTipoequipo,))
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
        return render_template('editTipo_equipo.html', tipo_equipo = data[0])
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('tipo_equipo.tipoEquipo'))

#actualiza un elemento de tipo de equipo segun el id correspondiente
@tipo_equipo.route('/update_tipo_equipo/<id>', methods = ['POST'])
def update_tipo_equipo(id):
    if request.method == 'POST':
        nombre_tipo_equipo = request.form['nombre_tipo_equipo']
        try:             
            cur = mysql.connection.cursor()
            cur.execute(""" 
            UPDATE tipo_equipo
            SET nombreidTipoequipo = %s
            WHERE idTipo_equipo = %s
            """, (nombre_tipo_equipo, id))
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
        