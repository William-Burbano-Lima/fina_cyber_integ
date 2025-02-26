import nmap

def scan_network(network_range):
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

# 📌 Ejecutar escaneo en la subred (ajustar según tu red)
network_range = "192.168.80.1/24"
discovered_devices = scan_network(network_range)

print("Dispositivos detectados en la red:")
for device in discovered_devices:
    print(device)
