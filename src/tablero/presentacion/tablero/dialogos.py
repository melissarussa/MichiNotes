"""Diálogos sencillos para editar el contenido de los elementos."""
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit, QPlainTextEdit,
                               QVBoxLayout)


class _Base(QDialog):
    def __init__(self, titulo: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.setMinimumWidth(380)
        self.lay = QVBoxLayout(self)
        self.botones = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.botones.accepted.connect(self.accept)
        self.botones.rejected.connect(self.reject)

    def _fin(self):
        self.lay.addWidget(self.botones)


def editar_texto(titulo: str, texto: str, parent=None) -> str | None:
    d = _Base(titulo, parent)
    caja = QPlainTextEdit(texto)
    d.lay.addWidget(caja)
    d._fin()
    caja.setFocus()
    return caja.toPlainText() if d.exec() else None


def editar_lista(titulo: str, items: list[dict], parent=None):
    d = _Base("Editar lista", parent)
    form = QFormLayout()
    campo_titulo = QLineEdit(titulo)
    form.addRow("Título", campo_titulo)
    d.lay.addLayout(form)
    d.lay.addWidget(QLabel("Una tarea por línea. Empieza con [x] para marcarla como hecha."))
    caja = QPlainTextEdit("\n".join(("[x] " if i.get("hecho") else "") + i.get("texto", "") for i in items))
    d.lay.addWidget(caja)
    d._fin()
    if not d.exec():
        return None
    nuevos = []
    for linea in caja.toPlainText().splitlines():
        linea = linea.strip()
        if not linea:
            continue
        hecho = linea.lower().startswith("[x]")
        if hecho:
            linea = linea[3:].strip()
        nuevos.append({"texto": linea, "hecho": hecho})
    return campo_titulo.text(), nuevos


def editar_enlace(titulo: str, url: str, parent=None):
    d = _Base("Editar enlace", parent)
    form = QFormLayout()
    c_titulo, c_url = QLineEdit(titulo), QLineEdit(url)
    c_url.setPlaceholderText("https://...")
    form.addRow("Título", c_titulo)
    form.addRow("Dirección", c_url)
    d.lay.addLayout(form)
    d._fin()
    if not d.exec():
        return None
    u = c_url.text().strip()
    if u and "://" not in u:
        u = "https://" + u
    return c_titulo.text().strip() or u, u
