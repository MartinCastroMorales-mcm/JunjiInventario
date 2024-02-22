from flask import request, flash, render_template, url_for, redirect, Blueprint
from db import mysql

equipo = Blueprint('equipo', __name__, template_folder='app/templates')

#envia datos al formulario y tabla de equipo CAMBIA FK_IDCODIGO_PROVEEDOR
@equipo.route('/equipo')
def Equipo():
    cur = mysql.connection.cursor()
    cur.execute(""" 
    SELECT e.idEquipo, e.Cod_inventarioEquipo, e.Num_serieEquipo, e.ObservacionEquipo, e.codigoproveedor_equipo, e.macEquipo, e.imeiEquipo, e.numerotelefonicoEquipo,e.idTipo_Equipo ,e.idEstado_Equipo, e.idUnidad, e.idOrden_compra, e.idModelo_equipo,te.idTipo_equipo, te.nombreidTipoequipo, ee.idEstado_equipo, ee.nombreEstado_equipo, u.idUnidad, u.nombreUnidad, oc.idOrden_compra, oc.nombreOrden_compra,
    moe.idModelo_equipo, moe.nombreModeloequipo, f.nombreFuncionario
    FROM equipo e
    INNER JOIN tipo_equipo te on te.idTipo_equipo = e.idTipo_Equipo
    INNER JOIN estado_equipo ee on ee.idEstado_equipo = e.idEstado_Equipo
    INNER JOIN Unidad u on u.idUnidad = e.idUnidad
    INNER JOIN orden_compra oc on oc.idOrden_compra = e.idOrden_compra
    INNER JOIN modelo_equipo moe on moe.idModelo_Equipo = e.idModelo_equipo
    INNER JOIN asignacion a on a.idEquipo = e.idEquipo
    INNER JOIN funcionario f on f.rutfuncionario = a.rutfuncionario
    """)
    data = cur.fetchall()
    cur.execute('SELECT * FROM tipo_equipo')
    tipoe_data = cur.fetchall()
    cur.execute('SELECT idEstado_equipo, nombreEstado_equipo FROM estado_equipo')
    estadoe_data = cur.fetchall()
    cur.execute('SELECT idUnidad, nombreUnidad FROM Unidad')
    ubi_data = cur.fetchall()
    cur.execute('SELECT idOrden_compra, nombreOrden_compra FROM orden_compra')
    ordenc_data = cur.fetchall()
    cur.execute('SELECT idModelo_Equipo, nombreModeloequipo FROM modelo_equipo')
    modeloe_data = cur.fetchall()  

    return render_template('equipo.html', equipo = data, tipo_equipo = tipoe_data, estado_equipo = estadoe_data, orden_compra = ordenc_data, 
    Unidad = ubi_data, modelo_equipo = modeloe_data)

