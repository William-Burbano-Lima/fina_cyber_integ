import wmi
import platform
import psutil
import json
import os
import subprocess
import socket

# 📌 Obtener Información del Sistema Operativo
def get_system_info():
    system_info = {
        "Sistema Operativo": platform.system(),
        "Versión": platform.version(),
        "Arquitectura": platform.architecture()[0],
        "Nombre del Equipo": platform.node(),
        "Usuario Actual": os.getlogin()
    }
    return system_info

# 📌 Obtener Información del Hardware
def get_hardware_info():
    c = wmi.WMI()
    hardware_info = {
        "Procesador": platform.processor(),
        "Núcleos": psutil.cpu_count(logical=False),
        "RAM Total (GB)": round(psutil.virtual_memory().total / (1024**3), 2),
        "Espacio en Disco (GB)": round(psutil.disk_usage('/').total / (1024**3), 2)
    }
    return hardware_info

# 📌 Obtener Software Instalado
def get_installed_software():
    c = wmi.WMI()
    software_list = []
    for software in c.Win32_Product():
        software_list.append({
            "Nombre": software.Name,
            "Versión": software.Version,
            "Fabricante": software.Vendor,
            "Fecha de Instalación": software.InstallDate
        })
    return software_list

# 📌 Obtener Documentos y Archivos Importantes
def get_documents():
    user_path = os.path.expanduser("~")
    documents_path = os.path.join(user_path, "Documents")
    files = os.listdir(documents_path)[:10]  # Mostrar solo los primeros 10 archivos
    return {"Documentos": files}

# 📌 Obtener Equipos Conectados en la Red
def get_network_devices():
    devices = []
    cmd = "arp -a"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    for line in result.stdout.split("\n"):
        if "dynamic" in line or "static" in line:
            parts = line.split()
            devices.append({"IP": parts[0], "MAC": parts[1]})
    return devices

# 📌 Generar Reporte JSON
def generate_report():
    report = {
        "Sistema": get_system_info(),
        "Hardware": get_hardware_info(),
        "Software Instalado": get_installed_software(),
        "Documentos": get_documents(),
        "Dispositivos en Red": get_network_devices()
    }
    
    with open("inventario_activos.json", "w") as file:
        json.dump(report, file, indent=4)
    
    print("✅ Reporte de activos generado en 'inventario_activos.json'")

# 📌 Ejecutar el Script
if __name__ == "__main__":
    generate_report()
