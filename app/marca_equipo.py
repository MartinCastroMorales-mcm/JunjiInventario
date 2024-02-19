from flask import Blueprint, request, flash, render_template, redirect, url_for, g
from db import mysql

marca_equipo = Blueprint('marca_equipo', __name__, template_folder= 'app/templates')
@marca_equipo.route('/')
@marca_equipo.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@marca_equipo.route('/marca_equipo')
@marca_equipo.route('/marca_equipo/<order>')
@marca_equipo.route('/marca_equipo/<order>')
def marcaEquipo(order=1):
    #flash(order)
    query = 'SELECT * FROM marca_equipo '
    #perpage = 2
    #startpage = page * perpage
    if(order == "ASC"):
        #flash("test")
        query += "ORDER BY marca_equipo.nombreMarcaEquipo" 
    elif(order == "DESC"):
        query += "ORDER BY marca_equipo.nombreMarcaEquipo DESC"
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    
    return render_template('marca_equipo.html', marca_equipo = data, agregar= False)

#abrir formulario agregar
@marca_equipo.route('/try_add_marca_equipo')
def try_add_marca_equipo():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM marca_equipo')
    data = cur.fetchall()
    return render_template('marca_equipo.html', marca_equipo = data, agregar= True)

#agregar
@marca_equipo.route('/add_marca_equipo', methods = ['POST'])
def add_marca_equipo():
    if request.method == 'POST':
        nombre_marca_equipo = request.form['nombre_marca_equipo']
        try:
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO marca_equipo (nombreMarcaEquipo) VALUES (%s)', (nombre_marca_equipo,))
            mysql.connection.commit()
            flash('Marca agregada correctamente')
            return redirect(url_for('marca_equipo.marcaEquipo'))  
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for('marca_equipo.marcaEquipo'))
        
#enviar datos a vista editar
@marca_equipo.route('/edit_marca_equipo/<id>', methods = ['POST', 'GET'])
def edit_marca_equipo(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM marca_equipo WHERE idMarca_Equipo = %s', (id,))
        data = cur.fetchall()
        return render_template('editMarca_equipo.html', marca_equipo = data[0])
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('marca_equipo.marcaEquipo'))

#actualizar
@marca_equipo.route('/update_marca_equipo/<id>', methods = ['POST'])
def update_marca_equipo(id):
    if request.method == 'POST':
        nombre_marca_equipo = request.form['nombre_marca_equipo']
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
            UPDATE marca_equipo
            SET nombreMarcaEquipo = %s
            WHERE idMarca_Equipo = %s
            """, (nombre_marca_equipo, id))
            mysql.connection.commit()
            flash('Marca actualizada correctamente')
            return redirect(url_for('marca_equipo.marcaEquipo'))
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for('marca_equipo.marcaEquipo'))

#eliminar    
@marca_equipo.route('/marca_equipo/delete_marca_equipo/<id>', methods = ['POST', 'GET'])
def delete_marca_equipo(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM marca_equipo WHERE idMarca_equipo = %s', (id,))
        mysql.connection.commit()
        flash('Marca eliminada correctamente')
        return redirect(url_for('marca_equipo.marcaEquipo'))
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('marca_equipo.marcaEquipo'))
    
    

