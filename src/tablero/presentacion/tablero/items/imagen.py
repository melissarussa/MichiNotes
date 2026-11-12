from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPixmap

from .base import ItemBase


class ItemImagen(ItemBase):
    def al_actualizar(self) -> None:
        ruta = self.p.get("recurso", "")
        if getattr(self, "_ruta", None) != ruta:
            self._ruta = ruta
            self._pm = QPixmap(str(self.ctx.carpeta_datos / ruta)) if ruta else QPixmap()

    def dibujar(self, painter) -> None:
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        if self._pm.isNull():
            painter.setPen(QColor("#999999"))
            painter.setBrush(QColor("#EEEEEE"))
            painter.drawRect(self.rect())
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Imagen no encontrada")
        else:
            painter.drawPixmap(self.rect().toRect(), self._pm)
