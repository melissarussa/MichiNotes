"""Rutas y constantes. Los datos van en la carpeta de datos del usuario,
nunca junto al ejecutable (con PyInstaller --onefile esa carpeta es temporal)."""
import os
import sys
from pathlib import Path

NOMBRE_APP = "MichiNotes"

def ruta_recurso(subcarpeta: str, nombre_archivo: str) -> str:
    # Esta funcion devuelve la ruta absoluta a un archivo dentro de la carpeta recursos
    # empaquetado con PyInstaller los recursos quedan en sys._MEIPASS
    raiz_proyecto = Path(getattr(sys, "_MEIPASS", None) or Path(__file__).resolve().parent.parent.parent)
    ruta = raiz_proyecto / "recursos" / subcarpeta / nombre_archivo
    return str(ruta)


def carpeta_datos() -> Path:
    # Se puede forzar con la variable TABLERO_DATOS (útil para pruebas)
    forzada = os.environ.get("TABLERO_DATOS")
    if forzada:
        ruta = Path(forzada)
    else:
        try:
            from PySide6.QtCore import QStandardPaths
            base = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
            ruta = Path(base) / NOMBRE_APP if base else Path.home() / f".{NOMBRE_APP}"
        except ImportError:
            ruta = Path.home() / f".{NOMBRE_APP}"
    ruta.mkdir(parents=True, exist_ok=True)
    return ruta


def ruta_db(carpeta: Path | None = None) -> Path:
    return (carpeta or carpeta_datos()) / "tablero.db"


