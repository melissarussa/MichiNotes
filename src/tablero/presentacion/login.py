"""Acceso: iniciar sesión, crear cuenta y recuperar contraseña (diseño del mockup "Iniciar sesión").

Una sola ventana con fondo de notas (imagen a pantalla completa, recortada tipo "cover") y una tarjeta
centrada que cambia de página: login · registro · recuperar · código de recuperación.
La tarjeta y sus textos escalan con el tamaño de la ventana, igual que en el mockup."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QGuiApplication, QPainter, QPalette, QPixmap
from PySide6.QtWidgets import (QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QStackedWidget,
                               QVBoxLayout, QWidget)

from ..aplicacion.servicio_acceso import ErrorAcceso
from ..config import ruta_recurso

# colores medidos del mockup
TARJETA = "#E6D6CB"
CAMPO = "#81766B"
BOTON = "#62564E"
BOTON_HOVER = "#51463F"
TEXTO = "#241D19"
ROJO = "#A12A2A"
FUENTE = '"Open Sans", "Segoe UI", "Helvetica Neue", Arial, sans-serif'
FUENTE_TITULO = '"Quicksand", "Josefin Sans", "Segoe UI Semilight", "Segoe UI", sans-serif'

# la tarjeta del mockup mide 742 x 1122 sobre una imagen de 3000 x 1688 y está centrada
IMG_ANCHO, IMG_ALTO = 3000, 1688
TARJETA_ANCHO, TARJETA_ALTO = 742, 1122
ANCHO_BASE = 638          # ancho de la tarjeta en el mockup de referencia (unidad u = ancho / 638)


def _hoja(u: float) -> str:
    """Hoja de estilos de la tarjeta, medidas en px proporcionales a la unidad u."""
    p = lambda v, minimo=1: max(minimo, round(v * u))
    return f"""
QFrame#tarjeta {{ background: {TARJETA}; border: none; border-radius: {p(75)}px; }}
QFrame#tarjeta QLabel {{ background: transparent; color: {TEXTO}; font-family: {FUENTE}; font-size: {p(26, 13)}px; }}
QLabel#titulo {{ font-family: {FUENTE_TITULO}; font-size: {p(62, 26)}px; font-weight: 400; }}
QLabel#texto {{ font-size: {p(24, 12)}px; }}
QLabel#error {{ color: {ROJO}; font-size: {p(23, 12)}px; }}
QLabel#codigo {{ background: {CAMPO}; color: #FFFFFF; border-radius: {p(28)}px; padding: {p(22)}px {p(10)}px;
                 font-size: {p(40, 18)}px; font-weight: 700; }}
QLineEdit#campo {{ background: {CAMPO}; color: #FFFFFF; border: none; border-radius: {p(28)}px;
                   padding: 0 {p(20)}px; min-height: {p(100, 40)}px; max-height: {p(100, 40)}px;
                   font-family: {FUENTE}; font-size: {p(30, 14)}px;
                   selection-background-color: {BOTON}; selection-color: #FFFFFF; }}
QLineEdit#campo:focus {{ background: #75695F; }}
QPushButton#boton {{ background: {BOTON}; color: #FFFFFF; border: none; border-radius: {p(42)}px;
                     min-height: {p(83, 36)}px; max-height: {p(83, 36)}px; min-width: {p(254, 140)}px; padding: 0 {p(20)}px;
                     font-family: {FUENTE}; font-size: {p(32, 14)}px; font-weight: 700; }}
QPushButton#boton:hover {{ background: {BOTON_HOVER}; }}
QPushButton#boton:pressed {{ background: #403630; }}
QPushButton#boton:disabled {{ background: #A99D93; }}
QPushButton#enlace {{ background: transparent; color: {TEXTO}; border: none; padding: 0; min-height: 0;
                      text-align: left; font-family: {FUENTE}; font-size: {p(26, 12)}px; }}
