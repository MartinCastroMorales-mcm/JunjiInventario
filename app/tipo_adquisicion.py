from flask import Blueprint, render_template, request, url_for, redirect,flash
from db import mysql
from funciones import validarChar

tipo_adquisicion = Blueprint('tipo_adquisicion', __name__, template_folder='app/templates')

@tipo_adquisicion.route('/tipo_adquisicion')
def tipoAdquisicion():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM tipo_adquisicion')
    data = cur.fetchall()
    return render_template('tipo_adquisicion.html', tipo_adquisicion = data)

#agrega un registro para tipo de adquisicion
@tipo_adquisicion.route('/add_tipoa', methods = ['POST'])    
def add_tipoa():       
    if request.method == 'POST':
        nombre_tipoa = request.form['nombre_tipoa']   
        try:    
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO tipo_adquisicion (nombreTipo_adquisicion) VALUES(%s)', (nombre_tipoa,))
            mysql.connection.commit()
            flash('Tipo de adquisicion agregado exitosamente')
            return redirect(url_for('tipo_adquisicion.tipoAdquisicion'))
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for('tipo_adquisicion.tipoAdquisicion')) 

#enviar datos a formulario editar segun el id
@tipo_adquisicion.route('/edit_tipoa/<id>', methods = ['POST', 'GET'])
def edit_tipoa(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM tipo_adquisicion WHERE idTipo_adquisicion = %s', (id,))
        data = cur.fetchall()
        return render_template('editTipo_Adquisicion.html' , tipo_adquisicion = data[0])
    except Exception as e:
            flash(e.args[1])
            return redirect(url_for('tipo_adquisicion.tipoAdquisicion'))   

#actualiza el registro segun su id
@tipo_adquisicion.route('/update_tipoa/<id>', methods = ['POST'])
def actualizar_tipoa(id):
    if request.method == 'POST':
        nombre_tipoa = request.form['nombre_tipoa'] 
        try: 
            cur = mysql.connection.cursor()
            cur.execute(""" 
            UPDATE tipo_adquisicion 
            SET nombreTipo_adquisicion = %s                  
            WHERE idTipo_adquisicion = %s                                    
            """, (nombre_tipoa, id))
            mysql.connection.commit()
            flash('Tipo de adquisicion actualizado correctamente')
            return redirect(url_for('tipo_adquisicion.tipoAdquisicion'))
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for('tipo_adquisicion.tipoAdquisicion'))
        
#elimina un registro segun su id
@tipo_adquisicion.route('/delete_tipoa/<id>', methods = ['POST', 'GET'])
def delete_tipoa(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM tipo_adquisicion WHERE idTipo_adquisicion = %s', (id,))
        mysql.connection.commit()
        flash('Tipo de adquisicion eliminado correctamente')
        return redirect(url_for('tipo_adquisicion.tipoAdquisicion'))
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('tipo_adquisicion.tipoAdquisicion'))