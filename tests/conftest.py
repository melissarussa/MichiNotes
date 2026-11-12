import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tablero.aplicacion.bus_eventos import BusEventos
from tablero.aplicacion.comandos import Historial
from tablero.aplicacion.servicio_tableros import ServicioElementos
from tablero.infraestructura.base_datos.conexion import abrir_conexion
from tablero.infraestructura.base_datos.migrador import migrar
from tablero.infraestructura.repositorios.sqlite_elementos import RepoElementos
from tablero.infraestructura.repositorios.sqlite_tableros import RepoTableros
from tablero.infraestructura.repositorios.sqlite_usuarios import RepoUsuarios


@pytest.fixture
def con():
    c = abrir_conexion(":memory:")
    migrar(c)
    return c


@pytest.fixture
def usuario(con):
    return RepoUsuarios(con).crear("Ana", None)


@pytest.fixture
def tablero(con, usuario):
    return RepoTableros(con, usuario.id).crear("Prueba")


@pytest.fixture
def servicio(con, usuario, tablero):
    bus = BusEventos()
    eventos = []
    for n in ("elemento_creado", "elemento_actualizado", "elemento_eliminado"):
        bus.suscribir(n, lambda _n=n, **d: eventos.append(_n))
    s = ServicioElementos(RepoElementos(con, usuario.id), bus, Historial(bus))
    s.eventos = eventos
    return s
