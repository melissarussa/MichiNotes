"""Pantalla del tablero: lienzo + barra flotante inferior (como el mockup) + panel de opciones flotante."""
from pathlib import Path

from PySide6.QtCore import QPointF, Qt,QSize
from PySide6.QtGui import QKeySequence, QPixmap, QShortcut,QIcon
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QComboBox, QLineEdit, QPlainTextEdit, QButtonGroup, QFileDialog, QFrame, QHBoxLayout, QLabel, QMessageBox, QStackedWidget, QToolButton, QVBoxLayout, QWidget)

from ..infraestructura.recursos import importar_imagen
from .basurero import DialogoBasurero
from .panel_opciones import PanelFiguras, PanelLienzo, PanelNotas, PanelPincel, PanelTexto
from .tablero.escena import EscenaTablero
from .tablero.items.base import ItemBase
from .tablero.vista import VistaTablero

HERRAMIENTAS = [  # (id, símbolo, ayuda)
    ("seleccionar", "↖", "Seleccionar / mover (V)"),
    ("nota", "🗒", "Notas, listas y enlaces (N)"),
    ("pincel", "🖌", "Pincel (B)"),
    ("borrador", "⌫", "Borrador de trazos (E)"),
    ("figura", "⬟", "Figuras (S)"),
    ("imagen", "🖼", "Insertar imagen (I)"),
    ("texto", "T", "Texto (T)"),
]
FORMATO_TEXTO = ("nota", "lista", "enlace", "texto")