#agrega registro para id
@equipo.route('/add_equipo', methods = ['POST'])
def add_equipo():
    if request.method == 'POST':
        codigo_inventario = request.form['codigo_inventario']
        numero_serie = request.form['numero_serie']
        observacion_equipo = request.form['observacion_equipo']
        codigoproveedor = request.form['codigoproveedor']
        mac = request.form['mac']
        imei = request.form['imei']
        numero = request.form['numero']
        nombre_tipo_equipo = request.form['nombre_tipo_equipo']
        nombre_estado_equipo = request.form['nombre_estado_equipo']
        codigo_Unidad = request.form['codigo_Unidad']
        nombre_orden_compra = request.form['nombre_orden_compra']
        nombre_modelo_equipo = request.form['nombre_modelo_equipo']
        try:
            cur = mysql.connection.cursor()
            cur.execute(""" INSERT INTO equipo (Cod_inventarioEquipo, Num_serieEquipo, ObservacionEquipo,codigoproveedor_equipo,macEquipo,
                        imeiEquipo , numerotelefonicoEquipo , idTipo_Equipo, idEstado_Equipo, idUnidad, idOrden_compra, idModelo_equipo) 
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (codigo_inventario, numero_serie, observacion_equipo, codigoproveedor,mac,imei,numero, nombre_tipo_equipo, nombre_estado_equipo, codigo_Unidad, nombre_orden_compra, nombre_modelo_equipo))
            mysql.connection.commit()
            flash('Equipo agregado correctamente')
            return redirect(url_for('equipo.Equipo'))
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for('equipo.Equipo'))
#envia datos al formulario editar segun id
@equipo.route('/edit_equipo/<id>', methods = ['POST', 'GET'])
def edit_equipo(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute(""" 
           SELECT e.idEquipo, e.Cod_inventarioEquipo, e.Num_serieEquipo, e.ObservacionEquipo, e.codigoproveedor_equipo, e.macEquipo, e.imeiEquipo, e.numerotelefonicoEquipo,e.idTipo_Equipo ,e.idEstado_Equipo, e.idUnidad, e.idOrden_compra, e.idModelo_equipo,te.idTipo_equipo, te.nombreidTipoequipo, ee.idEstado_equipo, ee.nombreEstado_equipo, u.idUnidad, u.nombreUnidad, oc.idOrden_compra, oc.nombreOrden_compra,
        moe.idModelo_equipo, moe.nombreModeloequipo
        FROM equipo e
        INNER JOIN tipo_equipo te on te.idTipo_equipo = e.idTipo_Equipo
        INNER JOIN estado_equipo ee on ee.idEstado_equipo = e.idEstado_Equipo
        INNER JOIN Unidad u on u.idUnidad = e.idUnidad
        INNER JOIN orden_compra oc on oc.idOrden_compra = e.idOrden_compra
        INNER JOIN modelo_equipo moe on moe.idModelo_Equipo = e.idModelo_equipo
        WHERE idEquipo = %s
        """, (id,))
        data = cur.fetchall()
        cur.execute('SELECT * FROM tipo_equipo')
        tipoe_data = cur.fetchall()
        cur.execute('SELECT idEstado_equipo, nombreEstado_equipo FROM estado_equipo')
        estadoe_data = cur.fetchall()
        cur.execute('SELECT idUnidad, nombreUnidad FROM Unidad')
        ubi_data = cur.fetchall()
        cur.execute('SELECT idOrden_compra, nombreOrden_compra FROM orden_compra')
        ordenc_data = cur.fetchall()
        cur.execute('SELECT idModelo_Equipo, nombreModeloequipo FROM modelo_equipo')
        modeloe_data = cur.fetchall()  
        return render_template('editEquipo.html', equipo = data[0], tipo_equipo = tipoe_data, estado_equipo = estadoe_data, orden_compra = ordenc_data, 
        Unidad = ubi_data, modelo_equipo = modeloe_data)
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('equipo.Equipo'))
    
#actualiza registro a traves de id correspondiente
@equipo.route('/update_equipo/<id>', methods = ['POST'])
def update_equipo(id):
    if request.method == 'POST':
        codigo_inventario = request.form['codigo_inventario']
        numero_serie = request.form['numero_serie']
        observacion_equipo = request.form['observacion_equipo']
        codigoproveedor = request.form['codigoproveedor']
        mac = request.form['mac']
        imei = request.form['imei']
        numero = request.form['numero']
        nombre_tipo_equipo = request.form['nombre_tipo_equipo']
        nombre_estado_equipo = request.form['nombre_estado_equipo']
        codigo_Unidad = request.form['codigo_Unidad']
        nombre_orden_compra = request.form['nombre_orden_compra']
        nombre_modelo_equipo = request.form['nombre_modelo_equipo']
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
            UPDATE equipo
            SET Cod_inventarioEquipo = %s,
                Num_serieEquipo = %s,
                ObservacionEquipo = %s,
                codigoproveedor_equipo =%s,
                macEquipo=%s,
                imeiEquipo=%s,
                numerotelefonicoEquipo=%s,
                idTipo_Equipo = %s,
                idEstado_Equpo = %s,
                idUnidad = %s,
                idOrden_compra = %s,
                idModelo_equipo = %s,
                WHERE idEquipo = %s
            """, (codigo_inventario, numero_serie, observacion_equipo,codigoproveedor, mac,imei, numero, nombre_tipo_equipo, nombre_estado_equipo, codigo_Unidad, nombre_orden_compra, nombre_modelo_equipo, id))
            mysql.connection.commit()
            flash('Equipo actualizado correctamente')
            return redirect(url_for('equipo.Equipo'))
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for('equipo.Equipo'))

