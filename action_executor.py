import time
import pyautogui
import pyperclip
from config import FAILSAFE, MOVE_DURATION, PAUSE_BETWEEN_ACTIONS
from screen_utils import normalized_to_pixel, get_screen_size

# Habilitar failsafe global
pyautogui.FAILSAFE = FAILSAFE

def clamp_pixel(px: int, py: int, screen_width: int, screen_height: int, margin: int = 5):
    """
    Limita las coordenadas de píxeles para evitar tocar exactamente los bordes (0, 0) de la pantalla
    y no disparar Failsafe por accidente.
    """
    safe_x = max(margin, min(px, screen_width - margin))
    safe_y = max(margin, min(py, screen_height - margin))
    return safe_x, safe_y

def execute_action(action: dict, screen_width: int = None, screen_height: int = None, region_offset=(0, 0)):
    """
    Ejecuta una acción devuelta por Gemini en la pantalla física.
    Soporta:
      - 'click': Clic simple en un punto.
      - 'connect': Clic en origen + Clic en destino (para unir parejas / columnas).
      - 'drag': Arrastre físico manteniendo botón presionado (para Sopas de Letras).
      - 'type': Escritura de texto.
    """
    if screen_width is None or screen_height is None:
        screen_width, screen_height = get_screen_size()

    atype = action.get("action_type", "").lower()
    desc = action.get("target_description", "")
    coords = action.get("coordinates", [0, 0])
    off_x, off_y = region_offset

    if not coords or len(coords) < 2:
        print(f"[Acción Omitida] Coordenadas inválidas: {coords}")
        return

    raw_px, raw_py = normalized_to_pixel(coords[0], coords[1], screen_width, screen_height, off_x, off_y)
    px, py = clamp_pixel(raw_px, raw_py, screen_width, screen_height)

    print(f"\n[Ejecutando] {atype.upper()} -> '{desc}' en píxeles ({px}, {py})")

    if atype == "click":
        pyautogui.moveTo(px, py, duration=MOVE_DURATION)
        pyautogui.click()
        time.sleep(PAUSE_BETWEEN_ACTIONS)

    elif atype == "connect":
        drop_coords = action.get("drop_coordinates", [0, 0])
        raw_dpx, raw_dpy = normalized_to_pixel(drop_coords[0], drop_coords[1], screen_width, screen_height, off_x, off_y)
        dpx, dpy = clamp_pixel(raw_dpx, raw_dpy, screen_width, screen_height)
        print(f"            Conectando Pareja (Clic Origen -> Clic Destino): ({px}, {py}) -> ({dpx}, {dpy})...")
        
        # Clic 1: Origen
        pyautogui.moveTo(px, py, duration=MOVE_DURATION)
        pyautogui.click()
        time.sleep(0.3)
        
        # Clic 2: Destino
        pyautogui.moveTo(dpx, dpy, duration=MOVE_DURATION)
        pyautogui.click()
        time.sleep(PAUSE_BETWEEN_ACTIONS)

    elif atype == "drag":
        drop_coords = action.get("drop_coordinates", [0, 0])
        raw_dpx, raw_dpy = normalized_to_pixel(drop_coords[0], drop_coords[1], screen_width, screen_height, off_x, off_y)
        dpx, dpy = clamp_pixel(raw_dpx, raw_dpy, screen_width, screen_height)
        print(f"            Arrastre Físico Sostenido (Sopa de letras): ({px}, {py}) ===> ({dpx}, {dpy})...")
        
        # Mover al punto inicial (primera letra), presionar, mover al punto final (última letra) y soltar
        pyautogui.moveTo(px, py, duration=MOVE_DURATION)
        pyautogui.mouseDown()
        time.sleep(0.2)
        pyautogui.moveTo(dpx, dpy, duration=0.6)
        time.sleep(0.2)
        pyautogui.mouseUp()
        time.sleep(PAUSE_BETWEEN_ACTIONS)

    elif atype == "type":
        text = action.get("text_to_type", "")
        print(f"            Escribiendo texto: '{text}'...")
        
        pyautogui.moveTo(px, py, duration=MOVE_DURATION)
        pyautogui.click()
        time.sleep(0.2)
        
        # Seleccionar todo y borrar contenido previo si lo hubiera
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        time.sleep(0.1)
        
        # Usar portapapeles para evitar problemas con tildes y caracteres en español
        pyperclip.copy(text)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(PAUSE_BETWEEN_ACTIONS)

    elif atype == "wait":
        print("            Esperando 2 segundos a que termine de cargar...")
        time.sleep(2)

    elif atype == "done":
        print("            ¡Lección marcada como finalizada!")

    else:
        print(f"[Aviso] Tipo de acción desconocido: '{atype}'")
