"""Punto de entrada: python main.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from tablero.presentacion.app import ejecutar  # noqa: E402

if __name__ == "__main__":
    sys.exit(ejecutar())
