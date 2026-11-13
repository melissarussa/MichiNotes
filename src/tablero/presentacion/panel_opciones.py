"""Paneles flotantes de opciones (derecha del tablero), uno por herramienta, como la plantilla:
cabecera con icono + nombre de la función, fichas en rejilla para elegir y selectores tipo píldora.
Todo en colores planos (los colores y bordes están en estilos/claro.qss)."""
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QFont, QFontDatabase
from PySide6.QtWidgets import (QButtonGroup, QColorDialog, QComboBox, QGridLayout, QHBoxLayout,
                               QLabel, QPushButton, QToolButton, QVBoxLayout, QWidget)

from . import iconos
from .estilo import FUENTE
from .tablero.items.dibujo import ESTILOS
from .tablero.items.figura import FORMAS

PALETA = ["#000000", "#FFFFFF", "#808080", "#E53935", "#FB8C00", "#FDD835", "#43A047", "#1E88E5", "#3949AB", "#8E24AA"]
COLORES_NOTA = ["#FFEB3B", "#FFCDD2", "#C8E6C9", "#BBDEFB", "#E1BEE7", "#FFE0B2", "#FFFFFF"]
TAM_FICHA = QSize(24, 24)


# ---------------------------------------------------------------- piezas reutilizables
class BotonColor(QPushButton):
    """Cuadro de color plano; al hacer clic abre el selector de colores."""
    elegido = Signal(str)

    def __init__(self, color: str = "#000000", parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 28)
        self.poner(color)
        self.clicked.connect(self._elegir)

    def poner(self, color: str) -> None:
        self.color = color
        self.setStyleSheet(f"BotonColor {{ background:{color}; border:none; border-radius:10px; padding:0; min-height:0; }}")

    def _elegir(self) -> None:
        c = QColorDialog.getColor(QColor(self.color), self.window(), "Elegir color", QColorDialog.ColorDialogOption.DontUseNativeDialog)
        if c.isValid():
            self.poner(c.name())
            self.elegido.emit(c.name())


