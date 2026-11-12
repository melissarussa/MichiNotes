"""Widget de notas: ventanita sin bordes, siempre visible, que guarda su texto y posición."""
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget


class WidgetNota(QWidget):
    def __init__(self, datos: dict, guardar, cerrar, parent=None):
        super().__init__(parent)
        self.datos, self._guardar, self._cerrar = datos, guardar, cerrar
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("QWidget{background:#FFF59D;color:#222;} QPlainTextEdit{border:none;font-size:13px;}"
                           "QPushButton{border:none;background:transparent;font-size:14px;}")
        self.resize(220, 200)
        self.move(datos.get("x", 80), datos.get("y", 80))
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 4, 6, 6)
        fila = QHBoxLayout()
        fila.addWidget(QLabel("📝 Nota"))
        fila.addStretch()
        x = QPushButton("✕")
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
