"""Clase base de todo lo que se dibuja en el tablero. Cada ítem guarda su Elemento (los datos)
y sabe pintarse; los cambios se envían al servicio, nunca directo a la base."""
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QGraphicsItem

from ... import iconos
from ...estilo import ESCALA_FUENTE, FUENTE

ASA = 14   # tamaño del asa de redimensionar

ALINEACION = {"izquierda": Qt.AlignmentFlag.AlignLeft, "centro": Qt.AlignmentFlag.AlignHCenter,
              "derecha": Qt.AlignmentFlag.AlignRight}


def fuente_de(props: dict, base: int = 12) -> QFont:
    familia = props.get("fuente") or FUENTE        # por defecto: Dongle
    f = QFont(familia)
    tam = float(props.get("tamano", base))
    if familia == FUENTE:
        tam *= ESCALA_FUENTE                       # Dongle es muy pequeña: se agranda para que se lea igual
    f.setPointSizeF(tam)
    f.setBold(bool(props.get("negrita")))
    f.setItalic(bool(props.get("cursiva")))
    f.setUnderline(bool(props.get("subrayado")))
    return f


def bandera_alineacion(props: dict):
    return ALINEACION.get(props.get("alineacion", "izquierda"), Qt.AlignmentFlag.AlignLeft)


class ItemBase(QGraphicsItem):
    redimensionable = True

    def __init__(self, elemento, ctx):
        super().__init__()
        self.ctx = ctx
        self.e = elemento
        self._redim = False
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        self.aplicar(elemento)

    # ---- datos
    def aplicar(self, e) -> None:
        self.prepareGeometryChange()
        self.e = e
        self.setPos(e.x, e.y)
        self.setZValue(e.z_index)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, not e.bloqueado)
        self.al_actualizar()
        self.update()

    def al_actualizar(self) -> None:
        """Gancho para que cada tipo recalcule cachés (imagen, trazo...)."""

    @property
    def p(self) -> dict:
        return self.e.propiedades

    def rect(self) -> QRectF:
        return QRectF(0, 0, self.e.ancho, self.e.alto)

    def boundingRect(self) -> QRectF:
        return self.rect().adjusted(-3, -3, 3 + ASA, 3 + ASA)

    def shape(self):
        from PySide6.QtGui import QPainterPath
        r = QPainterPath()
        r.addRect(self.rect())
        return r

    # ---- pintado
    def paint(self, painter, option, widget=None) -> None:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.dibujar(painter)
        if self.isSelected():
            self.decorar(painter)
        if self.e.bloqueado:
            painter.drawPixmap(int(self.rect().right() - 22), int(self.rect().bottom() - 22), 18, 18,
                               iconos.pixmap("lock-key-bold.svg", iconos.COLOR_ICONO))

    def dibujar(self, painter) -> None:
        raise NotImplementedError

    def decorar(self, painter) -> None:
        pen = QPen(QColor("#2D7FF9"), 1.5, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(self.rect())
        if self.redimensionable and not self.e.bloqueado:
            painter.setPen(QPen(QColor("#2D7FF9")))
            painter.setBrush(QBrush(QColor("white")))
            painter.drawRect(self._asa())

    def _asa(self) -> QRectF:
        return QRectF(self.e.ancho - ASA / 2, self.e.alto - ASA / 2, ASA, ASA)

    # ---- ratón: redimensionar
    def mousePressEvent(self, ev) -> None:
        if (self.redimensionable and self.isSelected() and not self.e.bloqueado
                and ev.button() == Qt.MouseButton.LeftButton and self._asa().contains(ev.pos())):
            self._redim = True
            ev.accept()
            return
        super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev) -> None:
        if self._redim:
            self.prepareGeometryChange()
            self.e.ancho = max(40.0, ev.pos().x())
            self.e.alto = max(30.0, ev.pos().y())
            self.update()
            return
        super().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, ev) -> None:
        if self._redim:
            self._redim = False
            self.ctx.servicio.modificar(self.e.id, "Redimensionar", ancho=self.e.ancho, alto=self.e.alto)
            return
        super().mouseReleaseEvent(ev)

    def hoverMoveEvent(self, ev) -> None:
        sobre_asa = (self.redimensionable and self.isSelected() and not self.e.bloqueado
                     and self._asa().contains(ev.pos()))
        self.setCursor(Qt.CursorShape.SizeFDiagCursor if sobre_asa else Qt.CursorShape.ArrowCursor)

    def mouseDoubleClickEvent(self, ev) -> None:
        self.editar()

    def editar(self) -> None:
        """Cada tipo abre su diálogo de edición."""

    def posicion(self) -> QPointF:
        return self.pos()
