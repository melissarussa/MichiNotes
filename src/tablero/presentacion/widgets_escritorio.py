"""Widget de notas: ventanita sin bordes, siempre visible, que guarda su texto y posición."""
from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget

from . import iconos


class WidgetNota(QWidget):
    def __init__(self, datos: dict, guardar, cerrar, parent=None):
        super().__init__(parent)
        self.datos, self._guardar, self._cerrar = datos, guardar, cerrar
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("QWidget{background:#FFF59D;color:#222;} QPlainTextEdit{border:none;background:transparent;}"
                           "QPushButton{border:none;background:transparent;padding:0;min-height:0;}"
                           "QLabel{background:transparent;}")
        self.resize(220, 200)
        self.move(datos.get("x", 80), datos.get("y", 80))
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 4, 6, 6)
        fila = QHBoxLayout()
        ic = QLabel()
        ic.setPixmap(iconos.pixmap("note-pencil-bold.svg", iconos.COLOR_ICONO).scaled(
            20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        fila.addWidget(ic)
        fila.addWidget(QLabel("Nota"))
        fila.addStretch()
        x = QPushButton()
        x.setIcon(iconos.icono("x-bold.svg"))
        x.setIconSize(QSize(18, 18))
        x.clicked.connect(self._cerrar_widget)
        fila.addWidget(x)
        lay.addLayout(fila)
        self.texto = QPlainTextEdit(datos.get("texto", ""))
        self.texto.textChanged.connect(self._cambio)
        lay.addWidget(self.texto)
        self._pos = None
        self._timer = QTimer(self, singleShot=True, interval=600)
        self._timer.timeout.connect(self._persistir)

    def _cambio(self):
        self._timer.start()

    def _persistir(self):
        self.datos.update(texto=self.texto.toPlainText(), x=self.x(), y=self.y())
        self._guardar()

    def _cerrar_widget(self):
        self._cerrar(self)
        self.close()

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self._pos = ev.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, ev):
        if self._pos is not None and ev.buttons() & Qt.MouseButton.LeftButton:
            self.move(ev.globalPosition().toPoint() - self._pos)

    def mouseReleaseEvent(self, ev):
        self._pos = None
        self._persistir()
