"""Contexto de sesión: arma repositorios y servicios para el usuario que inició sesión."""
import json
import sqlite3
from pathlib import Path

from .bus_eventos import BusEventos
from .comandos import Historial
from .servicio_tableros import ServicioElementos
from ..dominio.usuario import Usuario
from ..infraestructura.repositorios.sqlite_calendario import RepoCalendario
from ..infraestructura.repositorios.sqlite_configuracion import RepoConfiguracion
from ..infraestructura.repositorios.sqlite_elementos import RepoElementos
from ..infraestructura.repositorios.sqlite_tableros import RepoTableros


class Contexto:
    def __init__(self, con: sqlite3.Connection, carpeta_datos: Path, usuario: Usuario):
        self.con, self.carpeta_datos, self.usuario = con, carpeta_datos, usuario
        self.bus = BusEventos()
        self.historial = Historial(self.bus)
        self.repo_elementos = RepoElementos(con, usuario.id)
        self.tableros = RepoTableros(con, usuario.id)
        self.calendario = RepoCalendario(con, usuario.id)
        self.config = RepoConfiguracion(con)
        self.servicio = ServicioElementos(self.repo_elementos, self.bus, self.historial)
        self.calendario.asegurar_calendario_por_defecto()

    # preferencias por usuario guardadas en la tabla configuracion
    def _clave(self, c: str) -> str:
        return f"{self.usuario.id}:{c}"

    def widgets_notas(self) -> list[dict]:
        return json.loads(self.config.obtener(self._clave("widgets_notas"), "[]"))

    def guardar_widgets_notas(self, lista: list[dict]) -> None:
        self.config.guardar(self._clave("widgets_notas"), json.dumps(lista))
