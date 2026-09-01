import pyautogui
import time

# Medida de seguridad: si mueves el cursor a la esquina superior izquierda (0,0), el script se aborta
pyautogui.FAILSAFE = True

print("Iniciando en 3 segundos... ¡Cambia a la ventana destino!")
time.sleep(3)

# 1. Definir tus coordenadas fijas objetivo (X, Y)
# Reemplaza estos números con la posición exacta obtenida de tu rastreador o Spectacle
x_objetivo = 5400
y_objetivo = 1200

print(f"Moviendo ratón a posición fija: X={x_objetivo}, Y={y_objetivo}")

# 2. Mover suavemente el puntero hacia el punto exacto
pyautogui.moveTo(x_objetivo, y_objetivo, duration=0.8)

# 3. Hacer clic
pyautogui.click()

print("¡Clic realizado en las coordenadas fijas!")