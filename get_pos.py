import time
from pynput.mouse import Controller

mouse = Controller()

print("Mueve el ratón por la pantalla para ver las coordenadas (Presiona Ctrl+C para salir):\n")

try:
    while True:
        x, y = mouse.position
        # \r sobreescribe la misma línea en la terminal para no llenar la consola de texto
        print(f"Coordenadas actuales -> X: {x} | Y: {y}   ", end="\r")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n\n¡Rastreo finalizado!")