QPushButton#enlace:hover {{ text-decoration: underline; }}
"""


class Fondo(QWidget):
    """Imagen de fondo que cubre toda la ventana (recortada, sin deformarse) y tarjeta centrada."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.imagen = QPixmap(ruta_recurso("imagenes", "fondo_login.jpg"))
        self.tarjeta = QFrame(self)
        self.tarjeta.setObjectName("tarjeta")
        self.contenido = None          # función(u, ancho): reescala la página o devuelve la altura que necesita
        self._u = 0.0

    def escala(self) -> float:
        return max(self.width() / IMG_ANCHO, self.height() / IMG_ALTO)

    def paintEvent(self, _):
        p = QPainter(self)
        if self.imagen.isNull():
            p.fillRect(self.rect(), QColor("#C9AF8E"))
            return
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        s = self.escala()
        w, h = IMG_ANCHO * s, IMG_ALTO * s
        p.drawPixmap(round((self.width() - w) / 2), round((self.height() - h) / 2),
                     round(w), round(h), self.imagen)

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self.colocar()

    def colocar(self):
        """Tarjeta del tamaño de la del mockup (un 3 % más grande para tapar la del fondo)."""
        s = self.escala()
        ancho = max(400, min(round(TARJETA_ANCHO * s * 1.03), self.width() - 24))
        u = ancho / ANCHO_BASE
        if abs(u - self._u) > 0.015:
            self._u = u
            self.tarjeta.setStyleSheet(_hoja(u))
            if self.contenido:
                self.contenido(u, ancho)
        alto = round(TARJETA_ALTO * s * 1.03)
        if self.contenido:
            alto = max(alto, self.contenido(None, ancho))
        alto = min(alto, self.height() - 24)
        self.tarjeta.setGeometry((self.width() - ancho) // 2, (self.height() - alto) // 2, ancho, alto)


class DialogoLogin(QDialog):
    LOGIN, REGISTRO, RECUPERAR, CODIGO = range(4)

    def __init__(self, acceso, parent=None):
        super().__init__(parent)
        self.acceso = acceso
        self.usuario = None
        self._pendiente = None           # usuario ya creado/validado que espera ver su código
        self.setWindowTitle("MichiNotes")
        self.setMinimumSize(760, 640)
        self.resize(1280, 800)

        self.fondo = Fondo(self)
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.addWidget(self.fondo)

        self.pila = QStackedWidget()
        caja = QVBoxLayout(self.fondo.tarjeta)
        caja.setContentsMargins(0, 0, 0, 0)
        caja.addWidget(self.pila)

        self._margenes = []              # layouts de las páginas, para reescalar sus márgenes
        self._crear_login()
        self._crear_registro()
        self._crear_recuperar()
        self._crear_codigo()
        self.fondo.contenido = self._reescalar
        self._ir(self.REGISTRO if not acceso.hay_usuarios() else self.LOGIN)

    # ------------------------------------------------------------ piezas
    def _pagina(self, titulo: str, texto: str | None = None):
        pag = QWidget()
        lay = QVBoxLayout(pag)
        lay.addStretch(2)
        t = QLabel(titulo)
        t.setObjectName("titulo")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t.setWordWrap(True)
        lay.addWidget(t)
        if texto:
            sub = QLabel(texto)
            sub.setObjectName("texto")
            sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sub.setWordWrap(True)
            lay.addWidget(sub)
        self.pila.addWidget(pag)
        self._margenes.append(lay)
        return pag, lay

    def _campo(self, lay, marcador: str, clave: bool = False) -> QLineEdit:
        c = QLineEdit()
        c.setObjectName("campo")
        c.setPlaceholderText(marcador)
        if clave:
            c.setEchoMode(QLineEdit.EchoMode.Password)
        pal = c.palette()
        pal.setColor(QPalette.ColorRole.PlaceholderText, QColor("#F3ECE6"))
        c.setPalette(pal)
        lay.addWidget(c)
        return c

    def _enlace(self, texto: str, destino=None) -> QPushButton:
        b = QPushButton(texto)
        b.setObjectName("enlace")
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setFlat(True)
        b.setAutoDefault(False)
        if destino is not None:
            b.clicked.connect(lambda: self._ir(destino))
        return b

    def _boton(self, texto: str, accion) -> QPushButton:
        b = QPushButton(texto)
        b.setObjectName("boton")
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setAutoDefault(False)
        b.clicked.connect(accion)
        return b

    def _centrar(self, lay, w):
        lay.addWidget(w, 0, Qt.AlignmentFlag.AlignHCenter)

    def _error(self, lay) -> QLabel:
        e = QLabel("")
        e.setObjectName("error")
        e.setWordWrap(True)
        e.setAlignment(Qt.AlignmentFlag.AlignCenter)
        e.hide()
        lay.addWidget(e)
        return e

    def _enviar_con(self, campos, accion):
        for c in campos:
            c.returnPressed.connect(accion)

    # ------------------------------------------------------------ páginas
    def _crear_login(self):
        _, lay = self._pagina("Iniciar sesión")
        self.l_ident = self._campo(lay, "correo o nombre de usuario")
        self.l_clave = self._campo(lay, "contraseña", True)
        lay.addWidget(self._enlace("¿olvidó su contraseña?", self.RECUPERAR))
        self.l_error = self._error(lay)
        self._centrar(lay, self._boton("Ingresar", self._entrar))
        self._centrar(lay, self._enlace("¿No tiene cuenta? Crear cuenta", self.REGISTRO))
        lay.addStretch(3)
        self._enviar_con((self.l_ident, self.l_clave), self._entrar)

    def _crear_registro(self):
        _, lay = self._pagina("Crear cuenta")
        self.r_nombre = self._campo(lay, "nombre de usuario")
        self.r_correo = self._campo(lay, "correo")
        self.r_clave = self._campo(lay, "contraseña", True)
        self.r_conf = self._campo(lay, "confirmar contraseña", True)
        self.r_error = self._error(lay)
        self._centrar(lay, self._boton("Crear cuenta", self._registrar))
        self._centrar(lay, self._enlace("¿Ya tiene cuenta? Iniciar sesión", self.LOGIN))
        lay.addStretch(3)
        self._enviar_con((self.r_nombre, self.r_correo, self.r_clave, self.r_conf), self._registrar)

    def _crear_recuperar(self):
        _, lay = self._pagina(
            "Recuperar contraseña",
            "Escriba su usuario o correo, el código de recuperación que recibió al crear la cuenta y su nueva contraseña.")
        self.c_ident = self._campo(lay, "correo o nombre de usuario")
        self.c_codigo = self._campo(lay, "código de recuperación")
        self.c_clave = self._campo(lay, "nueva contraseña", True)
        self.c_conf = self._campo(lay, "confirmar nueva contraseña", True)
        self.c_error = self._error(lay)
        self._centrar(lay, self._boton("Restablecer", self._recuperar))
        self._centrar(lay, self._enlace("Volver a iniciar sesión", self.LOGIN))
        lay.addStretch(3)
        self._enviar_con((self.c_ident, self.c_codigo, self.c_clave, self.c_conf), self._recuperar)

    def _crear_codigo(self):
        _, lay = self._pagina("Guarde su código")
        self.k_texto = QLabel("")
        self.k_texto.setObjectName("texto")
        self.k_texto.setWordWrap(True)
        self.k_texto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.k_texto)
        self.k_codigo = QLabel("")
        self.k_codigo.setObjectName("codigo")
        self.k_codigo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.k_codigo.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lay.addWidget(self.k_codigo)
        self.k_copiar = self._enlace("Copiar código")
        self.k_copiar.clicked.connect(self._copiar)
        lay.addWidget(self.k_copiar, 0, Qt.AlignmentFlag.AlignHCenter)
        self._centrar(lay, self._boton("Continuar", self._continuar))
        lay.addStretch(3)

    # ------------------------------------------------------------ navegación y escala
    def _ir(self, pagina: int):
        for e in (self.l_error, self.r_error, self.c_error):
            e.hide()
            e.setText("")
        if pagina == self.LOGIN:
            self.l_clave.clear()
            (self.l_ident if not self.l_ident.text() else self.l_clave).setFocus()
        elif pagina == self.REGISTRO:
            self.r_nombre.setFocus()
        elif pagina == self.RECUPERAR:
            self.c_ident.setText(self.l_ident.text())
            self.c_codigo.setFocus()
        self.pila.setCurrentIndex(pagina)
        self.fondo.colocar()

    def _reescalar(self, u, ancho):
        """Con u: reescala márgenes. Sin u: devuelve la altura que pide la página actual con ese ancho."""
        if u is not None:
            m, sep = round(46 * u), max(6, round(14 * u))
            for lay in self._margenes:
                lay.setContentsMargins(m, round(40 * u), m, round(40 * u))
                lay.setSpacing(sep)
            return 0
        lay = self.pila.currentWidget().layout()
        return max(lay.totalHeightForWidth(ancho), lay.sizeHint().height()) + 8

    def _mostrar_error(self, etiqueta: QLabel, msg: str):
        etiqueta.setText(msg)
        etiqueta.show()
        self.fondo.colocar()

    # ------------------------------------------------------------ acciones
    def _entrar(self):
        try:
            self.usuario = self.acceso.entrar(self.l_ident.text(), self.l_clave.text())
            self.accept()
        except ErrorAcceso as e:
            self._mostrar_error(self.l_error, str(e))

    def _registrar(self):
        try:
            if not self.r_correo.text().strip():        # en el formulario el correo es obligatorio
                raise ErrorAcceso("Escriba su correo.")
            u = self.acceso.registrar(self.r_nombre.text(), self.r_clave.text(),
                                      self.r_correo.text(), self.r_conf.text())
        except ErrorAcceso as e:
            self._mostrar_error(self.r_error, str(e))
            return
        codigo = self.acceso.nuevo_codigo_recuperacion(u.id)
        self._mostrar_codigo(u, codigo, "¡Cuenta creada! Si olvida su contraseña, este código es la única forma de recuperarla. "
                                        "Guárdelo en un lugar seguro: no se vuelve a mostrar.")

    def _recuperar(self):
        try:
            u, codigo = self.acceso.recuperar_clave(self.c_ident.text(), self.c_codigo.text(),
                                                    self.c_clave.text(), self.c_conf.text())
        except ErrorAcceso as e:
            self._mostrar_error(self.c_error, str(e))
            return
        self._mostrar_codigo(u, codigo, "Contraseña restablecida. El código anterior ya no sirve; "
                                        "este es su nuevo código de recuperación. Guárdelo, no se vuelve a mostrar.")

    def _mostrar_codigo(self, usuario, codigo: str, texto: str):
        self._pendiente = usuario
        self.k_texto.setText(texto)
        self.k_codigo.setText(codigo)
        self.k_copiar.setText("Copiar código")
        for c in (self.r_clave, self.r_conf, self.c_codigo, self.c_clave, self.c_conf):
            c.clear()
        self._ir(self.CODIGO)

    def _copiar(self):
        QGuiApplication.clipboard().setText(self.k_codigo.text())
        self.k_copiar.setText("¡Copiado!")

    def _continuar(self):
        """Entra con la cuenta recién creada o recuperada."""
        self.usuario = self._pendiente
        self.accept()

    def reject(self):
        # si ya se creó la cuenta / se restableció la clave, cerrar la ventana equivale a continuar
        if self.pila.currentIndex() == self.CODIGO and self._pendiente:
            self._continuar()
        else:
            super().reject()
