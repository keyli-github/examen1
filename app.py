from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import psycopg2.pool
import os
import time

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'tu-clave-secreta-tecsup-2026'

# Configuración de la base de datos
DB_HOST = 'dpg-cr6bdj1u0jms73bn1teg-a.oregon-postgres.render.com'
DB_NAME = 'dbtest_h0hy'
DB_USER = 'dbtest_h0hy_user'
DB_PASSWORD = 'xkmD4V6rmoGNJ27uGLq1k76ynORQ8HTd'

# Pool de conexiones para mejor rendimiento
try:
    db_pool = psycopg2.pool.SimpleConnectionPool(
        1, 5,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        connect_timeout=10,
        sslmode='require'
    )
    print("✓ Pool de conexiones creado exitosamente")
except psycopg2.Error as e:
    print(f"✗ Error al crear pool de conexiones: {e}")
    db_pool = None


def conectar_db(reintentos=3, espera=1):
    """Conecta a la DB con reintentos automáticos"""
    for intento in range(reintentos):
        try:
            if db_pool:
                conn = db_pool.getconn()
            else:
                conn = psycopg2.connect(
                    dbname=DB_NAME,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    host=DB_HOST,
                    connect_timeout=10,
                    sslmode='require'
                )
            print(f"✓ Conexión exitosa (intento {intento + 1}/{reintentos})")
            return conn
        except psycopg2.Error as e:
            print(f"✗ Intento {intento + 1}/{reintentos} fallido: {e}")
            if intento < reintentos - 1:
                time.sleep(espera)
                espera *= 2  # Backoff exponencial
            else:
                print(f"✗ No se pudo conectar después de {reintentos} intentos")
                return None
    return None


def liberar_conexion(conn):
    """Libera una conexión del pool"""
    if db_pool and conn:
        try:
            db_pool.putconn(conn)
        except Exception as e:
            print(f"Error al liberar conexión: {e}")


def crear_persona(dni, nombre, apellido, direccion, telefono):
    conn = conectar_db()
    if conn is None:
        raise Exception("No se pudo conectar a la base de datos después de múltiples intentos")
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO personas (dni, nombre, apellido, direccion, telefono) VALUES (%s, %s, %s, %s, %s)",
            (dni, nombre, apellido, direccion, telefono)
        )
        conn.commit()
        print(f"✓ Persona registrada: {nombre} {apellido} (DNI: {dni})")
        cursor.close()
    except psycopg2.IntegrityError as e:
        conn.rollback()
        cursor.close()
        raise Exception(f"El DNI {dni} ya está registrado")
    except Exception as e:
        conn.rollback()
        cursor.close()
        raise Exception(f"Error en base de datos: {str(e)}")
    finally:
        liberar_conexion(conn)


def obtener_registros():
    conn = conectar_db()
    if conn is None:
        print("✗ No se pudo conectar para obtener registros")
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM personas ORDER BY apellido, nombre")
        registros = cursor.fetchall()
        cursor.close()
        print(f"✓ {len(registros)} registros obtenidos")
        return registros
    except Exception as e:
        print(f"✗ Error al obtener registros: {e}")
        return []
    finally:
        liberar_conexion(conn)

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
    conn = conectar_db()
    if conn is None:
        flash('Error: No se pudo conectar a la base de datos', 'error')
        return redirect(url_for('administrar'))
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM personas WHERE dni = %s", (dni,))
        
        if cursor.rowcount > 0:
            conn.commit()
            flash(f'✓ Registro {dni} eliminado correctamente', 'success')
            print(f"✓ Registro eliminado: {dni}")
        else:
            conn.rollback()
            flash('Error: Registro no encontrado', 'error')
            print(f"✗ No se encontró registro con DNI: {dni}")
        
        cursor.close()
    except Exception as e:
        conn.rollback()
        print(f"✗ Error al eliminar: {e}")
        flash(f'Error al eliminar: {str(e)}', 'error')
    finally:
        liberar_conexion(conn)
    
    return redirect(url_for('administrar'))


def cerrar_pool():
    """Cierra el pool de conexiones al apagar la app"""
    global db_pool
    if db_pool:
        try:
            db_pool.closeall()
            print("✓ Pool de conexiones cerrado")
        except Exception as e:
            print(f"✗ Error al cerrar pool: {e}")


if __name__ == '__main__':
    import atexit
    atexit.register(cerrar_pool)
    
    print("\n" + "="*50)
    print("🚀 INICIANDO SERVIDOR TECSUP")
    print("="*50)
    print(f"DB Host: {DB_HOST}")
    print(f"DB Name: {DB_NAME}")
    print(f"DB User: {DB_USER}")
    print("="*50 + "\n")
    
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
