"""Calendario semanal (LUN–DOM, 8 AM–6 PM) con mini calendario y lista de calendarios, como el mockup."""
from datetime import date, datetime, timedelta

from PySide6.QtCore import QDate, QSize, Signal
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (QCalendarWidget, QCheckBox, QHBoxLayout, QHeaderView, QInputDialog, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QAbstractItemView)

from ...dominio.calendario import Evento
from .. import iconos
from .dialogo_evento import DialogoEvento

def _boton(texto: str, icono: str) -> QPushButton:
    b = QPushButton((" " + texto) if texto else "")
    b.setIcon(iconos.icono(icono, normal=iconos.COLOR_ACTIVO))
    b.setIconSize(QSize(20, 20))
    return b


DIAS = ["LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB", "DOM"]
H0, H1 = 0, 23      # horas visibles (0:00 a 23:59: todo el día)
H_INICIAL = 7       # al abrir, la vista se desplaza hasta esta hora


def lunes_de(d: date) -> date:
    return d - timedelta(days=d.weekday())


class VistaSemanal(QWidget):
    abrir_tablero = Signal(str)

    def __init__(self, ctx, parent=None):
        super().__init__(parent)
        self.ctx = ctx
        self.lunes = lunes_de(date.today())
        self._celdas: dict[tuple[int, int], list[Evento]] = {}
        raiz = QHBoxLayout(self)

        izq = QVBoxLayout()
        raiz.addLayout(izq, 0)
        
        # --- CAMBIOS EN EL MINI CALENDARIO ---
        self.mini = QCalendarWidget()
        self.mini.setMaximumWidth(260)
        self.mini.setGridVisible(False)
        # Ocultar la columna de números de semana (44, 45, 46...)
        self.mini.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        # el estilo (colores planos) viene de estilos/claro.qss
        # -------------------------------------
        
        self.mini.selectionChanged.connect(self._mini_cambio)
        izq.addWidget(self.mini)
        izq.addWidget(QLabel("<b>Calendarios</b>"))
        self.caja_cals = QVBoxLayout()
        izq.addLayout(self.caja_cals)
        nuevo = _boton("Nuevo calendario", "plus-bold.svg")
        nuevo.clicked.connect(self._nuevo_calendario)
        izq.addWidget(nuevo)
        izq.addStretch()

        der = QVBoxLayout()
        raiz.addLayout(der, 1)
        nav = QHBoxLayout()
        self.titulo = QLabel()
        self.titulo.setObjectName("tituloPanel")
        ant, hoy, sig = _boton("", "caret-left-bold.svg"), QPushButton("Hoy"), _boton("", "caret-right-bold.svg")
        ant.clicked.connect(lambda: self.mover(-7))
        sig.clicked.connect(lambda: self.mover(7))
        hoy.clicked.connect(self.ir_hoy)
        nav.addWidget(self.titulo, 1)
        for b in (ant, hoy, sig):
            nav.addWidget(b)
        nuevo_ev = _boton("Evento", "plus-bold.svg")
        nuevo_ev.clicked.connect(self._evento_nuevo_ahora)
        nav.addWidget(nuevo_ev)
        der.addLayout(nav)

        # --- TABLA PRINCIPAL ---
        self.tabla = QTableWidget(H1 - H0 + 1, 7)
        self.tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.tabla.setVerticalHeaderLabels([f"{h % 12 or 12} {'AM' if h < 12 else 'PM'}"
                                            for h in range(H0, H1 + 1)])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # 24 filas no caben "estiradas": altura fija por hora y barra de desplazamiento vertical
        self.tabla.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.tabla.verticalHeader().setDefaultSectionSize(64)
        self.tabla.cellDoubleClicked.connect(self._doble_clic)
        
        # -----------------------

        der.addWidget(self.tabla, 1)
        self.refrescar()
        self._desplazado = False

    def showEvent(self, ev):
        super().showEvent(ev)
        if not self._desplazado:       # la primera vez que se muestra, ir a las 7 AM (la tabla ya tiene tamaño)
            self._desplazado = True
            self.tabla.verticalScrollBar().setValue(H_INICIAL * self.tabla.verticalHeader().defaultSectionSize())

    # ---- navegación
    def mover(self, dias: int):
        self.lunes += timedelta(days=dias)
        self.refrescar()

    def ir_hoy(self):
        self.lunes = lunes_de(date.today())
        self.mini.setSelectedDate(QDate.currentDate())
        self.refrescar()

    def _mini_cambio(self):
        self.lunes = lunes_de(self.mini.selectedDate().toPython())
        self.refrescar()

    # ---- datos
    def refrescar(self):
        fin = self.lunes + timedelta(days=7)
        self.titulo.setText(f"{self.lunes:%d/%m/%Y} – {(fin - timedelta(days=1)):%d/%m/%Y}")
        hoy = date.today()
        self.tabla.setHorizontalHeaderLabels(
            [f"{DIAS[i]} {(self.lunes + timedelta(days=i)).day}" + (" •" if self.lunes + timedelta(days=i) == hoy else "")
             for i in range(7)])
        self.tabla.clearContents()
        self._celdas.clear()
        eventos = self.ctx.calendario.listar_eventos(self.lunes.isoformat(), fin.isoformat())
        for ev in eventos:
            ini = datetime.fromisoformat(ev.inicio)
            col, fila = (ini.date() - self.lunes).days, ini.hour - H0
            if 0 <= col < 7 and 0 <= fila <= H1 - H0:
                self._celdas.setdefault((fila, col), []).append(ev)
        for (fila, col), evs in self._celdas.items():
            it = QTableWidgetItem("\n".join(f"{datetime.fromisoformat(e.inicio):%H:%M} {e.titulo}" for e in evs))
            c = QColor(evs[0].color)
            c.setAlpha(150)
            it.setBackground(QBrush(c))
            it.setForeground(QBrush(QColor("#111111")))
            self.tabla.setItem(fila, col, it)
        self._cargar_calendarios()

    def _cargar_calendarios(self):
        while self.caja_cals.count():
            w = self.caja_cals.takeAt(0).widget()
            if w:
                w.deleteLater()
        for c in self.ctx.calendario.listar_calendarios():
            cb = QCheckBox(c["nombre"])
            cb.setChecked(bool(c["visible"]))
            cb.toggled.connect(lambda ok, cid=c["id"]: (self.ctx.calendario.fijar_visible(cid, ok), self.refrescar()))
            self.caja_cals.addWidget(cb)

    def _nuevo_calendario(self):
        nombre, ok = QInputDialog.getText(self, "Nuevo calendario", "Nombre:")
        if ok and nombre.strip():
            self.ctx.calendario.crear_calendario(nombre.strip())
            self._cargar_calendarios()

    # ---- eventos
    def _doble_clic(self, fila: int, col: int):
        evs = self._celdas.get((fila, col))
        if evs:
            ev = evs[0]
            if len(evs) > 1:
                nombres = [f"{datetime.fromisoformat(e.inicio):%H:%M} {e.titulo}" for e in evs]
                elegido, ok = QInputDialog.getItem(self, "Eventos", "Elige uno:", nombres, 0, False)
                if not ok:
                    return
                ev = evs[nombres.index(elegido)]
            self._editar(ev, False)
        else:
            dia = self.lunes + timedelta(days=col)
            self._editar(Evento("", "", datetime(dia.year, dia.month, dia.day, H0 + fila).isoformat(timespec="minutes")), True)

    def _evento_nuevo_ahora(self):
        d = datetime.now().replace(minute=0, second=0, microsecond=0)
        self._editar(Evento("", "", d.isoformat(timespec="minutes")), True)

    def _editar(self, ev: Evento, nuevo: bool):
        dlg = DialogoEvento(self.ctx, ev, nuevo, self)
        if not dlg.exec():
            return
        if dlg.resultado == "guardar":
            (self.ctx.calendario.crear_evento if nuevo else self.ctx.calendario.actualizar_evento)(ev)
        elif dlg.resultado == "eliminar":
            self.ctx.calendario.eliminar_evento(ev.id)
        self.refrescar()