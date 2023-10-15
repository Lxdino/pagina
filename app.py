import openai
import config
from rich import print
import os
from flask import Flask
from flask import render_template, request, redirect, session
from flaskext.mysql import MySQL
from flask import send_from_directory


app = Flask(__name__)
app.secret_key = 'develoteca'
mysql = MySQL()

openai.api_key = config.api_key

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'sitio'
app.config['MYSQL_DATABASE_DB1'] = 'tasa_metabolica'
mysql.init_app(app)


@app.route('/')
def inicio():
    return render_template('sitio/index.html')


@app.route("/img/<imagen>")
def imagenes(imagen):
    print(imagen)
    return send_from_directory(os.path.join('templates/sitio/img'), imagen)


@app.route("/admin_img/<imagen>")
def imagenes_img(imagen):
    print(imagen)
    return send_from_directory(os.path.join('templates/admin/admin_img'), imagen)


@app.route("/admin_css/<archivocss>")
def css_link1(archivocss):
    return send_from_directory(os.path.join('templates/admin/admin_css'), archivocss)


@app.route("/css/<archivocss>")
def css_link(archivocss):
    return send_from_directory(os.path.join('templates/sitio/css'), archivocss)


@app.route('/entrenamiento')
def libros():

    if not 'login' in session:
        return redirect('/admin/login')

    return render_template('admin/entrenamiento.html')


@app.route('/alimentacion')
def nosotros():

    if not 'login' in session:
        return redirect('/admin/login')

    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM `tasa_metabolica`")
    tasa_metabolica = cursor.fetchall()
    conexion.commit()

    return render_template('admin/alimentacion.html', tasa_metabolica=tasa_metabolica)


@app.route('/admin/tasa/aceptar', methods=['post'])
def metabolica():

    openai.api_key = config.api_key
    global _peso
    try:

        _altura = int(request.form['txtAltura'])
        _peso = int(request.form['txtPeso'])
        _edad = int(request.form['txtEdad'])
        _gasto_calorico = float(request.form['txtCalorico'])

    except ValueError:
        return {'error': 'Los valores de altura, peso, edad y gasto_calórico deben ser números válidos'}

    global mantenimiento
    global deficit
    global superavit

    mantenimiento = int((_peso * 10) + (_altura * 6.25) -
                        (_edad * 5)-70) * _gasto_calorico

    deficit = int(mantenimiento) * -0.15 + int(mantenimiento)
    superavit = int(mantenimiento) * 0.15 + int(mantenimiento)

    return render_template('/admin/alimentacion.html', mantenimiento=mantenimiento, deficit=deficit, superavit=superavit)


@app.route('/admin/dieta/mantenimiento', methods=['post'])
def dieta_mantenimiento():

    openai.api_key = config.api_key

    content = f"eres un assitente de nutrición deportiva que tomará el {_peso} y multiplicará por dos gramos la proteina que debe ingerir al día y tomará las calorias {mantenimiento} y haras una dieta de 4 comidas al día, especificando los gramos de comida que deba consumir con sus respectivas calorías y diciendo cuanto debo consumir de cada alimento"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": content}])
    response_content = response.choices[0].message.content

    return render_template('/admin/dieta.html', response_content=response_content)


@app.route('/admin/dieta/deficit', methods=['post'])
def dieta_deficit():

    openai.api_key = config.api_key

    content = f"eres un assitente de nutrición deportiva que tomará el {_peso} y multiplicará por dos gramos la proteina que debe ingerir al día y tomará las calorias {deficit} y haras una dieta de 4 comidas al día, especificando los gramos de comida que deba consumir con sus respectivas calorías y diciendo que alimentos consumir"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": content}])
    response_content = response.choices[0].message.content

    return render_template('/admin/dieta_deficit.html', response_content=response_content)


@app.route('/admin/dieta/superavit', methods=['post'])
def dieta_superavit():

    openai.api_key = config.api_key

    content = f"eres un assitente de nutrición deportiva que tomará el {_peso} y multiplicará por dos gramos la proteina que debe ingerir al día y tomará las calorias {superavit} y haras una dieta de 4 comidas al día, especificando los gramos de comida que deba consumir con sus respectivas calorías y diciendo que alimentos consumir"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": content}])
    response_content = response.choices[0].message.content

    return render_template('/admin/dieta_superavit.html', response_content=response_content)


@app.route('/nosotros')
def admin_index():
    if not 'login' in session:
        return redirect('/admin/login')
    return render_template('admin/index.html')


@app.route('/admin/login')
def admin_login():
    return render_template('admin/login.html')


@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    _usuario = request.form['txtUsuario']
    _password = request.form['txtPassword']
    print(_usuario)
    print(_password)

    if _usuario == "admin" and _password == "1235":
        session["login"] = True
        session["usuario"] = "Alejandro"
        return redirect("/")

    return render_template('admin/login.html')


@app.route('/admin/cerrar')
def admin_login_cerrar():
    session.clear()
    return redirect('/admin/login')


@app.route('/admin/libros')
def admin_libros():

    if not 'login' in session:
        return redirect('/admin/login')

    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM `libros`")
    libros = cursor.fetchall()
    conexion.commit()
    print(libros)

    return render_template('/admin/libros.html',   libros=libros)


@app.route('/progreso_personal')
def progreso_personal():

    if not 'login' in session:
        return redirect('/admin/login')

    return render_template('/admin/progreso.html')


if __name__ == '__main__':
    app.run(debug=True)
