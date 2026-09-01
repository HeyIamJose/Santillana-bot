import sys
import os
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import load_env_file, MODEL_NAME
from screen_utils import capture_screen, draw_debug_overlay
from gemini_solver import analyze_lesson

load_env_file()

def test_api(image_path: str = None):
    print("=" * 60)
    print("   PRUEBA DE CONEXIÓN Y VISIÓN CON GEMINI API")
    print("=" * 60)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n[!] No se encontró GEMINI_API_KEY en el archivo .env o en el entorno.")
        print("Para probar la API de Gemini, crea un archivo llamado `.env` en este directorio con:")
        print("GEMINI_API_KEY=tu_api_key_aqui")
        print("\nPuedes obtener tu API Key gratuita en: https://aistudio.google.com/")
        return

    if image_path and os.path.exists(image_path):
        print(f"Cargando imagen desde: {image_path}")
        img = Image.open(image_path)
    else:
        print("Capturando pantalla actual...")
        img = capture_screen(save_path="test_capture.png")

    print(f"Enviando imagen a {MODEL_NAME}...")
    try:
        response = analyze_lesson(img, model_name=MODEL_NAME)
        print("\n=== RESPUESTA DE GEMINI ===")
        print(f"Tipo de ejercicio: {response.exercise_type}")
        print(f"Explicación: {response.explanation}\n")
        print("Acciones sugeridas:")
        
        actions_dict = [act.model_dump() for act in response.actions]
        for idx, act in enumerate(actions_dict, 1):
            print(f"  {idx}. Tipo: {act['action_type'].upper()} | Coords (0-1000): {act['coordinates']} | Objeto: {act['target_description']}")
            if act.get("drop_coordinates"):
                print(f"     -> Destino arrastre: {act['drop_coordinates']}")
            if act.get("text_to_type"):
                print(f"     -> Texto a escribir: '{act['text_to_type']}'")

        overlay_file = draw_debug_overlay(img, actions_dict, save_path="test_debug_overlay.png")
        print(f"\n[ÉXITO] Se generó la imagen con puntos anotados en: {overlay_file}")
        print("Abre 'test_debug_overlay.png' para verificar si los puntos coinciden con las opciones de Santillana.")

    except Exception as e:
        print(f"\n[ERROR] Ocurrió un error al consultar la API de Gemini: {e}")

if __name__ == "__main__":
    img_arg = sys.argv[1] if len(sys.argv) > 1 else None
    test_api(img_arg)
