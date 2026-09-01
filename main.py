import sys
import time
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import GEMINI_API_KEY, MODEL_NAME, SCREEN_REGION
from screen_utils import capture_screen, draw_debug_overlay, get_screen_size
from gemini_solver import analyze_lesson
from action_executor import execute_action

def run_bot(auto_mode: bool = False):
    print("=" * 60)
    print("      BOT AUTOMATIZADO DE SANTILLANA WEB (Gemini Vision)")
    print("=" * 60)
    print(f"Modelo: {MODEL_NAME}")
    print(f"Modo: {'100% AUTOMÁTICO' if auto_mode else 'SUPERVISADO (Confirmación requerida)'}")
    print("Failsafe: Activo (Mueve el ratón a la esquina superior izquierda (0,0) para detener).")
    print("-" * 60)

    if not os.getenv("GEMINI_API_KEY") and not GEMINI_API_KEY:
        print("[ERROR CRÍTICO] Falta la GEMINI_API_KEY.")
        print("Por favor, agrega tu API Key en el archivo .env como:")
        print("GEMINI_API_KEY=tu_clave_aqui")
        return

    print("\nIniciando en 5 segundos... ¡Asegúrate de tener la lección de Santillana visible en pantalla!")
    for i in range(5, 0, -1):
        print(f" {i}...", end="\r", flush=True)
        time.sleep(1)
    print("\n¡Comenzando análisis!\n")

    step_count = 1
    screen_w, screen_h = get_screen_size()

    while True:
        print(f"\n--- PASO #{step_count} ---")
        
        # 1. Capturar pantalla
        print("[1/4] Capturando pantalla...")
        screenshot = capture_screen(region=SCREEN_REGION, save_path="last_capture.png")

        # 2. Analizar con Gemini
        print("[2/4] Enviando imagen a Gemini Vision para análisis...")
        try:
            response = analyze_lesson(screenshot, model_name=MODEL_NAME)
        except Exception as e:
            print(f"[Error de API] {e}")
            break

        print(f"\n>> Tipo de ejercicio detectado: {response.exercise_type}")
        print(f">> Razonamiento de Gemini: {response.explanation}\n")

        # Convertir objetos Pydantic a lista de diccionarios
        actions_list = [act.model_dump() for act in response.actions]

        # 3. Dibujar superposición de depuración
        overlay_path = draw_debug_overlay(screenshot, actions_list, save_path="debug_overlay.png")

        if not actions_list:
            print("[Aviso] No se detectaron acciones a realizar.")
            break

        # 4. Modo supervisado: solicitar confirmación si no está en modo automático
        if not auto_mode:
            print("Acciones propuestas:")
            for idx, act in enumerate(actions_list, 1):
                atype = act.get('action_type')
                desc = act.get('target_description')
                coords = act.get('coordinates')
                print(f"  {idx}. [{atype.upper()}] {desc} -> Coords 0-1000: {coords}")
            
            print(f"\nRevisa la imagen guardada '{overlay_path}' para ver las marcas visuales.")
            user_input = input("\n¿Ejecutar estas acciones? [S/n/q para salir]: ").strip().lower()
            
            if user_input in ['q', 'quit', 'exit']:
                print("Bot detenido por el usuario.")
                break
            elif user_input == 'n':
                print("Paso omitido por el usuario. Reintentando análisis...")
                continue

        # 5. Ejecutar acciones
        print("[3/4] Ejecutando acciones en la pantalla...")
        is_done = False
        for act in actions_list:
            if act.get("action_type") == "done":
                is_done = True
                print("Lección finalizada exitosamente.")
                break
            
            execute_action(act, screen_width=screen_w, screen_height=screen_h)

        if is_done:
            break

        step_count += 1
        print("[4/4] Esperando 3 segundos antes del siguiente paso...")
        time.sleep(3)

    print("\n¡Ejecución del Bot finalizada!")

if __name__ == "__main__":
    auto = "--auto" in sys.argv
    run_bot(auto_mode=auto)
