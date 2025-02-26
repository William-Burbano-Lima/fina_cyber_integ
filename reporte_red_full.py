import nmap
import wmi
import psutil
import platform
import sqlite3
from jinja2 import Template
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# 📌 Configuración de Base de Datos
DB_TYPE = "sqlite"  # Cambia a "sqlserver" si usas SQL Server

def connect_db():
    """Conectar a la base de datos SQLite o SQL Server."""
    if DB_TYPE == "sqlite":
        conn = sqlite3.connect("inventario_red.db")
    else:
        import pyodbc
        conn = pyodbc.connect("DRIVER={SQL Server};SERVER=tu_servidor;DATABASE=tu_db;UID=usuario;PWD=contraseña")
    return conn

def create_table():
    """Crear tabla de inventario si no existe."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            nombre TEXT,
            sistema TEXT,
            procesador TEXT,
            ram TEXT,
            almacenamiento TEXT,
            gpu TEXT,
            software TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_device(ip, nombre, sistema, procesador, ram, almacenamiento, gpu, software):
    """Guardar información de un dispositivo en la base de datos."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO activos (ip, nombre, sistema, procesador, ram, almacenamiento, gpu, software) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                   (ip, nombre, sistema, procesador, ram, almacenamiento, gpu, software))
    conn.commit()
    conn.close()

def scan_network(network_range="192.168.1.0/24"):
    """Escanear la red y obtener dispositivos conectados."""
    nm = nmap.PortScanner()
    nm.scan(hosts=network_range, arguments='-sn')  # Escaneo sin puertos
    devices = []

    for host in nm.all_hosts():
        devices.append({
            "IP": host,
            "Nombre": nm[host].hostname(),
            "Estado": nm[host].state()
        })

    return devices

def get_system_info():
    """Obtener información detallada del sistema local."""
    c = wmi.WMI()
    
    system_info = {
        "Equipo": platform.node(),
        "Sistema Operativo": platform.system(),
        "Versión": platform.version(),
        "Procesador": platform.processor(),
        "RAM (GB)": round(psutil.virtual_memory().total / (1024**3), 2),
        "Almacenamiento (GB)": round(psutil.disk_usage('/').total / (1024**3), 2),
        "GPU": [gpu.Name for gpu in c.Win32_VideoController()]
    }

    # 📌 Obtener software instalado
    software_list = [{"Nombre": s.Name, "Versión": s.Version} for s in c.Win32_Product()]
    
    return system_info, software_list

def generate_html_report():
    """Generar un reporte en HTML con los dispositivos en la base de datos."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM activos")
    devices = cursor.fetchall()
    conn.close()

    html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Inventario de Red</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body>
        <div class="container mt-4">
            <h2 class="text-center">📊 Inventario de Activos en la Red</h2>
            <table class="table table-bordered">
                <thead class="table-dark">
                    <tr>
                        <th>ID</th>
                        <th>IP</th>
                        <th>Nombre</th>
                        <th>Sistema</th>
                        <th>Procesador</th>
                        <th>RAM</th>
                        <th>Almacenamiento</th>
                        <th>GPU</th>
                        <th>Software</th>
                    </tr>
                </thead>
                <tbody>
                    {% for device in devices %}
                    <tr>
                        <td>{{ device[0] }}</td>
                        <td>{{ device[1] }}</td>
                        <td>{{ device[2] }}</td>
                        <td>{{ device[3] }}</td>
                        <td>{{ device[4] }}</td>
                        <td>{{ device[5] }}</td>
                        <td>{{ device[6] }}</td>
                        <td>{{ device[7] }}</td>
                        <td>{{ device[8] }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

    template = Template(html_template)
    rendered_html = template.render(devices=devices)

    with open("reporte_inventario.html", "w", encoding="utf-8") as file:
        file.write(rendered_html)

    print("✅ Reporte HTML generado: 'reporte_inventario.html'")

def main():
    """Ejecutar el escaneo de la red, obtener información y generar reportes."""
    create_table()
    print("🔍 Escaneando la red...")
    devices = scan_network()

    system_data, software_list = get_system_info()
    software_text = ", ".join([f"{s['Nombre']} ({s['Versión']})" for s in software_list])

    print("\n🖥️ Información del Sistema Local:", system_data)

    for device in devices:
        save_device(device["IP"], device["Nombre"], system_data["S"])
