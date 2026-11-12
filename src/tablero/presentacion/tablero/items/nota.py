from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from .base import ItemBase, bandera_alineacion, fuente_de
from .. import dialogos


class ItemNota(ItemBase):
    """Nota adhesiva con color de fondo."""

    def dibujar(self, painter) -> None:
        r = self.rect()
        painter.setPen(QColor(0, 0, 0, 40))
        painter.setBrush(QColor(self.p.get("color", "#FFEB3B")))
        painter.drawRoundedRect(r, 6, 6)
        painter.setPen(QColor(self.p.get("color_texto", "#222222")))
        painter.setFont(fuente_de(self.p))
        painter.drawText(r.adjusted(10, 10, -10, -10),
                         int(bandera_alineacion(self.p) | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap),
                         self.p.get("texto", ""))

    def editar(self) -> None:
        nuevo = dialogos.editar_texto("Editar nota", self.p.get("texto", ""))
        if nuevo is not None:
            self.ctx.servicio.editar_propiedades(self.e.id, texto=nuevo)


class ItemTexto(ItemBase):
    """Texto libre sin fondo."""

    def dibujar(self, painter) -> None:
        painter.setPen(QColor(self.p.get("color_texto", "#222222")))
        painter.setFont(fuente_de(self.p, 14))
        painter.drawText(self.rect(), int(bandera_alineacion(self.p) | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap),
                         self.p.get("texto", ""))

    def decorar(self, painter) -> None:
        super().decorar(painter)

    def editar(self) -> None:
        nuevo = dialogos.editar_texto("Editar texto", self.p.get("texto", ""))
        if nuevo is not None:
            self.ctx.servicio.editar_propiedades(self.e.id, texto=nuevo)
