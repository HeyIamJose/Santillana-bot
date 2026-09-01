import os
import time
import warnings
from typing import List, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from PIL import Image

warnings.filterwarnings("ignore")

class Action(BaseModel):
    action_type: str = Field(
        description="Tipo de acción: 'click', 'connect', 'drag', 'type', 'wait', o 'done'"
    )
    target_description: str = Field(
        description="Breve descripción del elemento objetivo (ej. 'Palabra Teatro en sopa de letras' o 'Unir Paradoja con opción e')"
    )
    coordinates: List[int] = Field(
        description="Coordenadas normalizadas [x, y] en rango 0 a 1000 del elemento (centro exacto u origen)"
    )
    drop_coordinates: Optional[List[int]] = Field(
        default=None,
        description="Coordenadas normalizadas [x, y] de destino para acciones 'connect' o 'drag'"
    )
    text_to_type: Optional[str] = Field(
        default=None,
        description="Texto exacto a escribir sólo si action_type es 'type'"
    )

class LessonResponse(BaseModel):
    exercise_type: str = Field(
        description="Tipo de ejercicio identificado (ej. 'Sopa de Letras', 'Relacionar/Unir', 'Opción Múltiple', 'Verdadero/Falso', 'Completación', 'Navegación', 'Terminado')"
    )
    explanation: str = Field(
        description="Explicación breve del razonamiento académico para la solución"
    )
    actions: List[Action] = Field(
        description="Lista secuencial de acciones que el script debe ejecutar en pantalla"
    )

SYSTEM_PROMPT = """
Eres un experto resolviendo lecciones educativas interactivas de libros digitales de Santillana Web.
Analiza la captura de pantalla de la lección actual y determina las acciones exactas con el ratón y teclado necesarias para resolver correctamente las actividades visibles.

REGLAS DE COORDENADAS:
- La esquina superior izquierda de la imagen es [0, 0] (X=0, Y=0).
- La esquina inferior derecha de la imagen es [1000, 1000] (X=1000, Y=1000).
- Todas las coordenadas [x, y] deben estar dentro del rango 0 a 1000 y apuntar al CENTRO EXACTO de cada elemento o casilla de letra.

DISTINCIÓN CRÍTICA DE TIPOS DE ACCIÓN:
1. 'click': Para opciones individuales (Opción múltiple, V/F, casillas de verificación, enfoque de campos y botones como 'Comprobar', 'Enviar', 'Siguiente').
2. 'connect': Para ejercicios de UNIR / RELACIONAR PAREJAS O COLUMNAS (donde al hacer clic en un elemento se marca en verde y al hacer clic en el segundo se une con una flecha).
   - Usa 'coordinates' para la casilla origen (columna izquierda) y 'drop_coordinates' para la casilla destino (columna derecha).
3. 'drag': Para SOPAS DE LETRAS o arrastrar fichas físicas manteniendo presionado el ratón.
   - En SOPAS DE LETRAS: Usa 'coordinates' para la primera letra de la palabra y 'drop_coordinates' para la última letra de la palabra (manteniendo presionado el botón del ratón desde la primera hasta la última letra).
4. 'type': Para escribir respuestas en campos de texto (indica 'coordinates' del campo y 'text_to_type').
5. 'wait': Si la lección está cargando.
6. 'done': Si no hay más ejercicios visibles o la lección finalizó.

Asegúrate de responder siempre con la mejor respuesta académica posible para la lección de Santillana.
"""

def get_gemini_client(api_key: str = None):
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("No se encontró la GEMINI_API_KEY. Configúrala en el archivo .env o variable de entorno.")
    return genai.Client(api_key=key)

def analyze_lesson(
    image: Image.Image,
    model_name: str = "gemini-3.6-flash",
    api_key: str = None
) -> LessonResponse:
    """
    Envía la captura de pantalla a Gemini usando una estrategia de cascada rápida:
      - 1 intento a gemini-3.6-flash (avanzado). Si responde 503, salta de inmediato.
      - 2 intentos a gemini-3.5-flash (intermedio).
      - 5 intentos a gemini-3.1-flash-lite (último recurso).
    """
    client = get_gemini_client(api_key)
    
    # Plan personalizado de fallbacks rápido
    model_plan = [
        ("gemini-3.6-flash", 1, 1.0),
        ("gemini-3.5-flash", 2, 1.0),
        ("gemini-3.1-flash-lite", 5, 1.5)
    ]

    last_exception = None

    for current_model, max_attempts, initial_delay in model_plan:
        print(f"[Análisis] Consultando modelo: {current_model}")
        current_delay = initial_delay

        for attempt in range(1, max_attempts + 1):
            try:
                response = client.models.generate_content(
                    model=current_model,
                    contents=[image, SYSTEM_PROMPT],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=LessonResponse,
                        temperature=0.1,
                    )
                )
                if response and response.parsed:
                    return response.parsed

            except Exception as e:
                last_exception = e
                err_msg = str(e)
                is_busy = "503" in err_msg or "UNAVAILABLE" in err_msg or "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg

                if is_busy:
                    print(f"[Aviso 503] {current_model} ocupado (intento {attempt}/{max_attempts}).")
                    if attempt < max_attempts:
                        time.sleep(current_delay)
                        current_delay *= 1.5
                else:
                    print(f"[Aviso Error] {current_model}: {err_msg}")
                    break

        print(f"[Fallback Rápido] Saltando al siguiente modelo...")

    raise last_exception or RuntimeError("No se pudo obtener respuesta de la API tras probar la cascada de modelos.")
