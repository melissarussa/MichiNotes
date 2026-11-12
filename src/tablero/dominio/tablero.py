from dataclasses import dataclass, field
from typing import Any


@dataclass
class Tablero:
    id: str
    nombre: str
    propietario_id: str | None = None
    config: dict[str, Any] = field(default_factory=dict)   # estilo de lienzo, color de fondo
    creado_en: str = ""
    actualizado_en: str = ""
    eliminado_en: str | None = None
