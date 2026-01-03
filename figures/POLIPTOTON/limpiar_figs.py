import os
import re

CARPETA_RAIZ = "FILES_POLIPTOTON"

def normalizar_archivo(contenido):
    lineas = contenido.split('\n')
    lineas_limpias = []
    
    # 1. Regex para encabezados (AHORA ES CODICIOSA para no cortar la palabra)
    # Detecta: =====PALABRA, =====[PALABRA], PALABRA (sola en una línea)
    re_encabezado_con_signos = re.compile(r'={2,}\s*\[?([A-ZÁÉÍÓÚÑa-z\s]+)\]?\s*={0,}')
    
    # 2. Regex para detectar si una línea es SOLO la palabra clave (sin signos de igual)
    # Debe ser todo mayúsculas, de más de 3 letras y sin verbos comunes al inicio
    re_palabra_sola = re.compile(r'^[A-ZÁÉÍÓÚÑ\s]{4,}$')

    # 3. Regex para limpiar basura
    re_limpiar_frase_basura = re.compile(r'(?i)\s+EN\s+MAYÚSCULAS?.*')
    re_separador = re.compile(r'ññññ')
    re_solo_numeros_o_puntos = re.compile(r'^[\d\.\s]+$')
    re_quitar_numero_al_inicio = re.compile(r'^[\d\.\s]+')

    for linea in lineas:
        l = linea.strip()
        
        # Ignorar líneas de decoración final (solo signos de igual)
        if re.match(r'^={10,}$', l) or not l:
            continue

        # CASO A: Encabezado con signos =====[PALABRA]
        match_h = re_encabezado_con_signos.match(l)
        if match_h:
            texto_extraido = match_h.group(1)
            palabra = re_limpiar_frase_basura.sub('', texto_extraido).strip().upper()
            if palabra:
                lineas_limpias.append(f"\n======[{palabra}]")
            continue

        # CASO B: Palabra sola (Encabezado sin signos)
        if re_palabra_sola.match(l):
            palabra = re_limpiar_frase_basura.sub('', l).strip().upper()
            lineas_limpias.append(f"\n======[{palabra}]")
            continue

        # CASO C: El separador ññññ (Limpiar si trae números pegados)
        if re_separador.search(l):
            lineas_limpias.append("ññññ")
            continue

        # CASO D: Líneas que son solo números o basura de lista (1., 2., etc)
        if re_solo_numeros_o_puntos.match(l):
            continue

        # CASO E: Versos del poema (Quitar números al inicio si existen)
        verso = re_quitar_numero_al_inicio.sub('', l).strip()
        
        if verso:
            lineas_limpias.append(verso)

    # Reconstrucción final con espaciado correcto
    texto_final = "\n".join(lineas_limpias)
    texto_final = re.sub(r'\n{2,}', '\n', texto_final) # Quitar saltos triples
    texto_final = texto_final.replace("ññññ", "\nññññ\n") # Aire a los separadores
    texto_final = re.sub(r'(\n======\[)', r'\n\1', texto_final) # Aire a los títulos

    return texto_final.strip()

def procesar_carpeta():
    if not os.path.exists(CARPETA_RAIZ):
        print(f"La carpeta {CARPETA_RAIZ} no existe")
        return

    archivos = [f for f in os.listdir(CARPETA_RAIZ) if f.endswith(".txt")]
    
    for nombre_archivo in archivos:
        ruta = os.path.join(CARPETA_RAIZ, nombre_archivo)
        with open(ruta, 'r', encoding='utf-8') as f:
            data = f.read()
        
        nueva_data = normalizar_archivo(data)
        
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(nueva_data)
        print(f"✨ Reparado y Limpiado: {nombre_archivo}")

if __name__ == "__main__":
    procesar_carpeta()