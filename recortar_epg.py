import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

# Canales donde quieres unir Title + Desc (usa el id del canal en el XMLTV)
CANALES_COMBINAR_TITULO = [
    "ArenaSport1.hr.scraper",
    "ArenaSport2.hr.scraper",
    "ArenaSport3.hr.scraper",
    "ArenaSport4.hr.scraper",
    "ArenaSport5.hr.scraper",
    "ArenaSport6.hr.scraper",
    "ArenaSport7.hr.scraper",
    "ArenaSport8.hr.scraper",
    "ArenaSport9.hr.scraper",
    "ArenaSport10.hr.scraper"
]

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
    titulos_modificados = 0

    # 3. Procesar cada programa (<programme>)
    for programme in list(root.findall('programme')):
        start_str = programme.get('start')
        channel_id = programme.get('channel')

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

        # 5. Combinar <title> con <desc> si el canal está en la lista
        if channel_id in CANALES_COMBINAR_TITULO:
            elem_title = programme.find('title')
            elem_desc = programme.find('desc')

            if elem_title is not None and elem_desc is not None:
                txt_title = (elem_title.text or "").strip()
                txt_desc = (elem_desc.text or "").strip()

                if txt_title and txt_desc and txt_desc != txt_title:
                    elem_title.text = f"{txt_title}: {txt_desc}"
                    titulos_modificados += 1

    print(f"Se eliminaron {eliminados} programas posteriores al límite.")
    print(f"Se combinaron {titulos_modificados} títulos con su descripción.")
    print("Etiquetas <icon> e <image> eliminadas con éxito.")

    # Guardar el archivo limpio
    ET.indent(tree, space="  ", level=0)
    tree.write(archivo, encoding="utf-8", xml_declaration=True)
    print("Guía EPG optimizada y guardada.")

if __name__ == "__main__":
    recortar_y_limpiar_guia()
