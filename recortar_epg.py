import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

def recortar_guia():
    archivo = "epg.xml"
    print(f"Abriendo {archivo} para ajustar fechas...")
    tree = ET.parse(archivo)
    root = tree.getroot()

    # 1. Calculamos: hoy + 2 días (pasado mañana) a las 05:59:59 UTC
    ahora_utc = datetime.now(timezone.utc)
    pasado_manana = ahora_utc + timedelta(days=2)
    limite = pasado_manana.replace(hour=5, minute=59, second=59, microsecond=0)

    formato_xmltv = "%Y%m%d%H%M%S %z"
    print(f"Fecha y hora límite establecida: {limite.strftime(formato_xmltv)}")

    eliminados = 0

    # 2. Recorremos los programas y eliminamos los que exceden el corte
    for programme in root.findall('programme'):
        start_str = programme.get('start')
        if not start_str:
            continue

        try:
            # Parseamos la fecha del programa (ej: "20260904185500 +0000")
            inicio_prog = datetime.strptime(start_str, formato_xmltv)
            
            # Si empieza después de nuestro límite, lo quitamos
            if inicio_prog > limite:
                root.remove(programme)
                eliminados += 1
        except ValueError:
            # Por si algún canal usa un formato de fecha no estándar
            continue

    print(f"Se eliminaron {eliminados} programas posteriores al límite.")

    # 3. Guardar el archivo limpio
    ET.indent(tree, space="  ", level=0)
    tree.write(archivo, encoding="utf-8", xml_declaration=True)
    print("Guía EPG acotada y guardada correctamente.")

if __name__ == "__main__":
    recortar_guia()
