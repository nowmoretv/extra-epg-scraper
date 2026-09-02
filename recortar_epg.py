import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

def recortar_y_limpiar_guia():
    archivo = "epg.xml"
    print(f"Abriendo {archivo} para procesar...")
    tree = ET.parse(archivo)
    root = tree.getroot()

    # 1. Eliminar <icon> de la definición de canales (<channel>)
    for channel in root.findall('channel'):
        for icon in channel.findall('icon'):
            channel.remove(icon)

    # 2. Configurar la fecha límite (pasado mañana a las 05:59:59 UTC)
    ahora_utc = datetime.now(timezone.utc)
    pasado_manana = ahora_utc + timedelta(days=2)
    limite = pasado_manana.replace(hour=5, minute=59, second=59, microsecond=0)

    formato_xmltv = "%Y%m%d%H%M%S %z"
    eliminados = 0

    # 3. Procesar cada programa (<programme>)
    for programme in list(root.findall('programme')):
        start_str = programme.get('start')
        if not start_str:
            continue

        try:
            inicio_prog = datetime.strptime(start_str, formato_xmltv)
            # Si empieza después del límite, eliminamos todo el programa
            if inicio_prog > limite:
                root.remove(programme)
                eliminados += 1
                continue
        except ValueError:
            pass

        # 4. Eliminar etiquetas <icon> e <image> dentro del programa
        for icon in programme.findall('icon'):
            programme.remove(icon)
        for image in programme.findall('image'):
            programme.remove(image)

    print(f"Se eliminaron {eliminados} programas posteriores al límite.")
    print("Etiquetas <icon> e <image> eliminadas con éxito.")

    # Guardar el archivo limpio
    ET.indent(tree, space="  ", level=0)
    tree.write(archivo, encoding="utf-8", xml_declaration=True)
    print("Guía EPG optimizada y guardada.")

if __name__ == "__main__":
    recortar_y_limpiar_guia()
