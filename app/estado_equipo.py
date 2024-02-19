from flask import Blueprint, render_template, request, url_for, redirect, flash
from db import mysql

estado_equipo = Blueprint('estado_equipo', __name__, template_folder='app/templates')

@estado_equipo.route('/estado_equipo')
def estadoEquipo():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM estado_equipo')
    data = cur.fetchall()
    cur.close()
    return render_template('estado_equipo.html', estado_equipo = data)

@estado_equipo.route('/add_estado_equipo', methods = ['POST'])
def add_estado_equipo():
    if request.method == 'POST':
        nombre_estado_equipo = request.form['nombre_estado_equipo']
        fecha_modificacion = request.form['fecha_modificacion']
        try:
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO estado_equipo (nombreEstado_equipo, FechaEstado_equipo) VALUES (%s, %s)', (nombre_estado_equipo, fecha_modificacion))
            mysql.connection.commit()
            flash('Estado de equipo agregado correctamente')
            return redirect(url_for('estado_equipo.estadoEquipo'))
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for('estado_equipo.estadoEquipo'))
    
#enviar datos a vista editar
@estado_equipo.route('/edit_estado_equipo/<id>', methods = ['POST', 'GET'])
def edit_estado_equipo(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM estado_equipo WHERE idEstado_equipo = %s', (id,))
        data = cur.fetchall()
        return render_template('editEstado_equipo.html', estado_equipo = data[0])
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('estado_equipo.estadoEquipo'))

#actualizar
@estado_equipo.route('/update_estado_equipo/<id>', methods = ['POST'])
def update_estado_equipo(id):
    if request.method == 'POST':
        nombre_estado_equipo = request.form['nombre_estado_equipo']
        fecha_modificacion = request.form['fecha_modificacion']
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
            UPDATE estado_equipo
            SET nombreEstado_equipo = %s,
                FechaEstado_equipo = %s
            WHERE idEstado_equipo = %s
            """, (nombre_estado_equipo, fecha_modificacion, id))
            mysql.connection.commit()
            flash('Estado de equipo actualizado correctamente')
            return redirect(url_for('estado_equipo.estadoEquipo'))
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for('estado_equipo.estadoEquipo'))

#eliminar    
@estado_equipo.route('/delete_estado_equipo/<id>', methods = ['POST', 'GET'])
def delete_estado_equipo(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM estado_equipo WHERE idEstado_equipo = %s', (id,))
        mysql.connection.commit()
        flash('Estado de equipo eliminado correctamente')
        return redirect(url_for('estado_equipo.estadoEquipo'))
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('estado_equipo.estadoEquipo'))
