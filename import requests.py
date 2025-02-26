import requests
import socket


def obtener_ip(dominio):
    try:
        ip = socket.gethostbyname(dominio)
        return ip
    except socket.gaierror:
        return None


def obtener_registros_dns(dominio):
    try:
        import dns.resolver
        registros = dns.resolver.resolve(dominio, 'A')
        return [str(rdata) for rdata in registros]
    except Exception as e:
        return str(e)


def obtener_informacion_whois(dominio):
    try:
        import whois
        info = whois.whois(dominio)
        return info
    except Exception as e:
        return str(e)


def main():
    dominio = input("Introduce el dominio: ")
    print(f"Obteniendo información para el dominio: {dominio}")

    ip = obtener_ip(dominio)
    if ip:
        print(f"Dirección IP: {ip}")
    else:
        print("No se pudo obtener la dirección IP.")

    registros_dns = obtener_registros_dns(dominio)
    if registros_dns:
        print(f"Registros DNS: {registros_dns}")
    else:
        print("No se pudieron obtener los registros DNS.")

    info_whois = obtener_informacion_whois(dominio)
    if info_whois:
        print(f"Información WHOIS: {info_whois}")
    else:
        print("No se pudo obtener la información WHOIS.")


if __name__ == "__main__":
    main()