def _titulo(icono: str, texto: str) -> QWidget:
    """Cabecera: círculo con el icono de la función + su nombre."""
    w = QWidget()
    fila = QHBoxLayout(w)
    fila.setContentsMargins(0, 0, 0, 0)
    fila.setSpacing(8)
    ins = QLabel()
    ins.setObjectName("insignia")
    ins.setFixedSize(34, 34)
    ins.setAlignment(Qt.AlignmentFlag.AlignCenter)
    ins.setPixmap(iconos.pixmap(icono, iconos.COLOR_ACTIVO).scaled(
        18, 18, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
    fila.addWidget(ins)
    t = QLabel(texto)
    t.setObjectName("tituloPanel")
    fila.addWidget(t, 1)
    return w


def _subtitulo(texto: str) -> QLabel:
    s = QLabel(texto)
    s.setObjectName("subtitulo")
    return s


def _ficha(icono: str, ayuda: str, marcable: bool = True, mini: bool = False) -> QToolButton:
    b = QToolButton()
    b.setObjectName("fichaMini" if mini else "ficha")
    b.setIcon(iconos.icono(icono))
    b.setIconSize(QSize(18, 18) if mini else TAM_FICHA)
    b.setToolTip(ayuda)
    b.setCheckable(marcable)
    return b


def _rejilla(widgets, columnas: int) -> QWidget:
    w = QWidget()
    g = QGridLayout(w)
    g.setContentsMargins(0, 0, 0, 0)
    g.setSpacing(6)
    for i, x in enumerate(widgets):
        g.addWidget(x, i // columnas, i % columnas, Qt.AlignmentFlag.AlignLeft)
    g.setColumnStretch(columnas, 1)      # las fichas quedan pegadas a la izquierda, sin estirarse
    return w


def _grupo_exclusivo(fichas, marcada: int = 0) -> QButtonGroup:
    """Solo una ficha marcada a la vez (como un radio)."""
    g = QButtonGroup(fichas[0])
    g.setExclusive(True)
    for f in fichas:
        g.addButton(f)
    if marcada is not None:
        fichas[marcada].setChecked(True)
    return g


def _paleta(callback, colores=PALETA) -> QWidget:
    botones = []
    for c in colores:
        b = QPushButton()
        b.setFixedSize(28, 28)
        b.setToolTip(c)
        b.setStyleSheet(f"background:{c}; border:none; border-radius:10px; padding:0; min-height:0;")
        b.clicked.connect(lambda _=False, col=c: callback(col))
        botones.append(b)
    return _rejilla(botones, 5)


def _selector(valores, actual) -> QComboBox:
    """Selector tipo píldora con una lista corta de números."""
    c = QComboBox()
    for v in valores:
        c.addItem(str(v), v)
    c.setCurrentIndex(max(c.findData(actual), 0))
    return c


def _selector_fuente() -> QComboBox:
    """Desplegable con TODAS las fuentes latinas instaladas (Dongle primero). Cada nombre se ve en su
    propia fuente pero a un tamaño fijo, así la lista no se agranda; muestra 8 a la vez y tiene scroll."""
    c = QComboBox()
    familias = [f for f in QFontDatabase.families(QFontDatabase.WritingSystem.Latin) if not f.startswith("@")]
    resto = sorted((f for f in set(familias) if f != FUENTE), key=str.lower)
    for nombre in [FUENTE] + resto:
        c.addItem(nombre, nombre)
        tam = 22 if nombre == FUENTE else 13       # Dongle es muy pequeña
        c.setItemData(c.count() - 1, QFont(nombre, tam), Qt.ItemDataRole.FontRole)
    c.setMaxVisibleItems(8)
    c.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
    c.setMinimumContentsLength(8)           # que no estire el panel por el nombre largo de una fuente
    return c


def _fila(texto: str, widget: QWidget) -> QWidget:
    w = QWidget()
    f = QHBoxLayout(w)
    f.setContentsMargins(0, 0, 0, 0)
    f.addWidget(_subtitulo(texto), 1)
    f.addWidget(widget)
    return w


def _base(panel: QWidget) -> QVBoxLayout:
    lay = QVBoxLayout(panel)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(5)
    return lay


# ---------------------------------------------------------------- paneles
class PanelNotas(QWidget):
    tipo_cambiado = Signal(str)
    color_cambiado = Signal(str)

    def __init__(self):
        super().__init__()
        lay = _base(self)
        lay.addWidget(_titulo("note-blank-bold.svg", "Notas"))
        lay.addWidget(_subtitulo("Tipo"))
        fichas = []
        for icono, tipo, ayuda in (("list-bullets-bold.svg", "lista", "Lista"), ("note-blank-bold.svg", "nota", "Nota"),
                                   ("link-simple-horizontal-bold.svg", "enlace", "Enlace")):
            f = _ficha(icono, ayuda)
            f.clicked.connect(lambda _=False, t=tipo: self.tipo_cambiado.emit(t))
            fichas.append(f)
        self._grupo = _grupo_exclusivo(fichas, 1)
        lay.addWidget(_rejilla(fichas, 4))
        lay.addWidget(_subtitulo("Color"))
        lay.addWidget(_paleta(self.color_cambiado.emit, COLORES_NOTA))
        pista = QLabel("Clic en el lienzo para crearla.\nDoble clic para editar.")
        pista.setWordWrap(True)
        lay.addWidget(pista)
        lay.addStretch()


class PanelPincel(QWidget):
    cambiado = Signal(dict)

    def __init__(self):
        super().__init__()
        self.estado = {"color": "#222222", "grosor": 4, "estilo": "duro"}
        lay = _base(self)
        lay.addWidget(_titulo("pencil-simple-line-bold.svg", "Pincel"))
        lay.addWidget(_subtitulo("Tipo de pincel"))
        fichas = []
        for nombre, codigo in ESTILOS.items():
            f = _ficha(f"trazo-{codigo}.svg", nombre)
            f.clicked.connect(lambda _=False, c=codigo: self._set(estilo=c))
            fichas.append(f)
        self._grupo = _grupo_exclusivo(fichas, 0)
        lay.addWidget(_rejilla(fichas, 4))
        lay.addWidget(_subtitulo("Color"))
        lay.addWidget(_paleta(self._color))
        self.boton = BotonColor(self.estado["color"])
        self.boton.elegido.connect(self._color)
        lay.addWidget(_fila("Otro color", self.boton))
        self.tam = _selector([1, 2, 3, 4, 6, 8, 10, 12, 16, 20, 24, 32, 40], 4)
        self.tam.currentIndexChanged.connect(lambda _: self._set(grosor=self.tam.currentData()))
        lay.addWidget(_fila("Tamaño", self.tam))
        lay.addStretch()

    def _set(self, **kw):
        self.estado.update(kw)
        self.cambiado.emit(dict(self.estado))

    def _color(self, c):
        self.boton.poner(c)
        self._set(color=c)


class PanelTexto(QWidget):
    """Formato de texto: se aplica a lo seleccionado y a los nuevos elementos."""
    cambiado = Signal(dict)

    def __init__(self):
        super().__init__()
        lay = _base(self)
        lay.addWidget(_titulo("text-t-bold.svg", "Texto"))
        self.fuente = _selector_fuente()
        self.fuente.currentIndexChanged.connect(lambda _: self.cambiado.emit({"fuente": self.fuente.currentData()}))
        lay.addWidget(self.fuente)
        self.tam = _selector([8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 48, 64, 72], 12)
        self.tam.currentIndexChanged.connect(lambda _: self.cambiado.emit({"tamano": self.tam.currentData()}))
        lay.addWidget(_fila("Tamaño", self.tam))
        estilos = []
        for icono, clave, ayuda in (("text-b-bold.svg", "negrita", "Negrita"), ("text-italic-bold.svg", "cursiva", "Cursiva"),
                                    ("text-underline-bold.svg", "subrayado", "Subrayado")):
            f = _ficha(icono, ayuda)
            f.toggled.connect(lambda ok, k=clave: self.cambiado.emit({k: ok}))
            estilos.append(f)
        lay.addWidget(_rejilla(estilos, 4))
        alin = []
        for icono, v, ayuda in (("text-align-left-bold.svg", "izquierda", "Izquierda"),
                                ("text-align-center-bold.svg", "centro", "Centro"),
                                ("text-align-right-bold.svg", "derecha", "Derecha")):
            f = _ficha(icono, ayuda)
            f.clicked.connect(lambda _=False, val=v: self.cambiado.emit({"alineacion": val}))
            alin.append(f)
        self._grupo = _grupo_exclusivo(alin, 0)
        lay.addWidget(_rejilla(alin, 4))
        lay.addWidget(_subtitulo("Color del texto"))
        lay.addWidget(_paleta(lambda c: self.cambiado.emit({"color_texto": c})))
        lay.addStretch()


class PanelFiguras(QWidget):
    cambiado = Signal(dict)

    ICONOS = {"rectangulo": "rectangle-bold.svg", "elipse": "circle-bold.svg", "triangulo": "triangle-bold.svg",
              "rombo": "diamond-bold.svg", "linea": "line-segment-bold.svg", "flecha": "arrow-down-right-bold.svg"}
    NOMBRES = {"rectangulo": "Rectángulo", "elipse": "Elipse", "triangulo": "Triángulo", "rombo": "Rombo",
               "linea": "Línea", "flecha": "Flecha"}

    def __init__(self):
        super().__init__()
        self.estado = {"forma": "rectangulo", "relleno": "", "borde": "#333333", "grosor": 2}
        lay = _base(self)
        lay.addWidget(_titulo("circle-bold.svg", "Figuras"))
        lay.addWidget(_subtitulo("Formas"))
        fichas = []
        for forma in FORMAS:
            f = _ficha(self.ICONOS[forma], self.NOMBRES[forma])
            f.clicked.connect(lambda _=False, fo=forma: self._set(forma=fo))
            fichas.append(f)
        self._grupo = _grupo_exclusivo(fichas, 0)
        lay.addWidget(_rejilla(fichas, 4))
        self.borde = BotonColor(self.estado["borde"])
        self.borde.elegido.connect(lambda c: self._set(borde=c))
        lay.addWidget(_fila("Borde", self.borde))
        self.relleno = BotonColor("#FFFFFF")
        self.relleno.elegido.connect(lambda c: self._set(relleno=c))
        sin = _ficha("x-bold.svg", "Sin relleno", marcable=False, mini=True)
        sin.clicked.connect(lambda: self._set(relleno=""))
        cont = QWidget()
        h = QHBoxLayout(cont)
        h.setContentsMargins(0, 0, 0, 0)
        h.addWidget(self.relleno)
        h.addWidget(sin)
        lay.addWidget(_fila("Relleno", cont))
        self.grosor = _selector([1, 2, 3, 4, 6, 8, 12, 16, 20], 2)
        self.grosor.currentIndexChanged.connect(lambda _: self._set(grosor=self.grosor.currentData()))
        lay.addWidget(_fila("Grosor", self.grosor))
        lay.addWidget(QLabel("Clic en el lienzo para colocarla."))
        lay.addStretch()

    def _set(self, **kw):
        self.estado.update(kw)
        self.cambiado.emit(dict(self.estado))


class PanelLienzo(QWidget):
    """Estilo de cuadrícula, fondo y widgets de escritorio (panel 'Lienzo' del mockup)."""
    estilo_cambiado = Signal(str)
    fondo_cambiado = Signal(str)
    nuevo_widget = Signal()

    def __init__(self):
        super().__init__()
        lay = _base(self)
        lay.addWidget(_titulo("grid-four-bold.svg", "Lienzo"))
        lay.addWidget(_subtitulo("Cuadrícula"))
        fichas = []
        for icono, v, ayuda in (("grid-four-bold.svg", "cuadricula", "Cuadrícula"), ("dots-nine-bold.svg", "puntos", "Puntos"),
                                ("square-bold.svg", "liso", "Liso")):
            f = _ficha(icono, ayuda)
            f.clicked.connect(lambda _=False, val=v: self.estilo_cambiado.emit(val))
            fichas.append(f)
        self._grupo = _grupo_exclusivo(fichas, 0)
        lay.addWidget(_rejilla(fichas, 4))
        self.fondo = BotonColor("#FAFAFA")
        self.fondo.elegido.connect(self.fondo_cambiado.emit)
        auto = _ficha("x-bold.svg", "Color automático", marcable=False, mini=True)
        auto.clicked.connect(lambda: (self.fondo.poner("#FAFAFA"), self.fondo_cambiado.emit("")))
        cont = QWidget()
        h = QHBoxLayout(cont)
        h.setContentsMargins(0, 0, 0, 0)
        h.addWidget(self.fondo)
        h.addWidget(auto)
        lay.addWidget(_fila("Fondo", cont))
        lay.addWidget(_subtitulo("Widgets de notas"))
        w = QPushButton(" Añadir widget")
        w.setIcon(iconos.icono("plus-bold.svg", normal=iconos.COLOR_ACTIVO))
        w.setIconSize(QSize(20, 20))
        w.clicked.connect(self.nuevo_widget.emit)
        lay.addWidget(w)
        lay.addStretch()
