import os
from typing import List, Any
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

FIGURAS_EXTENDIDAS = {
    "Personificación": "PROSOPOPEYA. Atribuir cualidades humanas a objetos inanimados. EJEMPLO: 'La ciudad nos miraba con ojos de asfalto'.",
    "Animalización": "ZOOMORFISMO. Atribuir rasgos animales a seres humanos o cosas. EJEMPLO: 'Sus manos eran garras que buscaban el pan'.",
    "Cosificación": "REIFICACIÓN. Tratar a una persona o concepto vivo como un objeto inerte. EJEMPLO: 'Mi abuelo es un mueble más en el rincón'.",
    "Antítesis": "CONTRASTE LÓGICO. Enfrentar dos ideas de significado opuesto. EJEMPLO: 'Es tan corto el amor y tan largo el olvido'.",
    "Onomatopeya": "IMITACIÓN FÓNICA. Utilizar palabras que imitan sonidos reales. EJEMPLO: 'El tic-tac del reloj marcaba su agonía'.",
    "Gradación": "CLÍMAX O ESCALERA. Encadenar términos que ascienden o descienden en intensidad. EJEMPLO: 'En tierra, en humo, en polvo, en sombra, en nada'.",
    "Eufemismo": "SUSTITUCIÓN DECOROSA. Sustituir una palabra dura por una expresión más suave. EJEMPLO: 'Pasó a mejor vida' en lugar de 'Murió'."
}


def get_mask(palabra: str, figura: str) -> str | None:
    """Procesa la solicitud de forma discreta a través de la API, sin warnings de tipado."""
    definicion = FIGURAS_EXTENDIDAS.get(figura, "Generar un poema con rigor técnico.")

    prompt = f"""Genera UN SOLO poema de 4 versos.
FIGURA OBLIGATORIA: [{figura}: {definicion}]
PALABRA OBLIGATORIA: {palabra}
REGLA DE ORO: La precisión técnica de la figura es prioridad máxima. Solo devuelve el poema, sin notas ni introducciones."""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Eres un experto en retórica y métrica poética."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        return completion.choices[0].message.content.strip()
    except Exception:
        return None