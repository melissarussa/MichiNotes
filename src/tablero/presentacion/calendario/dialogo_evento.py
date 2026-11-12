from datetime import datetime

from PySide6.QtCore import QDate, QTime
from PySide6.QtWidgets import (QComboBox, QDateEdit, QDialog, QDialogButtonBox, QFormLayout, QLineEdit,
                               QPlainTextEdit, QPushButton, QTimeEdit, QVBoxLayout)

from ...dominio.calendario import Evento
from ..panel_opciones import BotonColor

AVISOS = [("Sin aviso", None), ("5 minutos antes", 5), ("15 minutos antes", 15), ("30 minutos antes", 30),
          ("1 hora antes", 60), ("1 día antes", 1440)]


class DialogoEvento(QDialog):
    """Crea o edita un evento. resultado: 'guardar' | 'eliminar' | None"""

    def __init__(self, ctx, evento: Evento, es_nuevo: bool, parent=None):
        super().__init__(parent)
        self.ev, self.resultado = evento, None
        self.setWindowTitle("Nuevo evento" if es_nuevo else "Editar evento")
        self.setMinimumWidth(380)
        lay = QVBoxLayout(self)
        form = QFormLayout()
        lay.addLayout(form)
        ini = datetime.fromisoformat(evento.inicio)
        fin = datetime.fromisoformat(evento.fin) if evento.fin else ini.replace(hour=min(ini.hour + 1, 23))
        self.titulo = QLineEdit(evento.titulo)
        self.desc = QPlainTextEdit(evento.descripcion)
        self.desc.setFixedHeight(70)
        self.fecha = QDateEdit(QDate(ini.year, ini.month, ini.day))
        self.fecha.setCalendarPopup(True)
        self.hi = QTimeEdit(QTime(ini.hour, ini.minute))
        self.hf = QTimeEdit(QTime(fin.hour, fin.minute))
        self.cal = QComboBox()
        for c in ctx.calendario.listar_calendarios():
            self.cal.addItem(c["nombre"], c["id"])
        if evento.calendario_id:
            i = self.cal.findData(evento.calendario_id)
            self.cal.setCurrentIndex(max(i, 0))
        self.aviso = QComboBox()
        for etq, v in AVISOS:
            self.aviso.addItem(etq, v)
        self.aviso.setCurrentIndex(max(self.aviso.findData(evento.aviso_minutos), 0))
        self.tablero = QComboBox()
        self.tablero.addItem("(ninguno)", None)
        for t in ctx.tableros.listar():
            self.tablero.addItem(t.nombre, t.id)
        self.tablero.setCurrentIndex(max(self.tablero.findData(evento.tablero_id), 0))
        self.color = BotonColor(evento.color)
        for etq, w in (("Título", self.titulo), ("Descripción", self.desc), ("Fecha", self.fecha),
                       ("Inicio", self.hi), ("Fin", self.hf), ("Calendario", self.cal), ("Aviso", self.aviso),
                       ("Tablero asociado", self.tablero), ("Color", self.color)):
            form.addRow(etq, w)
        botones = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        botones.accepted.connect(self._guardar)
        botones.rejected.connect(self.reject)
        if not es_nuevo:
            b = QPushButton("Eliminar")
            b.clicked.connect(self._eliminar)
            botones.addButton(b, QDialogButtonBox.ButtonRole.DestructiveRole)
        lay.addWidget(botones)

    def _guardar(self):
        if not self.titulo.text().strip():
            self.titulo.setFocus()
            return
        d = self.fecha.date().toPython()
        ini = datetime(d.year, d.month, d.day, self.hi.time().hour(), self.hi.time().minute())
        fin = datetime(d.year, d.month, d.day, self.hf.time().hour(), self.hf.time().minute())
        if fin <= ini:
            fin = ini.replace(hour=min(ini.hour + 1, 23), minute=ini.minute)
        e = self.ev
        e.titulo, e.descripcion = self.titulo.text().strip(), self.desc.toPlainText()
        e.inicio, e.fin = ini.isoformat(timespec="minutes"), fin.isoformat(timespec="minutes")
        e.calendario_id, e.aviso_minutos = self.cal.currentData(), self.aviso.currentData()
        e.tablero_id, e.color = self.tablero.currentData(), self.color.color
        e.notificado = False
        self.resultado = "guardar"
        self.accept()

    def _eliminar(self):
        self.resultado = "eliminar"
        self.accept()
