from dataclasses import dataclass


@dataclass
class Evento:
    id: str
    titulo: str
    inicio: str                # ISO 8601 (hora local, sin zona: "2026-10-29T09:00")
    fin: str | None = None
    calendario_id: str | None = None
    tablero_id: str | None = None
    descripcion: str = ""
    color: str = "#4F8EF7"
    aviso_minutos: int | None = None
    notificado: bool = False
