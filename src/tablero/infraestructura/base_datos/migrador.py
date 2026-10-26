"""Aplica los scripts de migraciones/ que falten, según PRAGMA user_version."""
import sqlite3
from pathlib import Path

CARPETA = Path(__file__).parent / "migraciones"


def migrar(con: sqlite3.Connection) -> None:
    actual = con.execute("PRAGMA user_version").fetchone()[0]
    for script in sorted(CARPETA.glob("*.sql")):
        numero = int(script.stem.split("_")[0])      # "001_inicial" -> 1
        if numero > actual:
            con.executescript(script.read_text(encoding="utf-8"))
            con.execute(f"PRAGMA user_version = {numero}")
            con.commit()
