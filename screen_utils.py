import os
import pyautogui
from PIL import Image, ImageGrab, ImageDraw, ImageFont

def get_screen_size():
    """Retorna (ancho, alto) de la pantalla principal en píxeles."""
    return pyautogui.size()

def capture_screen(region=None, save_path=None):
    """
    Captura la pantalla completa o una región específica en Linux X11 usando ImageGrab/PyAutoGUI.
    region: tuple (left, top, width, height) o (left, top, right, bottom) según el método.
    """
    try:
        # Intentar captura nativa de PIL ImageGrab (funciona rápido en X11)
        if region:
            # region para ImageGrab es bbox (left, upper, right, lower)
            bbox = (region[0], region[1], region[0] + region[2], region[1] + region[3])
            screenshot = ImageGrab.grab(bbox=bbox)
        else:
            screenshot = ImageGrab.grab()
    except Exception as e:
        print(f"[Aviso] ImageGrab falló ({e}), intentando pyautogui.screenshot()...")
        if region:
            screenshot = pyautogui.screenshot(region=region)
        else:
            screenshot = pyautogui.screenshot()
    
    if save_path:
        screenshot.save(save_path)
        print(f"[Captura] Guardada exitosamente en {save_path}")
        
    return screenshot

def normalized_to_pixel(norm_x, norm_y, width, height, offset_x=0, offset_y=0):
    """
    Convierte coordenadas normalizadas (0 a 1000) a coordenadas de píxeles reales.
    """
    px = int(offset_x + (norm_x / 1000.0) * width)
    py = int(offset_y + (norm_y / 1000.0) * height)
    return px, py

def draw_debug_overlay(image, actions, save_path="debug_overlay.png", region_offset=(0, 0)):
    """
    Dibuja una marca visual sobre una copia de la imagen para validar las acciones.
    """
    img_copy = image.copy()
    draw = ImageDraw.Draw(img_copy)
    w, h = img_copy.size
    off_x, off_y = region_offset

    for idx, act in enumerate(actions, start=1):
        atype = act.get("action_type", "").lower()
        coords = act.get("coordinates", [0, 0])
        desc = act.get("target_description", f"Acción {idx}")

        if not coords or len(coords) < 2:
            continue

        px, py = normalized_to_pixel(coords[0], coords[1], w, h)

        if atype == "click":
            r = 15
            draw.ellipse((px - r, py - r, px + r, py + r), outline="red", width=3)
            draw.ellipse((px - 3, py - 3, px + 3, py + 3), fill="red")
            draw.text((px + 18, py - 10), f"{idx}. Click: {desc}", fill="red")

        elif atype == "connect":
            drop_coords = act.get("drop_coordinates", [0, 0])
            dpx, dpy = normalized_to_pixel(drop_coords[0], drop_coords[1], w, h)
            draw.ellipse((px - 10, py - 10, px + 10, py + 10), fill="cyan", outline="blue", width=2)
            draw.line((px, py, dpx, dpy), fill="cyan", width=3)
            draw.ellipse((dpx - 10, dpy - 10, dpx + 10, dpy + 10), fill="cyan", outline="blue", width=2)
            draw.text((px + 12, py - 10), f"{idx}. Conectar: {desc}", fill="blue")

        elif atype == "drag":
            drop_coords = act.get("drop_coordinates", [0, 0])
            dpx, dpy = normalized_to_pixel(drop_coords[0], drop_coords[1], w, h)
            draw.ellipse((px - 8, py - 8, px + 8, py + 8), fill="blue")
            draw.line((px, py, dpx, dpy), fill="green", width=4)
            draw.ellipse((dpx - 10, dpy - 10, dpx + 10, dpy + 10), outline="green", width=3)
            draw.text((px + 12, py - 10), f"{idx}. Arrastrar (Sopa): {desc}", fill="blue")

        elif atype == "type":
            text = act.get("text_to_type", "")
            r = 12
            draw.rectangle((px - r, py - r, px + r, py + r), outline="purple", width=3)
            draw.text((px + 15, py - 10), f"{idx}. Escribir '{text}': {desc}", fill="purple")

    img_copy.save(save_path)
    print(f"[Debug] Imagen anotada guardada en: {save_path}")
    return save_path
