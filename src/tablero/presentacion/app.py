"""Ventana principal y arranque de la aplicación."""
import sys
from pathlib import Path

from PySide6.QtCore import QTimer, QUrl, QSize
from PySide6.QtGui import QAction, QDesktopServices,QIcon
from PySide6.QtWidgets import (QApplication, QFileDialog, QMainWindow, QMenu, QMessageBox, QStackedWidget, QStyle,
                               QSystemTrayIcon, QToolBar)
from .. import config
from ..config import ruta_recurso
from ..aplicacion.contexto import Contexto
from ..aplicacion.servicio_acceso import ServicioAcceso
from ..dominio.utiles import nuevo_id
from ..infraestructura import respaldo
from ..infraestructura.base_datos.conexion import abrir_conexion
from ..infraestructura.base_datos.migrador import migrar
from ..infraestructura.repositorios.sqlite_usuarios import RepoUsuarios
from .calendario.vista_semanal import VistaSemanal
from .login import DialogoLogin
from .panel_trabajo import PanelTrabajo
from .ventana_tablero import VentanaTablero
from .widgets_escritorio import WidgetNota

ESTILOS = Path(__file__).parent / "estilos"
ATAJOS = """<b>Atajos de teclado</b><br><br>
V seleccionar · N notas · B pincel · E borrador · S figuras · I imagen · T texto<br>
Ctrl+Z deshacer · Ctrl+Y rehacer · Ctrl+D duplicar · Supr eliminar · Ctrl+A seleccionar todo<br>
Ctrl+rueda zoom · Ctrl+0 zoom 100% · botón del medio: mover el lienzo<br>
Doble clic en vacío: nueva nota · clic derecho: menú del elemento<br>
Esc: volver a seleccionar"""


class VentanaPrincipal(QMainWindow):
    def __init__(self, ctx: Contexto):
        super().__init__()
        self.ctx = ctx
        self.setWindowTitle("Tablero Digital")
        self.resize(1200, 760)
        self.widgets: list[WidgetNota] = []

        self.pila = QStackedWidget()
        self.setCentralWidget(self.pila)
        self.trabajo = PanelTrabajo(ctx)
        self.tablero = VentanaTablero(ctx, self.crear_menu)
        self.calendario = VistaSemanal(ctx)
        for w in (self.trabajo, self.tablero, self.calendario):
            self.pila.addWidget(w)
        self.trabajo.abrir.connect(self.abrir_tablero)

        barra = QToolBar("Navegación")
        barra.setMovable(False)
        barra.setIconSize(QSize(24, 24)) 
        self.addToolBar(barra)

