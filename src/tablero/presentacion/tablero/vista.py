from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QGraphicsView


class VistaTablero(QGraphicsView):
    zoom_cambiado = Signal(float)

    def __init__(self, escena, parent=None):
        super().__init__(escena, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.SmartViewportUpdate)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._zoom = 1.0
        self._pan = None
        self._cursor_antes = None
        self.modo_mano = False        # herramienta Mano: el botón izquierdo mueve la vista
        self.centerOn(0, 0)

    def poner_zoom(self, z: float) -> None:
        z = max(0.2, min(4.0, z))
        self.resetTransform()
        self.scale(z, z)
        self._zoom = z
        self.zoom_cambiado.emit(z)

    def wheelEvent(self, ev) -> None:
        if ev.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.poner_zoom(self._zoom * (1.15 if ev.angleDelta().y() > 0 else 1 / 1.15))
            ev.accept()
        else:
            super().wheelEvent(ev)

    # el botón del medio (o el izquierdo con la herramienta Mano) mueve el lienzo sin tocar los elementos
    def mousePressEvent(self, ev) -> None:
        if ev.button() == Qt.MouseButton.MiddleButton or (self.modo_mano and ev.button() == Qt.MouseButton.LeftButton):
            self._pan = ev.position().toPoint()
            self._boton_pan = ev.button()
            self._cursor_antes = self.viewport().cursor()
            self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)
            ev.accept()
            return
        super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev) -> None:
        if self._pan is not None:
            d = ev.position().toPoint() - self._pan
            self._pan = ev.position().toPoint()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - d.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - d.y())
            ev.accept()
            return
        super().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, ev) -> None:
        if self._pan is not None and ev.button() == self._boton_pan:
            self._pan = None
            if self._cursor_antes is not None:
                self.viewport().setCursor(self._cursor_antes)
            ev.accept()
            return
        super().mouseReleaseEvent(ev)
