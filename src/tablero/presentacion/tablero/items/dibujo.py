from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainterPath, QPainterPathStroker, QPen

from .base import ItemBase

ESTILOS = {"Duro redondo": "duro", "Resaltador": "resaltador", "Suave texturizado": "suave", "Pincel de óleo": "oleo"}


def pluma(props: dict) -> QPen:
    """Convierte las propiedades del trazo en un QPen (también lo usa la vista previa mientras se dibuja)."""
    color = QColor(props.get("color", "#222222"))
    g = float(props.get("grosor", 4))
    estilo = props.get("estilo", "duro")
    cap = Qt.PenCapStyle.RoundCap
    if estilo == "resaltador":
        color.setAlpha(90)
        g *= 3
        cap = Qt.PenCapStyle.FlatCap
    elif estilo == "suave":
        color.setAlpha(150)
    elif estilo == "oleo":
        color.setAlpha(225)
        g *= 1.6
    pen = QPen(color, g, Qt.PenStyle.SolidLine, cap, Qt.PenJoinStyle.RoundJoin)
    return pen


def trazado(puntos) -> QPainterPath:
    if not puntos:
        return QPainterPath()
    path = QPainterPath(QPointF(*puntos[0]))
    if len(puntos) == 1:
        path.lineTo(puntos[0][0] + 0.01, puntos[0][1] + 0.01)
    for x, y in puntos[1:]:
        path.lineTo(x, y)
    return path


class ItemDibujo(ItemBase):
    """Trazo a mano alzada. Los puntos son coordenadas del lienzo; mover el trazo cambia x,y."""
    redimensionable = False

    def al_actualizar(self) -> None:
        self._path = trazado(self.p.get("puntos", []))
        self._pen = pluma(self.p)
        st = QPainterPathStroker()
        st.setWidth(max(self._pen.widthF(), 10))
        self._forma = st.createStroke(self._path)

    def rect(self):
        return self._forma.boundingRect()

    def boundingRect(self):
        return self._forma.boundingRect().adjusted(-4, -4, 4, 4)

    def shape(self):
        return self._forma

    def dibujar(self, painter) -> None:
        painter.setPen(self._pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self._path)

    def _asa(self):
        from PySide6.QtCore import QRectF
        return QRectF()

    def mousePressEvent(self, ev) -> None:
        # sin asa de redimensionar
        super(ItemBase, self).mousePressEvent(ev)

    def mouseDoubleClickEvent(self, ev) -> None:
        pass
