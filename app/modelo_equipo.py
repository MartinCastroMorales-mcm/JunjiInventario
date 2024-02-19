from flask import Blueprint, flash, redirect, render_template, url_for, request
from db import mysql

modelo_equipo = Blueprint('modelo_equipo', __name__, template_folder='app/templates')

@modelo_equipo.route('/modelo_equipo')
def modeloEquipo():
    cur = mysql.connection.cursor()
    cur.execute(""" 
    SELECT moe.idModelo_Equipo, moe.nombreModeloequipo, moe.idMarca_equipo, mae.idMarca_Equipo, mae.nombreMarcaEquipo
    FROM modelo_equipo moe
    INNER JOIN marca_equipo mae on moe.idMarca_equipo = mae.idMarca_Equipo
    """)
    data = cur.fetchall()
    cur.execute('SELECT * FROM marca_equipo')
    mae_data = cur.fetchall()
    return render_template('modelo_equipo.html', modelo_equipo = data, marca_equipo = mae_data)

#agregar un regisro para modelo de equipo
@modelo_equipo.route('/add_modelo_equipo', methods = ['POST'])
def add_modelo_equipo():
    if request.method == 'POST':
        nombre_modelo_equipo = request.form['nombre_modelo_equipo']
        nombre_marca_equipo = request.form['nombre_marca_equipo']        
        try:      
            cur = mysql.connection.cursor()
            cur.execute('''
            INSERT INTO modelo_equipo (nombreModeloequipo, idMarca_equipo) VALUES (%s,%s)
            ''', (nombre_modelo_equipo, nombre_marca_equipo))
            cur.connection.commit()
            flash("Modelo agregado correctamente")
            return redirect(url_for('modelo_equipo.modeloEquipo'))
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for('modelo_equipo.modeloEquipo'))
#Envias datos a formulario editar
@modelo_equipo.route('/edit_modelo_equipo/<id>', methods = ['POST', 'GET'])
def edit_modelo_equipo(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute(""" 
        SELECT moe.idModelo_Equipo, moe.nombreModeloequipo, moe.idMarca_equipo, mae.idMarca_Equipo, mae.nombreMarcaEquipo
        FROM modelo_equipo moe
        INNER JOIN marca_equipo mae on moe.idMarca_equipo = mae.idMarca_Equipo
        WHERE idModelo_Equipo = %s
        """, (id,))
        data = cur.fetchall()
        cur.close()        
        curs = mysql.connection.cursor()
        curs.execute('SELECT * FROM marca_equipo')  
        mae_data = curs.fetchall()
        curs.close()      
        return render_template('editModelo_equipo.html', modelo_equipo = data[0], marca_equipo = mae_data)
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('modelo_equipo.modeloEquipo'))
    
#actualizar
@modelo_equipo.route('/update_modelo_equipo/<id>', methods = ['POST'])
def update_modelo_equipo(id):
    if request.method == 'POST':
        nombre_modelo_equipo = request.form['nombre_modelo_equipo']
        nombre_marca_equipo = request.form['nombre_marca_equipo']
        try:
            cur = mysql.connection.cursor()
            cur.execute('''
            UPDATE modelo_equipo 
            SET nombreModeloequipo = %s,
                idMarca_equipo = %s
            WHERE idModelo_Equipo = %s
            ''', (nombre_modelo_equipo, nombre_marca_equipo, id))
            mysql.connection.commit()
            flash('Modelo actualizado correctamente')
            return redirect(url_for('modelo_equipo.modeloEquipo'))
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for('modelo_equipo.modeloEquipo'))
        
#eliminar    
@modelo_equipo.route('/delete_modelo_equipo/<id>', methods = ['POST', 'GET'])
def delete_modelo_equipo(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM modelo_equipo WHERE idModelo_Equipo = %s', (id,))
        mysql.connection.commit()
        flash('Modelo eliminado correctamente')
        return redirect(url_for('modelo_equipo.modeloEquipo'))
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('modelo_equipo.modeloEquipo'))