"""Paneles flotantes de opciones (derecha del tablero), uno por herramienta, como en los mockups."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QButtonGroup, QColorDialog, QComboBox, QFontComboBox, QGridLayout, QHBoxLayout,
                               QLabel, QPushButton, QRadioButton, QSlider, QSpinBox, QVBoxLayout, QWidget)

from .tablero.items.dibujo import ESTILOS
from .tablero.items.figura import FORMAS

PALETA = ["#000000", "#FFFFFF", "#808080", "#E53935", "#FB8C00", "#FDD835", "#43A047", "#1E88E5", "#3949AB", "#8E24AA"]
COLORES_NOTA = ["#FFEB3B", "#FFCDD2", "#C8E6C9", "#BBDEFB", "#E1BEE7", "#FFE0B2", "#FFFFFF"]


class BotonColor(QPushButton):
    """Botón que muestra un color y abre el selector al hacer clic."""
    elegido = Signal(str)

    def __init__(self, color: str = "#000000", parent=None):
        super().__init__(parent)
        self.setFixedSize(34, 24)
        self.poner(color)
        self.clicked.connect(self._elegir)

    def poner(self, color: str) -> None:
        self.color = color
        self.setStyleSheet(f"background:{color}; border:1px solid #777; border-radius:4px;")

    def _elegir(self) -> None:
        c = QColorDialog.getColor(QColor(self.color), self, "Elegir color")
        if c.isValid():
            self.poner(c.name())
            self.elegido.emit(c.name())


def _paleta(callback, colores=PALETA) -> QWidget:
    w = QWidget()
    g = QGridLayout(w)
    g.setContentsMargins(0, 0, 0, 0)
    g.setSpacing(4)
    for i, c in enumerate(colores):
        b = QPushButton()
        b.setFixedSize(26, 26)
        b.setStyleSheet(f"background:{c}; border:1px solid #777; border-radius:5px;")
        b.clicked.connect(lambda _=False, col=c: callback(col))
        g.addWidget(b, i // 5, i % 5)
    return w


def _titulo(texto: str) -> QLabel:
    l = QLabel(texto)
    l.setObjectName("tituloPanel")
    return l


class PanelNotas(QWidget):
    tipo_cambiado = Signal(str)
    color_cambiado = Signal(str)

    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.addWidget(_titulo("Tipo de nota"))
        self.grupo = QButtonGroup(self)
        for i, (etq, tipo) in enumerate((("☑ Lista", "lista"), ("🗒 Nota", "nota"), ("🔗 Enlace", "enlace"))):
            r = QRadioButton(etq)
            r.setChecked(tipo == "nota")
            r.toggled.connect(lambda ok, t=tipo: ok and self.tipo_cambiado.emit(t))
            self.grupo.addButton(r, i)
            lay.addWidget(r)
        lay.addWidget(QLabel("Color de la nota"))
        lay.addWidget(_paleta(self.color_cambiado.emit, COLORES_NOTA))
        lay.addWidget(QLabel("Haz clic en el lienzo para crearla.\nDoble clic para editar."))
        lay.addStretch()


class PanelPincel(QWidget):
    cambiado = Signal(dict)

    def __init__(self):
        super().__init__()
        self.estado = {"color": "#222222", "grosor": 4, "estilo": "duro"}
        lay = QVBoxLayout(self)
        lay.addWidget(_titulo("Pincel"))
        lay.addWidget(QLabel("Color"))
        lay.addWidget(_paleta(self._color))
        fila = QHBoxLayout()
        self.boton = BotonColor(self.estado["color"])
        self.boton.elegido.connect(self._color)
        fila.addWidget(QLabel("Personalizado"))
        fila.addWidget(self.boton)
        lay.addLayout(fila)
        self.lbl = QLabel("Tamaño: 4 px")
        lay.addWidget(self.lbl)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(1, 40)
        self.slider.setValue(4)
        self.slider.valueChanged.connect(self._grosor)
        lay.addWidget(self.slider)
        lay.addWidget(QLabel("Tipo de pincel"))
        self.combo = QComboBox()
        self.combo.addItems(list(ESTILOS))
        self.combo.currentTextChanged.connect(lambda t: self._set(estilo=ESTILOS[t]))
        lay.addWidget(self.combo)
        lay.addStretch()

    def _set(self, **kw):
        self.estado.update(kw)
        self.cambiado.emit(dict(self.estado))

    def _color(self, c):
        self.boton.poner(c)
        self._set(color=c)

    def _grosor(self, v):
        self.lbl.setText(f"Tamaño: {v} px")
        self._set(grosor=v)


class PanelTexto(QWidget):
    """Formato de texto: se aplica a lo seleccionado y a los nuevos elementos."""
    cambiado = Signal(dict)

    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.addWidget(_titulo("Texto"))
        self.fuente = QFontComboBox()
        self.fuente.currentFontChanged.connect(lambda f: self.cambiado.emit({"fuente": f.family()}))
        lay.addWidget(self.fuente)
        fila = QHBoxLayout()
        fila.addWidget(QLabel("Tamaño"))
        self.tam = QSpinBox()
        self.tam.setRange(6, 96)
        self.tam.setValue(12)
        self.tam.valueChanged.connect(lambda v: self.cambiado.emit({"tamano": v}))
        fila.addWidget(self.tam)
        lay.addLayout(fila)
        fila = QHBoxLayout()
        for etq, clave, estilo in (("N", "negrita", "font-weight:bold"), ("K", "cursiva", "font-style:italic"),
                                   ("S", "subrayado", "text-decoration:underline")):
            b = QPushButton(etq)
            b.setCheckable(True)
            b.setFixedWidth(34)
            b.setStyleSheet(estilo)
            b.toggled.connect(lambda ok, k=clave: self.cambiado.emit({k: ok}))
            fila.addWidget(b)
        lay.addLayout(fila)
        fila = QHBoxLayout()
        for etq, v in (("⇤", "izquierda"), ("↔", "centro"), ("⇥", "derecha")):
            b = QPushButton(etq)
            b.setFixedWidth(34)
            b.clicked.connect(lambda _=False, val=v: self.cambiado.emit({"alineacion": val}))
            fila.addWidget(b)
        lay.addLayout(fila)
        lay.addWidget(QLabel("Color del texto"))
        lay.addWidget(_paleta(lambda c: self.cambiado.emit({"color_texto": c})))
        lay.addStretch()


class PanelFiguras(QWidget):
    cambiado = Signal(dict)

    def __init__(self):
        super().__init__()
        self.estado = {"forma": "rectangulo", "relleno": "", "borde": "#333333", "grosor": 2}
        lay = QVBoxLayout(self)
        lay.addWidget(_titulo("Figuras"))
        nombres = {"rectangulo": "▭ Rectángulo", "elipse": "◯ Elipse", "triangulo": "△ Triángulo",
                   "rombo": "◇ Rombo", "linea": "╱ Línea", "flecha": "➝ Flecha"}
        self.combo = QComboBox()
        for f in FORMAS:
            self.combo.addItem(nombres[f], f)
        self.combo.currentIndexChanged.connect(lambda _: self._set(forma=self.combo.currentData()))
        lay.addWidget(self.combo)
        f1 = QHBoxLayout()
        f1.addWidget(QLabel("Borde"))
        self.borde = BotonColor(self.estado["borde"])
        self.borde.elegido.connect(lambda c: self._set(borde=c))
        f1.addWidget(self.borde)
        lay.addLayout(f1)
        f2 = QHBoxLayout()
        f2.addWidget(QLabel("Relleno"))
        self.relleno = BotonColor("#FFFFFF")
        self.relleno.elegido.connect(lambda c: self._set(relleno=c))
        f2.addWidget(self.relleno)
        sin = QPushButton("Sin")
        sin.clicked.connect(lambda: self._set(relleno=""))
        f2.addWidget(sin)
        lay.addLayout(f2)
        f3 = QHBoxLayout()
        f3.addWidget(QLabel("Grosor"))
        self.grosor = QSpinBox()
        self.grosor.setRange(1, 20)
        self.grosor.setValue(2)
        self.grosor.valueChanged.connect(lambda v: self._set(grosor=v))
        f3.addWidget(self.grosor)
        lay.addLayout(f3)
        lay.addWidget(QLabel("Haz clic en el lienzo para colocarla."))
        lay.addStretch()

    def _set(self, **kw):
        self.estado.update(kw)
        self.cambiado.emit(dict(self.estado))


class PanelLienzo(QWidget):
    """Estilo de cuadrícula, fondo y widgets (panel 'Lienzo y cuadrícula' del mockup)."""
    estilo_cambiado = Signal(str)
    fondo_cambiado = Signal(str)
    nuevo_widget = Signal()

    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.addWidget(_titulo("Lienzo y cuadrícula"))
        fila = QHBoxLayout()
        for etq, v in (("Cuadrícula", "cuadricula"), ("Puntos", "puntos"), ("Liso", "liso")):
            b = QPushButton(etq)
            b.clicked.connect(lambda _=False, val=v: self.estilo_cambiado.emit(val))
            fila.addWidget(b)
        lay.addLayout(fila)
        f = QHBoxLayout()
        f.addWidget(QLabel("Color de fondo"))
        self.fondo = BotonColor("#FAFAFA")
        self.fondo.elegido.connect(self.fondo_cambiado.emit)
        f.addWidget(self.fondo)
        auto = QPushButton("Auto")
        auto.clicked.connect(lambda: self.fondo_cambiado.emit(""))
        f.addWidget(auto)
        lay.addLayout(f)
        lay.addWidget(_titulo("Widgets de notas"))
        w = QPushButton("＋ Añadir widget al escritorio")
        w.clicked.connect(self.nuevo_widget.emit)
        lay.addWidget(w)
        lay.addStretch()