# 1. Agregamos el nombre del archivo a cada tupla
        acciones = (
            ("chalkboard-simple-bold.svg", "Tableros", self.ver_tableros), 
            ("palette-bold.svg", "Tablero actual", lambda: self.pila.setCurrentWidget(self.tablero)),
            ("calendar-dots-bold.svg", "Calendario", self.ver_calendario)
        )

        # 2. Bucle para los 3 botones principales
        for archivo_icono, texto, funcion in acciones:
            icono = QIcon(ruta_recurso("iconos", archivo_icono))
            accion = QAction(icono, texto, self)
            accion.triggered.connect(funcion)
            barra.addAction(accion)

        # 3. El Separador y el Menú van AFUERA del bucle (¡esto arregla el desastre!)
        barra.addSeparator()
        
        icono_menu = QIcon(ruta_recurso("iconos", "dots-three-outline-bold.svg"))
        accion_menu = QAction(icono_menu, "Menú", self)
        accion_menu.triggered.connect(lambda: self.crear_menu().exec(self.cursor().pos()))
        barra.addAction(accion_menu)

        # bandeja del sistema + avisos de calendario
    
        self.bandeja = None
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.bandeja = QSystemTrayIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon), self)
            self.bandeja.setToolTip("Tablero Digital")
            self.bandeja.show()
        self.timer = QTimer(self, interval=30_000)
        self.timer.timeout.connect(self.revisar_avisos)
        self.timer.start()
        QTimer.singleShot(1500, self.revisar_avisos)

        QApplication.instance().setStyleSheet((ESTILOS / "claro.qss").read_text(encoding="utf-8"))
        for d in ctx.widgets_notas():
            self._mostrar_widget(d)
        self.ver_tableros()

    # ---- navegación
    def ver_tableros(self):
        self.trabajo.cargar()
        self.pila.setCurrentWidget(self.trabajo)

    def ver_calendario(self):
        self.calendario.refrescar()
        self.pila.setCurrentWidget(self.calendario)

    def abrir_tablero(self, tablero_id: str):
        self.tablero.abrir_tablero(tablero_id)
        self.pila.setCurrentWidget(self.tablero)

    def crear_menu(self) -> QMenu:
        m = QMenu(self)
        accion_tableros = QAction(QIcon(ruta_recurso("iconos", "chalkboard-simple-bold.svg")), "Panel de trabajo", self)
        accion_tableros.triggered.connect(self.ver_tableros)
        m.addAction(accion_tableros)
        accion_calendario = QAction(QIcon(ruta_recurso("iconos","calendar-dots-bold.svg")),"Calendario", self)
        accion_calendario.triggered.connect(self.ver_calendario)
        m.addAction(accion_calendario)
        accion_widget = QAction(QIcon(ruta_recurso("iconos", "note-pencil-bold.svg")),"Nuevo Widget", self)
        accion_widget.triggered.connect(self.nuevo_widget_notas)
        m.addAction(accion_widget)
        accion_guardar = QAction(QIcon(ruta_recurso("iconos","floppy-disk-bold.svg")),"Guardar", self)
        accion_guardar.triggered.connect(self.hacer_respaldo)
        m.addAction(accion_guardar)
        accion_restaurar = QAction(QIcon(ruta_recurso("iconos","recycle-bold.svg")),"Restaurar guardado", self)
        accion_restaurar.triggered.connect(self.restaurar_respaldo)
        m.addAction(accion_restaurar)
        m.addSeparator()
        accion_atajos = QAction(QIcon(ruta_recurso("iconos","keyboard-bold.svg")),"Atajos de teclado", self)
        accion_atajos.triggered.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.ctx.carpeta_datos))))
        m.addAction(accion_atajos)
        accion_salir = QAction(QIcon(ruta_recurso("iconos","power-bold.svg")),"Salir", self)
        accion_salir.triggered.connect(self.close)
        m.addAction(accion_salir)

        return m
    
    # ---- respaldo
    def hacer_respaldo(self):
        destino, _ = QFileDialog.getSaveFileName(self, "Guardar respaldo",
                                                 str(self.ctx.carpeta_datos / "respaldo.db"), "Base de datos (*.db)")
        if destino:
            ruta = respaldo.crear_respaldo(self.ctx.con, self.ctx.carpeta_datos, destino)
            QMessageBox.information(self, "Respaldo", f"Respaldo creado:\n{ruta}")

    def restaurar_respaldo(self):
        origen, _ = QFileDialog.getOpenFileName(self, "Elegir respaldo", str(self.ctx.carpeta_datos), "Base de datos (*.db)")
        if origen and QMessageBox.question(
                self, "Restaurar", "Esto reemplaza TODO el contenido actual por el del respaldo. ¿Continuar?"
        ) == QMessageBox.StandardButton.Yes:
            respaldo.restaurar_respaldo(self.ctx.con, self.ctx.carpeta_datos, origen)
            self.ctx.historial.limpiar()
            self.ver_tableros()

    # ---- widgets de escritorio
    def nuevo_widget_notas(self):
        d = {"id": nuevo_id(), "texto": "", "x": 100 + 30 * len(self.widgets), "y": 100 + 30 * len(self.widgets)}
        lista = self.ctx.widgets_notas()
        lista.append(d)
        self.ctx.guardar_widgets_notas(lista)
        self._mostrar_widget(d)

    def _mostrar_widget(self, d: dict):
        def guardar():
            lista = [x for x in self.ctx.widgets_notas() if x["id"] != d["id"]] + [d]
            self.ctx.guardar_widgets_notas(lista)

        def cerrar(w):
            self.ctx.guardar_widgets_notas([x for x in self.ctx.widgets_notas() if x["id"] != d["id"]])
            self.widgets.remove(w)

        w = WidgetNota(d, guardar, cerrar)
        self.widgets.append(w)
        w.show()

    # ---- avisos
    def revisar_avisos(self):
        from datetime import datetime
        for ev in self.ctx.calendario.eventos_por_avisar(datetime.now().isoformat(timespec="minutes")):
            self.ctx.calendario.marcar_notificado(ev.id)
            msg = f"{ev.titulo} — {ev.inicio[11:16]}"
            if self.bandeja:
                self.bandeja.showMessage("Recordatorio", msg)
            else:
                QMessageBox.information(self, "Recordatorio", msg)

    def closeEvent(self, ev):
        for w in list(self.widgets):
            w.close()
        self.ctx.con.close()
        super().closeEvent(ev)


def ejecutar() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(config.NOMBRE_APP)
    rutaLogo = ruta_recurso("iconos", "logo.png")
    app.setWindowIcon(QIcon(rutaLogo))
    carpeta = config.carpeta_datos()
    con = abrir_conexion(config.ruta_db(carpeta))
    migrar(con)
    acceso = ServicioAcceso(RepoUsuarios(con))
    dlg = DialogoLogin(acceso)
    if not dlg.exec():
        return 0
    ctx = Contexto(con, carpeta, dlg.usuario)
    ventana = VentanaPrincipal(ctx)
    ventana.show()

    return app.exec()
