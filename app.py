from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import os
import time

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'tu-clave-secreta-tecsup-2026'

# Configuración de la base de datos
DB_HOST = 'dpg-cr6bdj1u0jms73bn1teg-a.oregon-postgres.render.com'
DB_NAME = 'dbtest_h0hy'
DB_USER = 'dbtest_h0hy_user'
DB_PASSWORD = 'xkmD4V6rmoGNJ27uGLq1k76ynORQ8HTd'

print("\n" + "="*70)
print("🚀 SERVIDOR TECSUP INICIANDO")
print("="*70)
print(f"PostgreSQL Host: {DB_HOST}")
print(f"Database: {DB_NAME}")
print("="*70 + "\n")


def conectar_db(reintentos=3, espera=1):
    """
    Conecta a PostgreSQL con reintentos automáticos.
    Si falla, reintenta hasta 3 veces con backoff exponencial.
    """
    ultimo_error = None
    
    for intento in range(reintentos):
        try:
            print(f"[{intento + 1}/{reintentos}] Intentando conexión a PostgreSQL...")
            
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                connect_timeout=15,
                sslmode='require'
            )
            
            print(f"✓ Conexión exitosa en intento {intento + 1}")
            return conn
            
        except psycopg2.OperationalError as e:
            ultimo_error = str(e)
            print(f"✗ Intento {intento + 1} fallido: {e}")
            if intento < reintentos - 1:
                print(f"  Esperando {espera} segundos antes de reintentar...")
                time.sleep(espera)
                espera *= 2
        except Exception as e:
            ultimo_error = str(e)
            print(f"✗ Error inesperado en intento {intento + 1}: {e}")
            if intento < reintentos - 1:
                time.sleep(espera)
                espera *= 2
    
    print(f"✗ No se pudo conectar después de {reintentos} intentos")
    print(f"  Último error: {ultimo_error}")
    return None


def crear_persona(dni, nombre, apellido, direccion, telefono):
    """Inserta una nueva persona en la base de datos"""
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
        
    except psycopg2.IntegrityError:
        conn.rollback()
        cursor.close()
        raise Exception(f"El DNI {dni} ya está registrado en el sistema")
    except Exception as e:
        conn.rollback()
        cursor.close()
        raise Exception(f"Error en base de datos: {str(e)}")
    finally:
        conn.close()


def obtener_registros():
    """Obtiene todos los registros de personas, ordenados por apellido"""
    conn = conectar_db()
    
    if conn is None:
        print("✗ No se pudo conectar para obtener registros")
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM personas ORDER BY apellido, nombre")
        registros = cursor.fetchall()
        cursor.close()
        print(f"✓ {len(registros)} registros obtenidos exitosamente")
        return registros
    except Exception as e:
        print(f"✗ Error al obtener registros: {e}")
        return []
    finally:
        conn.close()

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
    """Elimina un registro por DNI"""
    conn = conectar_db()
    
    if conn is None:
        flash('Error: No se pudo conectar a la base de datos', 'error')
        return redirect(url_for('administrar'))
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM personas WHERE dni = %s", (dni,))
        
        if cursor.rowcount > 0:
            conn.commit()
            flash(f'✓ Registro eliminado correctamente', 'success')
            print(f"✓ Registro eliminado: DNI {dni}")
        else:
            conn.rollback()
            flash('Error: Registro no encontrado', 'error')
            print(f"✗ Registro no encontrado: DNI {dni}")
        
        cursor.close()
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error al eliminar: {e}")
        flash(f'Error al eliminar: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('administrar'))


def cerrar_app(error=None):
    """Hook para cerrar la aplicación limpiamente"""
    print("\n" + "="*70)
    print("🛑 SERVIDOR TECSUP DETENIÉNDOSE")
    print("="*70 + "\n")


if __name__ == '__main__':
    app.teardown_appcontext(cerrar_app)
    
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"Iniciando en puerto {port} (Debug: {debug_mode})")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
