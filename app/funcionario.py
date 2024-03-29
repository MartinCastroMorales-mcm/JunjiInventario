from flask import Blueprint, request, render_template, flash, url_for, redirect
from db import mysql
from funciones import validarRut, getPerPage
funcionario = Blueprint('funcionario', __name__, template_folder='app/templates')

#envias los datos a la vista pricipal de funcionario
@funcionario.route('/funcionario')
@funcionario.route('/funcionario/<page>')
def Funcionario(page = 1):
    page = int(page)
    perpage = getPerPage()
    offset = (page -1) * perpage 
    cur = mysql.connection.cursor()
    cur.execute(""" 
    SELECT f.rutFuncionario, f.nombreFuncionario, f.cargoFuncionario, f.idUnidad, u.idUnidad, u.nombreUnidad
    FROM funcionario f
    INNER JOIN Unidad u on f.idUnidad = u.idUnidad
    LIMIT {} OFFSET {}
    """.format(perpage, offset))
    data = cur.fetchall()
    cur.execute('SELECT * FROM Unidad')
    ubi_data = cur.fetchall()
    cur.execute('SELECT COUNT(*) FROM funcionario')
    total = cur.fetchone()
    total = int(str(total).split(':')[1].split('}')[0])
    return render_template('funcionario.html', funcionario = data, 
                           Unidad = ubi_data, page=page, lastpage= page < (total/perpage)+1)


#agregar funcionario
@funcionario.route('/add_funcionario', methods = ['POST'])
def add_funcionario():
    if request.method == 'POST':
        rut_funcionario = request.form['rut_funcionario']
        nombre_funcionario = request.form['nombre_funcionario']
        cargo_funcionario = request.form['cargo_funcionario']
        codigo_Unidad = request.form['codigo_Unidad']

        if(not validarRut(rut_funcionario)):
            flash(f'Rut no es valido')
            return redirect(url_for('funcionario.Funcionario'))
        
    
        try:
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO funcionario (rutFuncionario, nombreFuncionario, cargoFuncionario, idUnidad) VALUES (%s, %s, %s, %s)', 
            (rut_funcionario, nombre_funcionario,cargo_funcionario, codigo_Unidad))
            mysql.connection.commit()
            flash('Funcionario agregado correctamente')
            return redirect(url_for('funcionario.Funcionario'))
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for('funcionario.Funcionario'))
    
#enviar datos a vista editar
@funcionario.route('/edit_funcionario/<id>', methods = ['POST', 'GET'])
def edit_funcionario(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute(""" 
        SELECT f.rutFuncionario, f.nombreFuncionario, f.cargoFuncionario, f.idUnidad, u.idUnidad
        FROM funcionario f
        INNER JOIN Unidad u on f.idUnidad = u.idUnidad
        WHERE rutFuncionario = %s
        """, (id,))
        data = cur.fetchall()
        cur.execute('SELECT idUnidad from Unidad')
        ubi_data = cur.fetchall()
        return render_template('editFuncionario.html', funcionario = data[0], Unidad = ubi_data)
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('funcionario.Funcionario'))

#actualizar funcionario por id
@funcionario.route('/update_funcionario/<id>', methods = ['POST'])
def update_funcionario(id):
    if request.method == 'POST':
        rut_funcionario = request.form['rut_funcionario']
        nombre_funcionario = request.form['nombre_funcionario']
        cargo_funcionario = request.form['cargo_funcionario']
        codigo_Unidad = request.form['codigo_Unidad']
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
            UPDATE funcionario
            SET rutFuncionario = %s,
                nombreFuncionario = %s,
                cargoFuncionario = %s,
                idUnidad = %s
            WHERE rutFuncionario = %s
            """, (rut_funcionario, nombre_funcionario, cargo_funcionario, codigo_Unidad, id))
            mysql.connection.commit()
            flash('Funcionario actualizado correctamente')
            return redirect(url_for('funcionario.Funcionario'))
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for('funcionario.Funcionario'))

#eliminar registro segun id
@funcionario.route('/delete_funcionario/<id>', methods = ['POST', 'GET'])
def delete_funcionario(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM funcionario WHERE rutFuncionario = %s', (id,))
        mysql.connection.commit()
        flash('Funcionario eliminado correctamente')
        return redirect(url_for('funcionario.Funcionario'))
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('funcionario.Funcionario'))

@funcionario.route("/funcionario/buscar_funcionario/<id>")
def buscar_funcionario(id):
    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT * 
    FROM funcionario f
    INNER JOIN Unidad u on f.idUnidad = u.idUnidad
    WHERE f.rutFuncionario = %s
    """, (id,))
    funcionarios = cur.fetchall()

    cur.execute("""
    SELECT *
    FROM unidad u 
                """)
    unidades = cur.fetchall()
    return render_template('funcionario.html', funcionario = funcionarios, 
                           Unidad = unidades, page=1, lastpage=True)
    pass