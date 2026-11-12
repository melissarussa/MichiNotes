import math

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QBrush, QColor, QPen, QPolygonF

from .base import ItemBase

FORMAS = ("rectangulo", "elipse", "triangulo", "rombo", "linea", "flecha")


class ItemFigura(ItemBase):
    def dibujar(self, painter) -> None:
        g = float(self.p.get("grosor", 2))
        pen = QPen(QColor(self.p.get("borde", "#333333")), g)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        relleno = self.p.get("relleno", "")
        painter.setBrush(QBrush(QColor(relleno)) if relleno else Qt.BrushStyle.NoBrush)
        r = self.rect().adjusted(g / 2, g / 2, -g / 2, -g / 2)
        forma = self.p.get("forma", "rectangulo")
        if forma == "elipse":
            painter.drawEllipse(r)
        elif forma == "triangulo":
            painter.drawPolygon(QPolygonF([QPointF(r.center().x(), r.top()), r.bottomRight(), r.bottomLeft()]))
        elif forma == "rombo":
            painter.drawPolygon(QPolygonF([QPointF(r.center().x(), r.top()), QPointF(r.right(), r.center().y()),
                                           QPointF(r.center().x(), r.bottom()), QPointF(r.left(), r.center().y())]))
        elif forma in ("linea", "flecha"):
            a, b = r.topLeft(), r.bottomRight()
            painter.drawLine(a, b)
            if forma == "flecha":
                ang = math.atan2(b.y() - a.y(), b.x() - a.x())
                largo = 12 + g * 2
                for d in (math.radians(155), -math.radians(155)):
                    painter.drawLine(b, QPointF(b.x() + largo * math.cos(ang + d), b.y() + largo * math.sin(ang + d)))
        else:
            painter.drawRoundedRect(r, 4, 4) if self.p.get("redondeado") else painter.drawRect(r)
