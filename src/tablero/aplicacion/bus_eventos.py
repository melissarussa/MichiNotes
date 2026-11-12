"""Bus de eventos mínimo: la interfaz se suscribe y se redibuja cuando cambian los datos."""
from collections import defaultdict
from typing import Callable


class BusEventos:
    def __init__(self):
        self._oyentes: dict[str, list[Callable]] = defaultdict(list)

    def suscribir(self, evento: str, funcion: Callable) -> None:
        self._oyentes[evento].append(funcion)

    def emitir(self, evento: str, **datos) -> None:
        for f in list(self._oyentes[evento]):
            f(**datos)
