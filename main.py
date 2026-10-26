"""Punto de entrada. Ejecutar:  python main.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))   # permite "import tablero"

from tablero.infraestructura.base_datos.conexion import abrir_conexion
from tablero.infraestructura.base_datos.migrador import migrar


def main() -> None:
    con = abrir_conexion(Path("data") / "tablero.db")
    migrar(con)
    print("Base de datos lista. Siguiente paso: abrir la ventana (presentacion/app.py).")


if __name__ == "__main__":
    main()
