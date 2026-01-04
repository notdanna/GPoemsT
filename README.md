# Modular Transformer Architecture for Constrained Poetic Generation

Esta arquitectura tiene como objetivo la generación de poemas con métricas y figuras retóricas precisas mediante un sistema de pesos intercambiables, permitiendo un control estilístico sin precedentes en modelos de lenguaje de gran escala.

## Resumen Técnico

El modelo utiliza un enfoque de dos etapas para la especialización: una fase de **Domain Adaptation** mediante Fine-Tuning completo (FFT) y una fase de **Especialización Retórica** mediante adaptadores LoRA (Low-Rank Adaptation). El sistema permite el intercambio dinámico de pesos (*hot-swapping*) en tiempo de ejecución para generar más de 30 figuras retóricas diferentes de forma instantánea.

## Pipeline de Desarrollo

### 1. Filtrado Léxico y Creación de Corpus

La base reside en una selección léxica rigurosa:

* **Diccionario inicial:** 50,000 términos provenientes de textos clásicos y la librería *wordfreq*.
* **Word Embeddings:** Uso del modelo `cc.es.300.bin` de FastText (Facebook AI Research) para proyectar palabras en un espacio de 300 dimensiones.
* **Destilación Poética:** Filtrado mediante proximidad vectorial en nodos temáticos (emociones, naturaleza, luz) para obtener un léxico optimizado de **5,000 palabras** de alta carga artística.

### 2. Entrenamiento del Modelo Base

* **Arquitectura:** Modelo basado en la arquitectura Transformer con mecanismos de atención.
* **Pre-entrenamiento:** Entrenamiento de un modelo de 3B de parámetros utilizando subconjuntos de **FineWeb-Edu** y textos de dominio público.
* **Implementación:** Desarrollado utilizando el ecosistema **PyTorch**.
* **Domain Adaptation:** Ajuste fino completo (FFT) sobre un corpus masivo de poesía clásica para asimilar la estética poética global.

### 3. Especialización mediante LoRA y Datos Sintéticos

Dada la escasez de ejemplos históricos para ciertas figuras, se implementó una estrategia de datos sintéticos:

* **Generación Masiva:** Uso de Qwen para generar 1,400,000 poemas categorizados por figura.
* **Adaptadores Modulares:** En lugar de alterar el modelo base, se entrenan matrices de bajo rango para cada figura retórica.
* **Fundamento Matemático:**



Donde  permanece congelado y solo se entrenan las matrices  y , reduciendo el costo computacional drásticamente.

## Optimización e Inferencia

El sistema de producción utiliza **vLLM** para una gestión eficiente de la memoria y aceleración de la inferencia.

* **Cuantización NF4:** El modelo se carga en 4 bits para reducir el uso de VRAM en un 70% sin perder coherencia.
* **Hot-Swapping:** El sistema realiza el intercambio de pesos de los adaptadores LoRA en milisegundos según la figura solicitada.
* **PagedAttention:** Optimización del KV Cache para evitar la fragmentación de memoria en generaciones largas.

## Instalación

Se recomienda el uso de `uv` para una instalación de dependencias acelerada y consistente:

```bash
# Instalación de uv
pip install uv

# Instalación del entorno optimizado
uv pip install --system --no-cache-dir \
    "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git" \
    xformers trl peft accelerate bitsandbytes \
    transformers datasets sentencepiece

```

## Figuras Retóricas Soportadas

El modelo cuenta con adaptadores específicos para las siguientes estructuras (selección):

| Categoría | Figuras |
| --- | --- |
| **Repetición** | Anáfora, Epífora, Anadiplosis, Epanadiplosis, Polisíndeton. |
| **Omisión/Orden** | Asíndeton, Hipérbaton, Elipsis, Anástrofe. |
| **Pensamiento** | Metáfora, Símil, Hipérbole, Personificación, Antítesis. |
| **Estructura** | Paralelismo, Bimembración, Gradación, Quiasmo. |

## Referencias Principales

* Vaswani, A. et al. (2017). *Attention Is All You Need*.
* Unsloth AI. (2025). *LoRA Hot Swapping Guide*.
* Hugging Face. (2024). *FineWeb-Edu Dataset*.