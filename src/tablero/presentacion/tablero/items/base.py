"""Clase base de todo lo que se dibuja en el tablero. Cada ítem guarda su Elemento (los datos)
y sabe pintarse; los cambios se envían al servicio, nunca directo a la base."""
import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QGraphicsItem

from ... import iconos
from ...estilo import ESCALA_FUENTE, FUENTE

ASA = 14   # tamaño del asa de redimensionar
GIRO_DIST = 28   # distancia del asa de giro sobre el borde superior
GIRO_R = 7       # radio del asa de giro

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
    girable = False          # las figuras se pueden girar (propiedad 'rotacion', en grados)

    def __init__(self, elemento, ctx):
        super().__init__()
        self.ctx = ctx
        self.e = elemento
        self._redim = False
        self._girando = False
        self._giro_vivo = 0.0
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
        self._aplicar_giro()
        self.al_actualizar()
        self.update()

    def al_actualizar(self) -> None:
        """Gancho para que cada tipo recalcule cachés (imagen, trazo...)."""

    def _aplicar_giro(self) -> None:
        if self.girable:
            self.setTransformOriginPoint(self.e.ancho / 2, self.e.alto / 2)    # gira sobre su centro
            self.setRotation(float(self.p.get("rotacion", 0)) % 360)

    @property
    def p(self) -> dict:
        return self.e.propiedades

    def rect(self) -> QRectF:
        return QRectF(0, 0, self.e.ancho, self.e.alto)

    def boundingRect(self) -> QRectF:
        extra = GIRO_DIST + GIRO_R if self.girable else 0
        return self.rect().adjusted(-3, -3 - extra, 3 + ASA, 3 + ASA)

    def shape(self):
        from PySide6.QtGui import QPainterPath
        r = QPainterPath()
        r.addRect(self.rect())
        if self._con_asa_giro():
            r.addEllipse(self._asa_giro())
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
        if self._con_asa_giro():
            c = self._asa_giro().center()
            painter.setPen(QPen(QColor("#2D7FF9"), 1.5))
            painter.drawLine(QPointF(self.e.ancho / 2, 0), QPointF(c.x(), c.y() + GIRO_R))
            painter.setBrush(QBrush(QColor("white")))
            painter.drawEllipse(self._asa_giro())

    def _con_asa_giro(self) -> bool:
        return self.girable and self.isSelected() and not self.e.bloqueado

    def _asa_giro(self) -> QRectF:
        return QRectF(self.e.ancho / 2 - GIRO_R, -GIRO_DIST - GIRO_R, 2 * GIRO_R, 2 * GIRO_R)

    def _asa(self) -> QRectF:
        return QRectF(self.e.ancho - ASA / 2, self.e.alto - ASA / 2, ASA, ASA)

    # ---- ratón: redimensionar
    def mousePressEvent(self, ev) -> None:
        if (self.redimensionable and self.isSelected() and not self.e.bloqueado
                and ev.button() == Qt.MouseButton.LeftButton and self._asa().contains(ev.pos())):
            self._redim = True
            ev.accept()
            return
        if self._con_asa_giro() and ev.button() == Qt.MouseButton.LeftButton and self._asa_giro().contains(ev.pos()):
            self._girando = True
            self._giro_vivo = self.rotation()
            ev.accept()
            return
        super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev) -> None:
        if self._redim:
            self.prepareGeometryChange()
            ancho0, alto0 = self.e.ancho, self.e.alto
            self.e.ancho = max(40.0, ev.pos().x())
            self.e.alto = max(30.0, ev.pos().y())
            if self.girable:
                self._reanclar(ancho0, alto0)
            self.update()
            return
        if self._girando:
            c = self.mapToScene(QPointF(self.e.ancho / 2, self.e.alto / 2))       # el centro no se mueve al girar
            p = ev.scenePos()
            ang = (math.degrees(math.atan2(p.y() - c.y(), p.x() - c.x())) + 90) % 360
            if ev.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                ang = round(ang / 15) * 15 % 360                                   # Shift: de 15 en 15 grados
            else:
                for recto in (0, 90, 180, 270, 360):                               # imán suave a los ángulos rectos
                    if abs(ang - recto) < 4:
                        ang = recto % 360
            self._giro_vivo = ang
            self.setRotation(ang)
            return
        super().mouseMoveEvent(ev)

    def _reanclar(self, ancho0: float, alto0: float) -> None:
        """Al redimensionar una figura girada, la esquina opuesta al asa se queda quieta en pantalla."""
        th = math.radians(self.rotation())
        dx, dy = (ancho0 - self.e.ancho) / 2, (alto0 - self.e.alto) / 2
        rx, ry = dx * math.cos(th) - dy * math.sin(th), dx * math.sin(th) + dy * math.cos(th)
        self.setTransformOriginPoint(self.e.ancho / 2, self.e.alto / 2)
        self.e.x, self.e.y = self.pos().x() + dx - rx, self.pos().y() + dy - ry
        self.setPos(self.e.x, self.e.y)

    def mouseReleaseEvent(self, ev) -> None:
        if self._redim:
            self._redim = False
            extra = {"x": self.e.x, "y": self.e.y} if self.girable else {}
            self.ctx.servicio.modificar(self.e.id, "Redimensionar", ancho=self.e.ancho, alto=self.e.alto, **extra)
            return
        if self._girando:
            self._girando = False
            self.ctx.servicio.editar_propiedades(self.e.id, rotacion=round(self._giro_vivo, 1))
            return
        super().mouseReleaseEvent(ev)

    def hoverMoveEvent(self, ev) -> None:
        if self.scene() is not None and self.scene().herramienta == "mano":
            self.unsetCursor()       # con la Mano, el cursor lo manda la vista (mano abierta)
            return
        if self._con_asa_giro() and self._asa_giro().contains(ev.pos()):
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            return
        sobre_asa = (self.redimensionable and self.isSelected() and not self.e.bloqueado
                     and self._asa().contains(ev.pos()))
        self.setCursor(Qt.CursorShape.SizeFDiagCursor if sobre_asa else Qt.CursorShape.ArrowCursor)

    def mouseDoubleClickEvent(self, ev) -> None:
        self.editar()

    def editar(self) -> None:
        """Cada tipo abre su diálogo de edición."""

    def posicion(self) -> QPointF:
        return self.pos()
