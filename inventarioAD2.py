import wmi
import platform
import psutil
import json
import os
import sqlite3
import pyodbc
from jinja2 import Template

# 📌 Conexión a Base de Datos (Elegir SQLite o SQL Server)
DB_TYPE = "sqlite"  # Opción: "sqlite" o "sqlserver"

def connect_db():
    if DB_TYPE == "sqlite":
        conn = sqlite3.connect("inventario.db")
    else:
        conn = pyodbc.connect(
            "DRIVER={SQL Server};SERVER=tu_servidor;DATABASE=tu_db;UID=usuario;PWD=contraseña"
        )
    return conn

# 📌 Crear Tabla en la Base de Datos
def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            categoria TEXT,
            detalles TEXT
        )
    """)
    conn.commit()
    conn.close()

# 📌 Guardar Activos en la Base de Datos
def save_asset(nombre, categoria, detalles):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO activos (nombre, categoria, detalles) VALUES (?, ?, ?)",
                   (nombre, categoria, detalles))
    conn.commit()
    conn.close()

# 📌 Obtener Información del Sistema
def get_system_info():
    return {
        "Sistema Operativo": platform.system(),
        "Versión": platform.version(),
        "Arquitectura": platform.architecture()[0],
        "Nombre del Equipo": platform.node(),
        "Usuario Actual": os.getlogin()
    }

# 📌 Obtener Información del Hardware
def get_hardware_info():
    return {
        "Procesador": platform.processor(),
        "Núcleos": psutil.cpu_count(logical=False),
        "RAM Total (GB)": round(psutil.virtual_memory().total / (1024**3), 2),
        "Espacio en Disco (GB)": round(psutil.disk_usage('/').total / (1024**3), 2)
    }

# 📌 Obtener Software Instalado
def get_installed_software():
    c = wmi.WMI()
    software_list = [{"Nombre": software.Name, "Versión": software.Version} for software in c.Win32_Product()]
    return software_list

# 📌 Guardar Datos en la Base de Datos
def save_all_assets():
    create_table()

    # Guardar Sistema Operativo
    system_info = get_system_info()
    save_asset(system_info["Nombre del Equipo"], "Sistema", json.dumps(system_info))

    # Guardar Hardware
    hardware_info = get_hardware_info()
    save_asset("Hardware del equipo", "Hardware", json.dumps(hardware_info))

    # Guardar Software
    for software in get_installed_software():
        save_asset(software["Nombre"], "Software", json.dumps(software))

# 📌 Generar Reporte HTML
def generate_html_report():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM activos")
    activos = cursor.fetchall()
    conn.close()

    # 📌 Plantilla HTML con Jinja2
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Inventario de Activos</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body>
        <div class="container mt-4">
            <h2 class="text-center">📋 Inventario de Activos Digitales</h2>
            <table class="table table-bordered">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nombre</th>
                        <th>Categoría</th>
                        <th>Detalles</th>
                    </tr>
                </thead>
                <tbody>
                    {% for activo in activos %}
                    <tr>
                        <td>{{ activo[0] }}</td>
                        <td>{{ activo[1] }}</td>
                        <td>{{ activo[2] }}</td>
                        <td>{{ activo[3] }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

    template = Template(html_template)
    rendered_html = template.render(activos=activos)

    with open("reporte_inventario.html", "w", encoding="utf-8") as file:
        file.write(rendered_html)

    print("✅ Reporte HTML generado: 'reporte_inventario.html'")

# 📌 Ejecutar Todo
if __name__ == "__main__":
    save_all_assets()
    generate_html_report()
    print("✅ Inventario de activos generado y almacenado en la base de datos.")
