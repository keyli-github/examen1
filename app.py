from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
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
                connect_timeout=20,  # Aumentado a 20 segundos
                sslmode='require'
            )
            
            # Verificar que la conexión funciona
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            
            print(f"✓ Conexión exitosa en intento {intento + 1}")
            return conn
            
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            ultimo_error = error_msg
            
            # Diagnosticar el tipo de error
            if 'timeout' in error_msg.lower():
                print(f"✗ TIMEOUT: El servidor tardó demasiado (intento {intento + 1}/{reintentos})")
            elif 'connection refused' in error_msg.lower():
                print(f"✗ RECHAZADO: El servidor rechazó la conexión (intento {intento + 1}/{reintentos})")
            elif 'password' in error_msg.lower():
                print(f"✗ AUTENTICACIÓN: Contraseña o usuario incorrecto (intento {intento + 1}/{reintentos})")
            elif 'no password' in error_msg.lower():
                print(f"✗ AUTENTICACIÓN: Se requiere contraseña (intento {intento + 1}/{reintentos})")
            else:
                print(f"✗ ERROR OPERACIONAL: {error_msg[:60]} (intento {intento + 1}/{reintentos})")
            
            if intento < reintentos - 1:
                print(f"  → Esperando {espera}s antes de reintentar...\n")
                time.sleep(espera)
                espera *= 2
                
        except Exception as e:
            ultimo_error = str(e)
            print(f"✗ ERROR INESPERADO (intento {intento + 1}/{reintentos}): {e}")
            if intento < reintentos - 1:
                time.sleep(espera)
                espera *= 2
    
    print(f"\n✗✗✗ NO SE PUDO CONECTAR DESPUÉS DE {reintentos} INTENTOS")
    print(f"✗ Último error: {ultimo_error}\n")
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


def inicializar_base_datos():
    """
    Crea la tabla 'personas' si no existe.
    Se ejecuta automáticamente al iniciar la aplicación.
    """
    print("\n[INIT] Verificando estructura de base de datos...")
    
    conn = conectar_db()
    if conn is None:
        print("✗ No se pudo conectar para inicializar BD")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Crear tabla si no existe
        sql_create = """
        CREATE TABLE IF NOT EXISTS personas (
            id SERIAL PRIMARY KEY,
            dni VARCHAR(20) NOT NULL UNIQUE,
            nombre VARCHAR(100) NOT NULL,
            apellido VARCHAR(100) NOT NULL,
            direccion TEXT,
            telefono VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cursor.execute(sql_create)
        conn.commit()
        print("✓ Tabla 'personas' verificada/creada")
        
        # Verificar que la tabla tiene datos
        cursor.execute("SELECT COUNT(*) FROM personas")
        count = cursor.fetchone()[0]
        print(f"✓ {count} registros en la tabla")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error al inicializar BD: {e}")
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    """Endpoint para verificar si la aplicación y BD están activas"""
    try:
        conn = conectar_db(reintentos=1)
        
        if conn is None:
            return jsonify({
                'status': 'error',
                'app': 'ok',
                'database': 'error',
                'message': 'No se pudo conectar a PostgreSQL. Revisa que esté activa en Render.'
            }), 503
        
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'ok',
            'app': 'ok',
            'database': 'ok',
            'message': 'Aplicación y base de datos están funcionando correctamente'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'app': 'ok',
            'database': 'error',
            'message': f'Error: {str(e)}'
        }), 500

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
        print(f"\n✓✓✓ REGISTRO EXITOSO: {nombre} {apellido} (DNI: {dni})\n")
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n✗✗✗ ERROR AL REGISTRAR: {error_msg}\n")
        
        # Proporcionar mensaje más útil al usuario
        if 'No se pudo conectar' in error_msg:
            flash('⚠️ Error: No hay conexión con la base de datos. Intenta de nuevo en unos segundos.', 'error')
        elif 'already exists' in error_msg or 'ya está registrado' in error_msg:
            flash(f'⚠️ Error: El DNI {dni} ya está registrado en el sistema.', 'error')
        else:
            flash(f'⚠️ Error: {error_msg}', 'error')
    
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
    
    # INICIALIZAR BASE DE DATOS
    print("\n[STARTUP] Iniciando aplicación...")
    inicializar_base_datos()
    
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"\n[STARTUP] Iniciando servidor en puerto {port} (Debug: {debug_mode})")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
