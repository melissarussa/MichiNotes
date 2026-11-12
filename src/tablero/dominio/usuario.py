from dataclasses import dataclass


@dataclass
class Usuario:
    id: str
    nombre: str
    correo: str | None = None
