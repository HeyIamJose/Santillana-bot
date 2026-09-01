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
    session_start_time = time.time()
    screen_w, screen_h = get_screen_size()

    while True:
        print(f"\n--- PASO #{step_count} ---")
        t_step_start = time.time()
        
        # 1. Capturar pantalla
        print("[1/4] Capturando pantalla...")
        t_cap_start = time.time()
        screenshot = capture_screen(region=SCREEN_REGION, save_path="last_capture.png")
        t_cap_end = time.time()
        cap_duration = t_cap_end - t_cap_start

        # 2. Analizar con Gemini
        print("[2/4] Enviando imagen a Gemini Vision para análisis...")
        t_gemini_start = time.time()
        try:
            response = analyze_lesson(screenshot, model_name=MODEL_NAME)
        except Exception as e:
            print(f"[Error de API] {e}")
            break
        t_gemini_end = time.time()
        gemini_duration = t_gemini_end - t_gemini_start

        print(f"\n>> Tipo de ejercicio detectado: {response.exercise_type}")
        print(f">> Razonamiento de Gemini: {response.explanation}")
        print(f"⏱️  Tiempo de respuesta de Gemini: {gemini_duration:.2f} segundos\n")

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
        t_exec_start = time.time()
        is_done = False
        for act in actions_list:
            if act.get("action_type") == "done":
                is_done = True
                print("Lección finalizada exitosamente.")
                break
            
            execute_action(act, screen_width=screen_w, screen_height=screen_h)

        t_exec_end = time.time()
        exec_duration = t_exec_end - t_exec_start
        t_step_end = time.time()
        step_total_duration = t_step_end - t_step_start

        print("-" * 50)
        print(f"⏱️  METRICAS PASO #{step_count}:")
        print(f"    - Análisis Gemini Vision  : {gemini_duration:.2f}s")
        print(f"    - Ejecución de Acciones   : {exec_duration:.2f}s")
        print(f"    - Tiempo Total del Paso   : {step_total_duration:.2f}s")
        print("-" * 50)

        if is_done:
            break

        step_count += 1
        print("[4/4] Esperando 3 segundos antes del siguiente paso...")
        time.sleep(3)

    total_session_duration = time.time() - session_start_time
    print(f"\n¡Ejecución del Bot finalizada! (Tiempo acumulado sesión: {total_session_duration:.2f}s)")

if __name__ == "__main__":
    auto = "--auto" in sys.argv
    run_bot(auto_mode=auto)
