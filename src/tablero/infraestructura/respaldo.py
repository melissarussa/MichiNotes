"""Copia de seguridad consistente con la API de backup de SQLite (segura aunque la app esté abierta)."""
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


def crear_respaldo(con: sqlite3.Connection, carpeta_datos: Path, destino: Path | str | None = None) -> Path:
    if destino is None:
        carpeta = carpeta_datos / "respaldos"
        carpeta.mkdir(exist_ok=True)
        destino = carpeta / f"tablero_{datetime.now():%Y%m%d_%H%M%S}.db"
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    dst = sqlite3.connect(destino)
    try:
        con.backup(dst)
    finally:
        dst.close()
    # las imágenes importadas viajan junto al respaldo
    recursos = carpeta_datos / "recursos"
    if recursos.exists():
        shutil.copytree(recursos, destino.with_suffix("") .parent / (destino.stem + "_recursos"),
                        dirs_exist_ok=True)
    return destino


def restaurar_respaldo(con: sqlite3.Connection, carpeta_datos: Path, origen: Path | str) -> None:
    """Reemplaza el contenido de la base abierta por el del respaldo."""
    origen = Path(origen)
    src = sqlite3.connect(origen)
    try:
        src.backup(con)
    finally:
        src.close()
    con.execute("PRAGMA foreign_keys = ON")
    carpeta_rec = origen.parent / (origen.stem + "_recursos")
    if carpeta_rec.exists():
        shutil.copytree(carpeta_rec, carpeta_datos / "recursos", dirs_exist_ok=True)