class VentanaTablero(QWidget):
    def __init__(self, ctx, menu_global, parent=None):
        super().__init__(parent)
        self.ctx = ctx
        self.menu_global = menu_global
        self.opciones = {"color_nota": "#FFEB3B", "texto": {}, "pincel": {}, "figura": {}}
        self.escena = EscenaTablero(ctx, self.opciones)
        self.vista = VistaTablero(self.escena)
        self.vista.setFrameShape(QFrame.Shape.NoFrame)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.vista)
        self._tipo_nota = "nota"
        self._crear_barra()
        self._crear_panel()
        self._atajos()
        ctx.bus.suscribir("historial_cambio", self._estado_historial)
        self.cambiar_herramienta("seleccionar")

    # ---------- construcción
    def _crear_barra(self):
        self.barra = QFrame(self)
        self.barra.setObjectName("barraFlotante")
        h = QHBoxLayout(self.barra)
        h.setContentsMargins(10, 6, 10, 6)
        h.setSpacing(4)
        self.grupo = QButtonGroup(self)
        self.grupo.setExclusive(True)
        self.botones = {}
        for hid, simbolo, ayuda in HERRAMIENTAS:
            b = QToolButton()
            b.setText(simbolo)
            b.setToolTip(ayuda)
            b.setCheckable(hid != "imagen")
            b.setObjectName("herramienta")
            if hid != "imagen":
                self.grupo.addButton(b)
            b.clicked.connect(lambda _=False, i=hid: self.cambiar_herramienta(i))
            h.addWidget(b)
            self.botones[hid] = b
        for simbolo, ayuda, f in (("↶", "Deshacer (Ctrl+Z)", lambda: self.ctx.historial.deshacer()),
                                  ("↷", "Rehacer (Ctrl+Y)", lambda: self.ctx.historial.rehacer()),
                                  ("🗑", "Papelera del tablero", self.abrir_basurero)):
            b = QToolButton()
            b.setText(simbolo)
            b.setToolTip(ayuda)
            b.setObjectName("herramienta")
            b.clicked.connect(f)
            h.addWidget(b)
            if simbolo == "↶":
                self.b_des = b
            elif simbolo == "↷":
                self.b_reh = b
        self.lbl_zoom = QLabel("100%")
        self.lbl_zoom.setToolTip("Ctrl + rueda para hacer zoom")
        h.addWidget(self.lbl_zoom)
        menu = QToolButton()
        menu.setIcon
        menu.setObjectName("herramienta")
        menu.clicked.connect(lambda: self.menu_global().exec(menu.mapToGlobal(menu.rect().topLeft())))
        h.addWidget(menu)
        self.vista.zoom_cambiado.connect(lambda z: self.lbl_zoom.setText(f"{int(z * 100)}%"))
        self._estado_historial()

    def _crear_panel(self):
        self.panel = QFrame(self)
        self.panel.setObjectName("panelFlotante")
        self.panel.setFixedWidth(250)
        lay = QVBoxLayout(self.panel)
        self.pila = QStackedWidget()
        lay.addWidget(self.pila)
        self.p_notas, self.p_pincel = PanelNotas(), PanelPincel()
        self.p_texto, self.p_figuras, self.p_lienzo = PanelTexto(), PanelFiguras(), PanelLienzo()
        # el panel de texto y el de lienzo comparten página con la de selección
        sel = QWidget()
        sl = QVBoxLayout(sel)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.addWidget(self.p_lienzo)
        self.paginas = {"seleccionar": sel, "nota": self.p_notas, "pincel": self.p_pincel,
                        "figura": self.p_figuras, "texto": self.p_texto}
        for w in self.paginas.values():
            self.pila.addWidget(w)
        self.p_notas.tipo_cambiado.connect(self._tipo_nota_cambiado)
        self.p_notas.color_cambiado.connect(self._color_nota)
        self.p_pincel.cambiado.connect(lambda d: self.opciones.update(pincel=d))
        self.p_figuras.cambiado.connect(lambda d: self.opciones.update(figura=d))
        self.p_texto.cambiado.connect(self._formato_texto)
        self.p_lienzo.estilo_cambiado.connect(lambda v: self._config_lienzo(lienzo=v))
        self.p_lienzo.fondo_cambiado.connect(lambda v: self._config_lienzo(fondo=v))
        self.p_lienzo.nuevo_widget.connect(lambda: self.window().nuevo_widget_notas())

    def _atajos(self):
        def a(secuencia, f):
            QShortcut(QKeySequence(secuencia), self, activated=f)
        a("Ctrl+Z", lambda: self.ctx.historial.deshacer())
        a("Ctrl+Y", lambda: self.ctx.historial.rehacer())
        a("Ctrl+Shift+Z", lambda: self.ctx.historial.rehacer())
        a("Ctrl+D", self._duplicar)
        a("Delete", self._eliminar_seleccion)
        a("Ctrl+0", lambda: self.vista.poner_zoom(1.0))
        a("Ctrl+A", lambda: [i.setSelected(True) for i in self.escena.items() if isinstance(i, ItemBase)])
        a("Escape", lambda: (self.escena.clearSelection(), self.cambiar_herramienta("seleccionar")))
        for tecla, hid in (("V", "seleccionar"), ("N", "nota"), ("B", "pincel"), ("E", "borrador"),
                           ("S", "figura"), ("I", "imagen"), ("T", "texto")):
            a(tecla, lambda h=hid: self._atajo_herramienta(h))

    def _atajo_herramienta(self, hid: str):
        # no cambiar de herramienta si la persona está escribiendo en un campo
        if isinstance(QApplication.focusWidget(), (QLineEdit, QAbstractSpinBox, QComboBox, QPlainTextEdit)):
            return
        self.cambiar_herramienta(hid)

    # ---------- comportamiento
    def abrir_tablero(self, tablero_id: str):
        self.ctx.historial.limpiar()
        self.escena.cargar(tablero_id)
        t = self.ctx.tableros.obtener(tablero_id)
        self.window().setWindowTitle(f"Tablero Digital — {t.nombre}")
        self.vista.poner_zoom(1.0)
        self.vista.centerOn(0, 0)
        self.cambiar_herramienta("seleccionar")

    def cambiar_herramienta(self, hid: str):
        if hid == "imagen":
            self.insertar_imagen()
            hid = "seleccionar"
        if hid == "nota":
            hid_escena = self._tipo_nota
        else:
            hid_escena = hid
        self.escena.herramienta = hid_escena
        if hid in self.botones and self.botones[hid].isCheckable():
            self.botones[hid].setChecked(True)
        self.vista.setDragMode(self.vista.DragMode.RubberBandDrag if hid == "seleccionar"
                               else self.vista.DragMode.NoDrag)
        self.vista.viewport().setCursor(Qt.CursorShape.ArrowCursor if hid == "seleccionar"
                                        else Qt.CursorShape.CrossCursor)
        pagina = self.paginas.get(hid)
        self.panel.setVisible(pagina is not None)
        if pagina is not None:
            self.pila.setCurrentWidget(pagina)
        self._herramienta_ui = hid
        self._colocar()

    def _tipo_nota_cambiado(self, tipo: str):
        self._tipo_nota = tipo
        if self._herramienta_ui == "nota":
            self.escena.herramienta = tipo

    def _color_nota(self, c: str):
        self.opciones["color_nota"] = c
        for it in self.escena.items_tablero():
            if it.e.tipo in ("nota", "lista", "enlace"):
                self.ctx.servicio.editar_propiedades(it.e.id, color=c)

    def _formato_texto(self, d: dict):
        self.opciones["texto"].update(d)
        for it in self.escena.items_tablero():
            if it.e.tipo in FORMATO_TEXTO:
                self.ctx.servicio.editar_propiedades(it.e.id, **d)

    def _config_lienzo(self, **kw):
        cfg = self.escena.config
        for k, v in kw.items():
            if v == "":
                cfg.pop(k, None)
            else:
                cfg[k] = v
        if self.escena.tablero_id:
            self.ctx.tableros.guardar_config(self.escena.tablero_id, cfg)
        self.escena.update()

    def insertar_imagen(self):
        if not self.escena.tablero_id:
            return
        ruta, _ = QFileDialog.getOpenFileName(self, "Insertar imagen", str(Path.home()),
                                              "Imágenes (*.png *.jpg *.jpeg *.gif *.bmp *.webp)")
        if not ruta:
            return
        pm = QPixmap(ruta)
        if pm.isNull():
            QMessageBox.warning(self, "Imagen", "No se pudo abrir esa imagen.")
            return
        rel = importar_imagen(self.ctx.con, self.ctx.carpeta_datos, self.escena.tablero_id, ruta)
        ancho = min(320.0, float(pm.width()))
        alto = ancho * pm.height() / max(1, pm.width())
        centro = self.vista.mapToScene(self.vista.viewport().rect().center())
        e = self.escena.crear_en("imagen", QPointF(centro.x() - ancho / 2, centro.y() - alto / 2), recurso=rel)
        if e:
            self.ctx.servicio.modificar(e.id, "Tamaño", ancho=ancho, alto=alto)

    def _duplicar(self):
        for it in self.escena.items_tablero():
            self.ctx.servicio.duplicar(it.e.id)

    def _eliminar_seleccion(self):
        self.ctx.servicio.eliminar_varios([i.e.id for i in self.escena.items_tablero()])

    def abrir_basurero(self):
        if self.escena.tablero_id:
            DialogoBasurero(self.ctx, self.escena.tablero_id, self).exec()

    def _estado_historial(self):
        self.b_des.setEnabled(self.ctx.historial.puede_deshacer())
        self.b_reh.setEnabled(self.ctx.historial.puede_rehacer())
        if self.escena.tablero_id:
            self.ctx.tableros.tocar(self.escena.tablero_id)

    # ---------- posición de los elementos flotantes
    def _colocar(self):
        self.barra.adjustSize()
        self.barra.move((self.width() - self.barra.width()) // 2, self.height() - self.barra.height() - 16)
        self.panel.adjustSize()
        self.panel.move(self.width() - self.panel.width() - 16, 16)
        self.barra.raise_()
        self.panel.raise_()

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self._colocar()
