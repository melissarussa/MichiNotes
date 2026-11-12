from PySide6.QtCore import QRectF, QUrl, Qt
from PySide6.QtGui import QColor, QDesktopServices, QFont

from .base import ItemBase, fuente_de
from .. import dialogos


class ItemEnlace(ItemBase):
    """Tarjeta con un enlace. Doble clic = abrir en el navegador; menú contextual = editar."""

    def dibujar(self, painter) -> None:
        r = self.rect()
        painter.setPen(QColor(0, 0, 0, 50))
        painter.setBrush(QColor(self.p.get("color", "#E3F2FD")))
        painter.drawRoundedRect(r, 8, 8)
        painter.setClipRect(r)
        f = fuente_de(self.p)
        f.setBold(True)
        painter.setFont(f)
        painter.setPen(QColor(self.p.get("color_texto", "#0D47A1")))
        painter.drawText(QRectF(12, 6, r.width() - 24, r.height() / 2), Qt.AlignmentFlag.AlignVCenter,
                         "🔗 " + self.p.get("titulo", "Enlace"))
        pequena = QFont(f)
        pequena.setBold(False)
        pequena.setPointSize(max(8, f.pointSize() - 3))
        painter.setFont(pequena)
        painter.setPen(QColor("#555555"))
        painter.drawText(QRectF(12, r.height() / 2, r.width() - 24, r.height() / 2 - 4),
                         Qt.AlignmentFlag.AlignVCenter, self.p.get("url", ""))
        painter.setClipping(False)

    def mouseDoubleClickEvent(self, ev) -> None:
        url = self.p.get("url", "")
        if url:
            QDesktopServices.openUrl(QUrl(url))
        else:
            self.editar()

    def editar(self) -> None:
        r = dialogos.editar_enlace(self.p.get("titulo", ""), self.p.get("url", ""))
        if r is not None:
            self.ctx.servicio.editar_propiedades(self.e.id, titulo=r[0], url=r[1])
