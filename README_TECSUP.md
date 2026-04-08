# 📚 Proyecto TECSUP - Registro de Personal

## Estado Actual
✅ Aplicación desplegada en Render  
✅ Base de datos PostgreSQL configurada  
✅ Tabla `personas` se crea automáticamente

---

## 🚀 URLs Activas

- **Aplicación Web**: https://examen1-o75s.onrender.com
- **GitHub**: https://github.com/keyli-github/examen1
- **Render Dashboard**: https://dashboard.render.com

---

## 🔧 Diagnóstico de Problemas

### Problema: "No se pudo conectar a la base de datos"

**Causa 1: Base de datos suspendida (MÁS COMÚN)**
- En Render, los servicios gratis se suspenden después de 15 minutos
- Solución:
  1. Ve a https://dashboard.render.com
  2. Busca tu PostgreSQL Database
  3. Si está en estado "Suspended" → Haz clic en "Resume"
  4. Espera 30 segundos
  5. Intenta nuevamente

**Causa 2: Credenciales incorrectas**
- Verifica que en `app.py` las credenciales coincidan con tu DB en Render
- Las credenciales deben ser exactas (mayúsculas/minúsculas)

**Causa 3: Red/Firewall**
- Asegúrate que tu conexión a internet sea estable
- Los servicios gratis de Render pueden tener latencia

---

## 📋 Requisitos del Proyecto

✅ **Completados:**
- [x] Database PostgreSQL en Render
- [x] Tabla `personas` con schema requerido
- [x] Frontend con HTML/CSS profesional
- [x] Registro de personas con validación
- [x] Visualización de registros en tabla
- [x] Eliminación de registros
- [x] Responsive design (mobile/tablet/desktop)
- [x] Deployado en Render

**Tabla `personas`:**
```sql
CREATE TABLE personas (
    id SERIAL PRIMARY KEY,
    dni VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    direccion TEXT,
    telefono VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🎨 Características de Diseño

- **Sidebar**: Navegación fija con logo TecSup
- **Topbar**: Header sticky con breadcrumbs y fecha
- **Dashboard**: 3 cards con estadísticas en tiempo real
- **Tabla**: Búsqueda integrada, hover effects, delete buttons
- **Formulario**: Validación en tiempo real, iconos SVG, campo DNI numérico
- **Colores**: Coral #C54058, Salmon #E27258, Blue #3EBCFF
- **Responsive**: Mobile (320px), Tablet (768px), Desktop (1024px+)

---

## 📁 Estructura del Proyecto

```
proyecto/
├── app.py                 # Backend Flask
├── requirements.txt       # Dependencias (Flask, psycopg2-binary)
├── init_db.py            # Script para inicializar BD (opcional)
├── test_db.py            # Script para probar conexión
├── static/
│   ├── styles.css        # Estilos profesionales
│   └── assets/
│       └── img_tecsup.jpeg   # Logo TecSup
└── templates/
    ├── index.html        # Formulario de registro
    └── administrar.html  # Tabla de registros
```

---

## 🚢 Deployment en Render

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
python app.py
```

**Environment Variables:**
```
PORT=5000
DEBUG=False
```

---

## 🔌 Funcionalidades API

### POST /registrar
Registra una nueva persona
```json
{
  "dni": "72841956",
  "nombre": "Juan",
  "apellido": "Pérez",
  "direccion": "Av. Principal 123",
  "telefono": "987654321"
}
```

### GET /administrar
Obtiene y muestra todos los registros

### POST /eliminar/<dni>
Elimina un registro por DNI

---

## 🛠️ Desarrollo Local

### Requisitos
- Python 3.8+
- PostgreSQL (o usar Render)
- pip

### Instalación
```bash
# Instalar dependencias
pip install -r requirements.txt

# Probar conexión a BD
python test_db.py

# Inicializar BD
python init_db.py

# Ejecutar servidor
python app.py
```

---

## 📞 Soporte

Si encuentras problemas:
1. Verifica que PostgreSQL esté activo en Render
2. Revisa los logs en Render Dashboard
3. Intenta nuevamente después de esperar 1-2 minutos
4. Limpia el cache del navegador (Ctrl+Shift+Delete)

---

**Última actualización:** 8 de abril de 2026
