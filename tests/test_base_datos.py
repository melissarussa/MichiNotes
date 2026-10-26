import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tablero.infraestructura.base_datos.conexion import abrir_conexion
from tablero.infraestructura.base_datos.migrador import migrar


def test_migrar_crea_las_tablas():
    con = abrir_conexion(":memory:")
    migrar(con)
    tablas = {f[0] for f in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"usuarios", "tableros", "elementos", "recursos", "calendarios",
            "eventos_calendario", "cambios", "configuracion"} <= tablas
