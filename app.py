from flask import Flask, render_template, request, url_for, redirect, flash
from flask_mysqldb import MySQL
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

app.secret_key = os.getenv('SECRET_KEY')
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT', 3306))

# Configuración de SSL
app.config['MYSQL_SSL_CA'] = os.getenv('MYSQL_SSL_CA_PATH')

mysql = MySQL(app)
socketio = SocketIO(app)

@app.route('/')
def index():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM tareas')
    data = cursor.fetchall()
    return render_template('index.html', tareas = data)

@app.route('/admin')
def admin():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM tareas')
    data = cursor.fetchall()
    return render_template('admin.html',tareas = data)

@app.route('/edit/<string:id>')
def get_task(id):
    cursor = mysql.connection.cursor()
    cursor.execute(f'SELECT * FROM tareas WHERE id = {id}')
    data = cursor.fetchall()
    return render_template('edit_task.html', tarea = data[0])

@app.route('/update/<string:id>', methods = ['POST'])
def update_task(id):
    if request.method == 'POST':
        titulo = request.form['titulo']
        materia = request.form['materia']
        detalles = request.form['detalle']
        vencimiento = request.form['vencimiento']

        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE tareas 
            SET titulo = %s,
                materia = %s,
                detalles = %s,
                vencimiento = %s
            WHERE id = %s
        """,(titulo, materia, detalles, vencimiento, id ))
        flash('Se actualizó la tarea correctamente')
        mysql.connection.commit()
        return redirect(url_for('admin'))

@app.route('/delete/<string:id>')
def delete(id):
    cursor = mysql.connection.cursor()
    cursor.execute(f'DELETE FROM tareas WHERE id = {id}')
    mysql.connection.commit()
    flash('Se eliminó la tarea')
    return redirect(url_for('admin'))

@app.route('/add_task', methods=['POST'])
def add_task():
    if request.method == 'POST':
        titulo = request.form['titulo']
        materia = request.form['materia']
        vencimiento = request.form['vencimiento']
        detalle = request.form['detalle']
        print(titulo, materia, vencimiento, detalle, sep="\n")
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO tareas (titulo, materia, detalles, vencimiento) VALUES (%s, %s, %s, %s)", (titulo, materia, detalle, vencimiento))
        mysql.connection.commit()
        flash('Tarea agregada exitosamente!')
        socketio.emit('nueva_tarea', {'titulo': titulo, 'materia': materia})
        return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8070))
    app.run(port=port)