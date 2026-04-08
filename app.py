from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'tu-clave-secreta-tecsup-2026'  # Necesario para flash messages

# Configuración de la base de datos
DB_HOST = 'dpg-cr6bdj1u0jms73bn1teg-a.oregon-postgres.render.com'
DB_NAME = 'dbtest_h0hy'
DB_USER = 'dbtest_h0hy_user'
DB_PASSWORD = 'xkmD4V6rmoGNJ27uGLq1k76ynORQ8HTd'


def conectar_db():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, 
            user=DB_USER, 
            password=DB_PASSWORD, 
            host=DB_HOST,
            connect_timeout=5
        )
        return conn
    except psycopg2.Error as e:
        print("Error al conectar a la base de datos:", e)
        return None


def crear_persona(dni, nombre, apellido, direccion, telefono):
    try:
        conn = conectar_db()
        if conn is None:
            raise Exception("No se pudo conectar a la base de datos")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO personas (dni, nombre, apellido, direccion, telefono) VALUES (%s, %s, %s, %s, %s)",
                       (dni, nombre, apellido, direccion, telefono))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error al crear persona: {e}")
        raise

def obtener_registros():
    try:
        conn = conectar_db()
        if conn is None:
            raise Exception("No se pudo conectar a la base de datos")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM personas order by apellido")
        registros = cursor.fetchall()
        cursor.close()
        conn.close()
        return registros
    except Exception as e:
        print(f"Error al obtener registros: {e}")
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registrar', methods=['POST'])
def registrar():
    try:
        dni = request.form.get('dni', '').strip()
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        direccion = request.form.get('direccion', '').strip()
        telefono = request.form.get('telefono', '').strip()
        
        # Validar campos requeridos
        if not dni or not nombre or not apellido:
            flash('Error: DNI, Nombre y Apellido son requeridos', 'error')
            return redirect(url_for('index'))
        
        crear_persona(dni, nombre, apellido, direccion, telefono)
        flash(f'✓ Persona registrada correctamente: {nombre} {apellido}', 'success')
    except Exception as e:
        print(f"Error en el registro: {e}")
        flash(f'Error al registrar: {str(e)}', 'error')
    
    # Redirigir a administrar para ver el nuevo registro
    return redirect(url_for('administrar'))

@app.route('/administrar')
def administrar():
    registros=obtener_registros()
    return render_template('administrar.html',registros=registros)

@app.route('/eliminar/<dni>', methods=['POST'])
def eliminar_registro(dni):
    try:
        conn = conectar_db()
        if conn is None:
            raise Exception("No se pudo conectar a la base de datos")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM personas WHERE dni = %s", (dni,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error al eliminar registro: {e}")
    return redirect(url_for('administrar'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
