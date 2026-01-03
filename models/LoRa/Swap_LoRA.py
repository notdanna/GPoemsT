import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Importamos la función discreta de respaldo
from Attention import get_mask

# Desactivar avisos de paralelismo para una consola limpia
os.environ["TOKENIZERS_PARALLELISM"] = "false"

#%% --- CONFIGURACIÓN DE RUTAS ---
if torch.backends.mps.is_available():
    torch.mps.empty_cache()

device = torch.device("mps")
dtype = torch.float16

BASE_MODEL = "/Users/dam/ESCOM/ML/Poemas/models/BASE_MODEL"
LORA_BASE_PATH = "/Users/dam/ESCOM/ML/Poemas/models/LoRa"

# Diccionario de rutas para facilitar la carga iterativa
LORA_PATHS = {
    "aliteracion": os.path.join(LORA_BASE_PATH, "lora_aliteracion"),
    "anafora": os.path.join(LORA_BASE_PATH, "lora_anafora"),
    "animalizacion": os.path.join(LORA_BASE_PATH, "lora_animalizacion"),
    "asindeton": os.path.join(LORA_BASE_PATH, "lora_asindeton"),
    "cosificacion": os.path.join(LORA_BASE_PATH, "lora_cosificacion"),
    "epiteto": os.path.join(LORA_BASE_PATH, "lora_epiteto"),
    "hiperbole": os.path.join(LORA_BASE_PATH, "lora_hiperbole"),
    "paralelismo": os.path.join(LORA_BASE_PATH, "lora_paralelismo"),
    "personificacion": os.path.join(LORA_BASE_PATH, "lora_personificacion"),
    "pleonasmo": os.path.join(LORA_BASE_PATH, "lora_pleonasmo"),
    "polisindeton": os.path.join(LORA_BASE_PATH, "lora_polisindeton"),
    "simil": os.path.join(LORA_BASE_PATH, "lora_simil"),
    "metafora": os.path.join(LORA_BASE_PATH, "modelo_lora_final")
}

#%% --- CARGA DE MODELO Y TOKENIZER ---
print(f"Cargando Tokenizer y Modelo Base desde {BASE_MODEL}...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, local_files_only=True)
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=dtype,
    device_map={"": "mps"},
    trust_remote_code=True,
    local_files_only=True
)

#%% --- CARGA DE TODOS LOS ADAPTADORES ---
print("Cargando adaptadores LoRA especializados...")
try:
    # Inicializar PeftModel con el primer adaptador
    model = PeftModel.from_pretrained(model, LORA_PATHS["metafora"], adapter_name="metafora")
    
    # Cargar el resto de los adaptadores de forma dinámica
    for nombre, ruta in LORA_PATHS.items():
        if nombre != "metafora":
            model.load_adapter(ruta, adapter_name=nombre)
    
    model.eval()
    print(f"Módulos locales activos: {len(model.peft_config.keys())}")
except Exception as e:
    print(f"Error crítico en la carga de adaptadores: {e}")

#%% --- FUNCIONES DE ANÁLISIS Y GENERACIÓN ---

def visualizar_atencion(palabra, figura="metafora", capa=-1, cabeza=0):
    """Genera un heatmap de la atención para analizar el comportamiento del LoRA."""
    if figura not in model.peft_config.keys():
        print(f"La visualización de atención solo está disponible para modelos locales.")
        return

    model.set_adapter(figura)
    prompt = f'Escribe un poema usando la figura retórica "{figura}" con la palabra "{palabra}".\nPoema:\n'
    inputs_prompt = tokenizer(prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        output_tokens = model.generate(
            **inputs_prompt,
            max_new_tokens=40,
            do_sample=True,
            temperature=0.7
        )
        # Re-pasar para obtener matrices de atención
        outputs = model(output_tokens, output_attentions=True)
        attentions = outputs.attentions

    attn_matrix = attentions[capa][0, cabeza].detach().cpu().float().numpy()
    full_tokens = [tokenizer.decode([t]) for t in output_tokens[0]]

    plt.figure(figsize=(12, 10))
    sns.heatmap(attn_matrix, xticklabels=full_tokens, yticklabels=full_tokens, cmap='magma')
    plt.title(f"Mapa de Atención: {figura.upper()} | Palabra: {palabra}")
    plt.show()

def generar_poema(palabra, figura="metafora"):
    """Motor de generación: Prioriza LoRA local, usa 'get_mask' como fallback."""
    
    if figura in model.peft_config.keys():
        model.set_adapter(figura)
        prompt = f'Escribe un poema usando la figura retórica "{figura}" con la palabra "{palabra}".\nPoema:\n'
        inputs = tokenizer(prompt, return_tensors="pt").to(device)

        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=80,
                temperature=0.7,
                do_sample=True,
                repetition_penalty=1.1,
                pad_token_id=tokenizer.pad_token_id
            )
        resultado = tokenizer.decode(output[0], skip_special_tokens=True)
        poema = resultado.split("Poema:")[-1].strip()
        tag = "[LOCAL]"
    else:
        # Fallback discreto a través del módulo Attention
        poema = get_mask(palabra, figura)
        tag = "[EXTENDIDO]"

    if poema:
        print(f"\n{tag} | {figura.upper()} -> {palabra}:\n{poema}\n" + "." * 30)
    else:
        print(f"Error: No se pudo obtener resultado para {figura}")

#%% --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    test_palabra = "naranja"
    
    # Prueba 1: Generación con LoRA local
    generar_poema(test_palabra, "metafora")
    
    # Prueba 2: Análisis de atención del LoRA local
    visualizar_atencion(test_palabra, "metafora")
    
    # Prueba 3: Generación con figura no entrenada (Fallback)
    generar_poema(test_palabra, "Antitesis")