#elimina registro a traves de id correspondiente
@equipo.route('/delete_equipo/<id>', methods = ['POST', 'GET'])
def delete_equipo(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM equipo WHERE idEquipo = %s', (id,))
        mysql.connection.commit()
        flash('Equipo eliminado correctamente')
        return redirect(url_for('equipo.Equipo'))
    except Exception as e:
        flash(e.args[1])
        return redirect(url_for('equipo.Equipo'))

@equipo.route('/mostrar_asociados_traslado/<idTraslado>')
def mostrar_asociados_traslado(idTraslado):
    cur = mysql.connection.cursor()
    cur.execute(""" 
    SELECT e.idEquipo, e.Cod_inventarioEquipo, e.Num_serieEquipo, e.ObservacionEquipo, e.codigoproveedor_equipo, e.macEquipo, e.imeiEquipo, e.numerotelefonicoEquipo,e.idTipo_Equipo ,e.idEstado_Equipo, e.idUnidad, e.idOrden_compra, e.idModelo_equipo,te.idTipo_equipo, te.nombreidTipoequipo, ee.idEstado_equipo, ee.nombreEstado_equipo, u.idUnidad, u.nombreUnidad, oc.idOrden_compra, oc.nombreOrden_compra,
    moe.idModelo_equipo, moe.nombreModeloequipo, f.nombreFuncionario
    FROM equipo e
    INNER JOIN tipo_equipo te on te.idTipo_equipo = e.idTipo_Equipo
    INNER JOIN estado_equipo ee on ee.idEstado_equipo = e.idEstado_Equipo
    INNER JOIN Unidad u on u.idUnidad = e.idUnidad
    INNER JOIN orden_compra oc on oc.idOrden_compra = e.idOrden_compra
    INNER JOIN modelo_equipo moe on moe.idModelo_Equipo = e.idModelo_equipo
    INNER JOIN asignacion a on a.idEquipo = e.idEquipo
    INNER JOIN funcionario f on f.rutfuncionario = a.rutfuncionario
    INNER JOIN traslacion tras on tras.idEquipo = e.idEquipo
    WHERE tras.idTraslado = %s
    """, (idTraslado,))
    data = cur.fetchall()
    cur.execute('SELECT * FROM tipo_equipo')
    tipoe_data = cur.fetchall()
    cur.execute('SELECT idEstado_equipo, nombreEstado_equipo FROM estado_equipo')
    estadoe_data = cur.fetchall()
    cur.execute('SELECT idUnidad, nombreUnidad FROM Unidad')
    ubi_data = cur.fetchall()
    cur.execute('SELECT idOrden_compra, nombreOrden_compra FROM orden_compra')
    ordenc_data = cur.fetchall()
    cur.execute('SELECT idModelo_Equipo, nombreModeloequipo FROM modelo_equipo')
    modeloe_data = cur.fetchall()  

    return render_template('equipo.html', equipo = data, tipo_equipo = tipoe_data, estado_equipo = estadoe_data, orden_compra = ordenc_data, 
    Unidad = ubi_data, modelo_equipo = modeloe_data)

@equipo.route('/mostrar_asociados_unidad/<idUnidad>')
def mostrar_asociados_unidad(idUnidad):
    cur = mysql.connection.cursor()
    cur.execute(""" 
    SELECT e.idEquipo, e.Cod_inventarioEquipo, e.Num_serieEquipo, e.ObservacionEquipo, e.codigoproveedor_equipo, e.macEquipo, e.imeiEquipo, e.numerotelefonicoEquipo,e.idTipo_Equipo ,e.idEstado_Equipo, e.idUnidad, e.idOrden_compra, e.idModelo_equipo,te.idTipo_equipo, te.nombreidTipoequipo, ee.idEstado_equipo, ee.nombreEstado_equipo, u.idUnidad, u.nombreUnidad, oc.idOrden_compra, oc.nombreOrden_compra,
    moe.idModelo_equipo, moe.nombreModeloequipo, f.nombreFuncionario
    FROM equipo e
    INNER JOIN tipo_equipo te on te.idTipo_equipo = e.idTipo_Equipo
    INNER JOIN estado_equipo ee on ee.idEstado_equipo = e.idEstado_Equipo
    INNER JOIN Unidad u on u.idUnidad = e.idUnidad
    INNER JOIN orden_compra oc on oc.idOrden_compra = e.idOrden_compra
    INNER JOIN modelo_equipo moe on moe.idModelo_Equipo = e.idModelo_equipo
    INNER JOIN asignacion a on a.idEquipo = e.idEquipo
    INNER JOIN funcionario f on f.rutfuncionario = a.rutfuncionario
    WHERE e.idUnidad = %s
    """, (idUnidad,))
    data = cur.fetchall()
    cur.execute('SELECT * FROM tipo_equipo')
    tipoe_data = cur.fetchall()
    cur.execute('SELECT idEstado_equipo, nombreEstado_equipo FROM estado_equipo')
    estadoe_data = cur.fetchall()
    cur.execute('SELECT idUnidad, nombreUnidad FROM Unidad')
    ubi_data = cur.fetchall()
    cur.execute('SELECT idOrden_compra, nombreOrden_compra FROM orden_compra')
    ordenc_data = cur.fetchall()
    cur.execute('SELECT idModelo_Equipo, nombreModeloequipo FROM modelo_equipo')
    modeloe_data = cur.fetchall()  

    return render_template('equipo.html', equipo = data, tipo_equipo = tipoe_data, estado_equipo = estadoe_data, orden_compra = ordenc_data, 
    Unidad = ubi_data, modelo_equipo = modeloe_data)
    
@equipo.route("/equipo_detalles")
def equipo_detalles():
    return render_template('equipo_detalles.html')