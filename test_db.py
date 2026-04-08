#!/usr/bin/env python
"""
Script para probar la conexión a PostgreSQL en Render
Útil para diagnosticar problemas de conexión
"""

import psycopg2
import time

DB_HOST = 'dpg-cr6bdj1u0jms73bn1teg-a.oregon-postgres.render.com'
DB_NAME = 'dbtest_h0hy'
DB_USER = 'dbtest_h0hy_user'
DB_PASSWORD = 'xkmD4V6rmoGNJ27uGLq1k76ynORQ8HTd'

print("="*60)
print("TEST DE CONEXIÓN A POSTGRESQL EN RENDER")
print("="*60)
print(f"\n📡 Parámetros de conexión:")
print(f"   Host: {DB_HOST}")
print(f"   DB:   {DB_NAME}")
print(f"   User: {DB_USER}")
print()

def test_conexion():
    """Prueba conexión con reintentos"""
    for intento in range(3):
        try:
            print(f"[Intento {intento + 1}/3] Conectando...")
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                connect_timeout=10,
                sslmode='require'
            )
            print(f"✅ ÉXITO: Conexión establecida en intento {intento + 1}")
            return conn
        except psycopg2.Error as e:
            print(f"❌ FALLO: {e}")
            if intento < 2:
                print(f"   Esperando 2 segundos antes de reintentar...")
                time.sleep(2)
    return None

def test_query(conn):
    """Prueba una query simple"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM personas")
        count = cursor.fetchone()[0]
        print(f"\n📊 Registros en tabla 'personas': {count}")
        cursor.close()
        return True
    except Exception as e:
        print(f"\n❌ Error en query: {e}")
        return False

def test_insert(conn):
    """Prueba inserción (ROLLBACK para no guardar cambios)"""
    try:
        cursor = conn.cursor()
        sql = "INSERT INTO personas (dni, nombre, apellido, direccion, telefono) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, ('99999999', 'Test', 'Usuario', 'Calle Test', '999999999'))
        print(f"✅ INSERT funciona correctamente")
        conn.rollback()  # No guardamos el cambio
        cursor.close()
        return True
    except Exception as e:
        print(f"❌ Error en INSERT: {e}")
        return False

if __name__ == '__main__':
    conn = test_conexion()
    
    if conn:
        print("\n" + "="*60)
        print("PRUEBAS DE FUNCIONALIDAD")
        print("="*60)
        
        if test_query(conn):
            print("✅ SELECT funciona correctamente")
        
        if test_insert(conn):
            print("✅ INSERT funciona correctamente")
        
        conn.close()
        print("\n✅ TODAS LAS PRUEBAS PASARON")
        print("Tu aplicación debería funcionar correctamente.\n")
    else:
        print("\n❌ NO SE PUDO ESTABLECER CONEXIÓN")
        print("Por favor verifica:")
        print("  • Las credenciales de la base de datos")
        print("  • La conectividad de red")
        print("  • El estado del servidor PostgreSQL en Render\n")
