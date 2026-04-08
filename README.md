# Registro de Personas - Aplicación Web en Render

## Descripción
Aplicación web desarrollada con Flask y PostgreSQL para gestionar registros de personas (DNI, nombre, apellido, dirección, teléfono).

## Requisitos
- Python 3.8+
- PostgreSQL
- Flask
- psycopg2-binary

## Instalación Local

1. Clonar el repositorio
2. Crear un entorno virtual: `python -m venv venv`
3. Activar el entorno: `venv\Scripts\activate` (Windows) o `source venv/bin/activate` (Linux/Mac)
4. Instalar dependencias: `pip install -r requirements.txt`

## Configuración de Base de Datos

La aplicación se conecta a una base de datos PostgreSQL en Render. 

Crear la tabla con el siguiente comando SQL:
```sql
CREATE TABLE personas (
    id SERIAL PRIMARY KEY,
    dni VARCHAR(20) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    direccion TEXT,
    telefono VARCHAR(20)
);
```

## Ejecución

Para ejecutar localmente:
```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## En Render

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
python app.py
```

## Características

- ✅ Registro de nuevas personas
- ✅ Visualización de todos los registros
- ✅ Eliminación de registros por DNI
- ✅ Diseño responsivo
- ✅ Interfaz intuitiva

## Estructura del Proyecto

```
proyecto/
├── app.py                 # Aplicación Flask
├── requirements.txt       # Dependencias de Python
├── templates/
│   ├── index.html        # Formulario de registro
│   └── administrar.html   # Gestión de registros
└── static/
    └── styles.css        # Estilos CSS
```

## Rutas Disponibles

- `GET /` - Formulario de registro
- `POST /registrar` - Registrar nueva persona
- `GET /administrar` - Listar todos los registros
- `POST /eliminar/<dni>` - Eliminar registro por DNI
