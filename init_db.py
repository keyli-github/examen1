#!/usr/bin/env python
"""
Script de inicialización de la base de datos
Crea la tabla 'personas' si no existe
"""

import psycopg2
import sys

DB_HOST = 'dpg-cr6bdj1u0jms73bn1teg-a.oregon-postgres.render.com'
DB_NAME = 'dbtest_h0hy'
DB_USER = 'dbtest_h0hy_user'
DB_PASSWORD = 'xkmD4V6rmoGNJ27uGLq1k76ynORQ8HTd'

SQL_CREATE_TABLE = """
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

print("="*70)
print("INICIALIZADOR DE BASE DE DATOS - TECSUP")
print("="*70)
print(f"\nConectando a: {DB_HOST}")
print(f"Database: {DB_NAME}")
print(f"User: {DB_USER}\n")

try:
    # Conectar
    print("[1/3] Conectando a PostgreSQL...")
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=15,
        sslmode='require'
    )
    print("✓ Conexión exitosa\n")
    
    # Crear tabla
    print("[2/3] Creando tabla 'personas'...")
    cursor = conn.cursor()
    cursor.execute(SQL_CREATE_TABLE)
    conn.commit()
    print("✓ Tabla creada/verificada\n")
    
    # Verificar
    print("[3/3] Verificando tabla...")
    cursor.execute("SELECT COUNT(*) FROM personas")
    count = cursor.fetchone()[0]
    print(f"✓ Tabla contiene {count} registros\n")
    
    cursor.close()
    conn.close()
    
    print("="*70)
    print("✅ BASE DE DATOS INICIALIZADA CORRECTAMENTE")
    print("="*70)
    print("\nYa puedes iniciar el servidor con: python app.py\n")
    sys.exit(0)
    
except psycopg2.OperationalError as e:
    print(f"\n❌ ERROR DE CONEXIÓN:")
    print(f"   {e}")
    print("\nVerifica:")
    print("  • Las credenciales sean correctas")
    print("  • El servidor PostgreSQL en Render esté activo")
    print("  • La conectividad de red sea correcta")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ ERROR INESPERADO:")
    print(f"   {e}")
    sys.exit(1)
