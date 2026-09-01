import os
import sys

# Asegurar que el directorio del proyecto esté en sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def load_env_file(filepath=None):
    """Carga variables desde el archivo .env si existe."""
    if filepath is None:
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip().strip("'\"")

load_env_file()

# Configuración de Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

# Configuración de PyAutoGUI
FAILSAFE = True
PAUSE_BETWEEN_ACTIONS = 1.0  # segundos
MOVE_DURATION = 0.5  # tiempo de movimiento suave del cursor

# Configuración de pantalla (None para pantalla completa)
SCREEN_REGION = None
