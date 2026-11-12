"""Entidad Elemento: todo lo que se puede poner en el tablero."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from .utiles import ahora, nuevo_id

TIPOS = ("nota", "lista", "enlace", "figura", "imagen", "texto", "dibujo")

TAMANOS_INICIALES = {
    "nota": (200, 160), "lista": (220, 200), "enlace": (240, 70),
    "figura": (140, 100), "imagen": (240, 180), "texto": (200, 50), "dibujo": (0, 0),
}


@dataclass
class Elemento:
    tipo: str
    tablero_id: str
    id: str = field(default_factory=nuevo_id)
    x: float = 0.0
    y: float = 0.0
    ancho: float = 200.0
    alto: float = 150.0
    z_index: int = 0
    bloqueado: bool = False
    propiedades: dict[str, Any] = field(default_factory=dict)
    padre_id: str | None = None
    revision: int = 0
    creado_en: str = field(default_factory=ahora)
    actualizado_en: str = field(default_factory=ahora)
    eliminado_en: str | None = None

    def copia(self) -> "Elemento":
        c = replace(self)
        c.propiedades = dict(self.propiedades)
        return c


def nuevo_elemento(tipo: str, tablero_id: str, x: float, y: float, **props) -> Elemento:
    if tipo not in TIPOS:
        raise ValueError(f"Tipo desconocido: {tipo}")
    ancho, alto = TAMANOS_INICIALES[tipo]
    return Elemento(tipo=tipo, tablero_id=tablero_id, x=x, y=y,
                    ancho=ancho, alto=alto, propiedades=props)
