"""Papelera: los elementos eliminados se pueden restaurar o borrar para siempre."""
from PySide6.QtWidgets import (QDialog, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout)


def resumen(e) -> str:
    p = e.propiedades
    texto = p.get("texto") or p.get("titulo") or p.get("url") or p.get("forma") or ""
    return f"{e.tipo.capitalize()}: {texto[:40]}".strip()


class DialogoBasurero(QDialog):
    def __init__(self, ctx, tablero_id: str, parent=None):
        super().__init__(parent)
        self.ctx, self.tablero_id = ctx, tablero_id
        self.setWindowTitle("Papelera")
        self.setMinimumSize(420, 360)
        lay = QVBoxLayout(self)
        self.lista = QListWidget()
        lay.addWidget(self.lista)
        fila = QHBoxLayout()
        for etq, f in (("Restaurar", self.restaurar), ("Eliminar para siempre", self.borrar), ("Vaciar", self.vaciar),
                       ("Cerrar", self.accept)):
            b = QPushButton(etq)
            b.clicked.connect(f)
            fila.addWidget(b)
        lay.addLayout(fila)
        self.cargar()

    def cargar(self):
        self.lista.clear()
        for e in self.ctx.repo_elementos.listar_eliminados(self.tablero_id):
            it = QListWidgetItem(resumen(e))
            it.setData(256, e.id)
            self.lista.addItem(it)

    def restaurar(self):
        for it in self.lista.selectedItems():
            self.ctx.servicio.restaurar(it.data(256))
        self.cargar()

    def borrar(self):
        for it in self.lista.selectedItems():
            self.ctx.servicio.borrar_definitivo(it.data(256))
        self.cargar()

    def vaciar(self):
        for i in range(self.lista.count()):
            self.ctx.servicio.borrar_definitivo(self.lista.item(i).data(256))
        self.cargar()
