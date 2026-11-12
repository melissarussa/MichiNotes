import sqlite3
from pathlib import Path


def abrir_conexion(ruta: Path | str) -> sqlite3.Connection:
    if str(ruta) != ":memory:":
        Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(ruta)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")   # SQLite lo trae apagado
    con.execute("PRAGMA journal_mode = WAL")
    return con
