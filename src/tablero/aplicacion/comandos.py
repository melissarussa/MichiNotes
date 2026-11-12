"""Patrón Comando: cada acción sabe hacerse y deshacerse. El Historial da Ctrl+Z / Ctrl+Y."""
from dataclasses import dataclass
from typing import Callable

from .bus_eventos import BusEventos


@dataclass
class Comando:
    descripcion: str
    hacer: Callable[[], None]
    deshacer: Callable[[], None]


class Historial:
    LIMITE = 200

    def __init__(self, bus: BusEventos | None = None):
        self._deshacer: list[Comando] = []
        self._rehacer: list[Comando] = []
        self.bus = bus

    def ejecutar(self, cmd: Comando) -> None:
        cmd.hacer()
        self._deshacer.append(cmd)
        del self._deshacer[:-self.LIMITE]
        self._rehacer.clear()
        self._avisar()

    def puede_deshacer(self) -> bool:
        return bool(self._deshacer)

    def puede_rehacer(self) -> bool:
        return bool(self._rehacer)

    def deshacer(self) -> bool:
        if not self._deshacer:
            return False
        cmd = self._deshacer.pop()
        cmd.deshacer()
        self._rehacer.append(cmd)
        self._avisar()
        return True

    def rehacer(self) -> bool:
        if not self._rehacer:
            return False
        cmd = self._rehacer.pop()
        cmd.hacer()
        self._deshacer.append(cmd)
        self._avisar()
        return True

    def limpiar(self) -> None:
        self._deshacer.clear()
        self._rehacer.clear()
        self._avisar()

    def _avisar(self) -> None:
        if self.bus:
            self.bus.emitir("historial_cambio")
