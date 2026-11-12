from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPen

from .base import ItemBase, fuente_de
from .. import dialogos

ALTO_FILA = 24
ALTO_TITULO = 34


class ItemLista(ItemBase):
    """Lista de tareas con casillas que se marcan con un clic."""

    def _casilla(self, i: int) -> QRectF:
        return QRectF(10, ALTO_TITULO + i * ALTO_FILA + 4, 14, 14)

    def dibujar(self, painter) -> None:
        r = self.rect()
        painter.setPen(QColor(0, 0, 0, 50))
        painter.setBrush(QColor(self.p.get("color", "#FFFFFF")))
        painter.drawRoundedRect(r, 6, 6)
        painter.setClipRect(r)
        texto = QColor(self.p.get("color_texto", "#222222"))
        f = fuente_de(self.p)
        negrita = fuente_de(self.p)
        negrita.setBold(True)
        painter.setFont(negrita)
        painter.setPen(texto)
        painter.drawText(QRectF(10, 4, r.width() - 20, ALTO_TITULO - 6), Qt.AlignmentFlag.AlignVCenter,
                         self.p.get("titulo", "Lista"))
        for i, it in enumerate(self.p.get("items", [])):
            c = self._casilla(i)
            painter.setPen(QPen(texto, 1.2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(c)
            if it.get("hecho"):
                painter.drawLine(c.left() + 3, c.center().y(), c.center().x() - 1, c.bottom() - 3)
                painter.drawLine(c.center().x() - 1, c.bottom() - 3, c.right() - 2, c.top() + 3)
            ff = fuente_de(self.p)
            ff.setBold(False)
            ff.setStrikeOut(bool(it.get("hecho")))
            painter.setFont(ff)
            painter.setPen(QColor("#888888") if it.get("hecho") else texto)
            painter.drawText(QRectF(32, ALTO_TITULO + i * ALTO_FILA, r.width() - 40, ALTO_FILA),
                             Qt.AlignmentFlag.AlignVCenter, it.get("texto", ""))
        painter.setClipping(False)
        _ = f

    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.MouseButton.LeftButton and not self._asa().contains(ev.pos()):
            items = self.p.get("items", [])
            for i in range(len(items)):
                if self._casilla(i).adjusted(-4, -4, 4, 4).contains(ev.pos()):
                    nuevos = [dict(x) for x in items]
                    nuevos[i]["hecho"] = not nuevos[i].get("hecho", False)
                    self.ctx.servicio.editar_propiedades(self.e.id, items=nuevos)
                    ev.accept()
                    return
        super().mousePressEvent(ev)

    def editar(self) -> None:
        r = dialogos.editar_lista(self.p.get("titulo", "Lista"), self.p.get("items", []))
        if r is not None:
            self.ctx.servicio.editar_propiedades(self.e.id, titulo=r[0], items=r[1])
