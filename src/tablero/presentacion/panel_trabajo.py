"""Panel de trabajo: lista de tableros con búsqueda, crear, renombrar, eliminar y restaurar."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QHBoxLayout, QInputDialog, QLineEdit, QListWidget, QListWidgetItem, QMessageBox,
                               QPushButton, QVBoxLayout, QWidget, QLabel)


class PanelTrabajo(QWidget):
    abrir = Signal(str)

    def __init__(self, ctx, parent=None):
        super().__init__(parent)
        self.ctx = ctx
        lay = QVBoxLayout(self)
        t = QLabel("Mis tableros")
        t.setObjectName("tituloPanel")
        lay.addWidget(t)
        fila = QHBoxLayout()
        self.buscar = QLineEdit()
        self.buscar.setPlaceholderText("Buscar tablero…")
        self.buscar.textChanged.connect(self.cargar)
        fila.addWidget(self.buscar, 1)
        for etq, f in (("＋ Nuevo tablero", self.nuevo), ("Renombrar", self.renombrar), ("Eliminar", self.eliminar),
                       ("Eliminados…", self.ver_eliminados)):
            b = QPushButton(etq)
            b.clicked.connect(f)
            fila.addWidget(b)
        lay.addLayout(fila)
        self.lista = QListWidget()
        self.lista.itemDoubleClicked.connect(lambda it: self.abrir.emit(it.data(256)))
        lay.addWidget(self.lista)
        lay.addWidget(QLabel("Doble clic sobre un tablero para abrirlo."))
        self.cargar()

    def cargar(self, *_):
        self.lista.clear()
        for t in self.ctx.tableros.listar(self.buscar.text()):
            it = QListWidgetItem(f"📋  {t.nombre}    ·  {t.actualizado_en[:10]}")
            it.setData(256, t.id)
            self.lista.addItem(it)

    def _actual(self):
        it = self.lista.currentItem()
        return it.data(256) if it else None

    def nuevo(self):
        nombre, ok = QInputDialog.getText(self, "Nuevo tablero", "Nombre del tablero:")
        if ok and nombre.strip():
            t = self.ctx.tableros.crear(nombre.strip())
            self.cargar()
            self.abrir.emit(t.id)

    def renombrar(self):
        tid = self._actual()
        if not tid:
            return
        t = self.ctx.tableros.obtener(tid)
        nombre, ok = QInputDialog.getText(self, "Renombrar", "Nuevo nombre:", text=t.nombre)
        if ok and nombre.strip():
            self.ctx.tableros.renombrar(tid, nombre.strip())
            self.cargar()

    def eliminar(self):
        tid = self._actual()
        if tid and QMessageBox.question(self, "Eliminar", "¿Mandar este tablero a eliminados?") == QMessageBox.StandardButton.Yes:
            self.ctx.tableros.eliminar(tid)
            self.cargar()

    def ver_eliminados(self):
        elim = self.ctx.tableros.listar_eliminados()
        if not elim:
            QMessageBox.information(self, "Eliminados", "No hay tableros eliminados.")
            return
        nombres = [t.nombre for t in elim]
        n, ok = QInputDialog.getItem(self, "Restaurar tablero", "Elige el que quieres restaurar:", nombres, 0, False)
        if ok:
            self.ctx.tableros.restaurar(elim[nombres.index(n)].id)
            self.cargar()
