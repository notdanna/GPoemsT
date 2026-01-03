import glob
import json
import os
import re

# --- CONFIGURACIÓN DE RUTAS ---
directorio_actual = os.getcwd()

if os.path.basename(directorio_actual) == "lotes":
    path_lotes = directorio_actual
    path_resultados = os.path.dirname(directorio_actual)
else:
    path_lotes = os.path.join(directorio_actual, "lotes")
    path_resultados = os.path.join(directorio_actual, "FILES_POLIPTOTON")

print(f"Directorio de Lotes: {path_lotes}")
print(f"Directorio de Resultados: {path_resultados}")

tokenizer_eos = "<|endoftext|>"
dataset_list = []

def get_lote_id(filename):
    match = re.search(r"(\d{3})", filename)
    return match.group(1) if match else None

# Regex para limpiar líneas de metadatos (Tono, Perspectiva, etc.)
re_limpiar_metadatos = re.compile(r'(?i)^(Tono|Perspectiva|Estilo|Enfoque|Contexto|Figura|Retórica|Imagen|Verso):\s*.*', re.MULTILINE)

archivos_lotes = sorted(glob.glob(os.path.join(path_lotes, "lote_*.txt")))

print(f"--- Iniciando procesamiento de {len(archivos_lotes)} lotes ---\n")

for archivo_palabras in archivos_lotes:
    lote_id = get_lote_id(os.path.basename(archivo_palabras))

    if not lote_id:
        continue

    patron_busqueda = os.path.join(
        path_resultados, f"poliptoton_lote_{lote_id}*.txt"
    )
    archivos_poemas = sorted(glob.glob(patron_busqueda))

    if not archivos_poemas:
        continue

    # 1. Leer las PALABRAS originales del lote
    with open(archivo_palabras, "r", encoding="utf-8", errors="ignore") as f:
        palabras_originales = [line.strip().upper() for line in f if line.strip()]

    # 2. Leer los POEMAS generados
    contenido_poemas_completo = ""
    for ap in archivos_poemas:
        try:
            with open(ap, "r", encoding="utf-8") as f:
                contenido_poemas_completo += "\n" + f.read()
        except UnicodeDecodeError:
            with open(ap, "r", encoding="cp1252") as f:
                contenido_poemas_completo += "\n" + f.read()

    # --- PROCESAMIENTO CON REGEX FLEXIBLE ---
    # Esta regex busca:
    # ={3,}        -> 3 o más signos de igual
    # \[{0,2}      -> 0, 1 o 2 corchetes de apertura
    # ([^\]\n]+)   -> Captura la palabra (cualquier cosa que no sea cierre de corchete o salto de línea)
    # \]{0,2}      -> 0, 1 o 2 corchetes de cierre
    bloques = re.split(r"={3,}\[?\[?([^\]\n]+)\]?\]?", contenido_poemas_completo)
    
    palabras_encontradas_count = 0
    palabras_vistas = set()

    for i in range(1, len(bloques), 2):
        # Limpiar la palabra extraída de posibles restos de caracteres
        palabra_clave = bloques[i].replace('[', '').replace(']', '').strip().upper()
        contenido_bloque = bloques[i+1]

        if palabra_clave == "=" or not palabra_clave:
            continue
        
        # Validación de palabra contra lista original
        if palabra_clave in palabras_originales and palabra_clave not in palabras_vistas:
            palabras_encontradas_count += 1
            palabras_vistas.add(palabra_clave)

        # Limpieza de metadatos (Tono, Perspectiva, etc.)
        contenido_limpio = re_limpiar_metadatos.sub('', contenido_bloque)

        # Separación por poemas
        versiones_poema = [p.strip() for p in re.split(r'ññññ|ñññ', contenido_limpio) if p.strip()]

        for poema in versiones_poema:
            # Eliminar posibles líneas de cierre con signos de igual
            poema_final = re.sub(r'\n={3,}.*', '', poema).strip()

            if len(poema_final) < 10:
                continue

            entry = {
                "text": f"Escribe un poema usando la figura retórica \"poliptoton\" con la palabra \"{palabra_clave}\".\nPoema:\n{poema_final}\n{tokenizer_eos}"
            }
            dataset_list.append(entry)

    if palabras_encontradas_count > 0:
        print(f"Lote {lote_id}: {palabras_encontradas_count}/{len(palabras_originales)} palabras coincidentes.")
    else:
        print(f"Lote {lote_id}: No se encontraron coincidencias (Revisar formato).")

# --- GUARDADO ---
print("\n" + "=" * 40)
print(f"TOTAL EJEMPLOS GENERADOS: {len(dataset_list)}")
print("=" * 40)

output_file = "dataset_final_poliptoton.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(dataset_list, f, ensure_ascii=False, indent=2)

print(f"Listo. Dataset generado con éxito.")