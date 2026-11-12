from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit, QVBoxLayout)

from ..aplicacion.servicio_acceso import ErrorAcceso


class DialogoLogin(QDialog):
    def __init__(self, acceso, parent=None):
        super().__init__(parent)
        self.acceso = acceso
        self.usuario = None
        self.registro = not acceso.hay_usuarios()
        self.setWindowTitle("Crear cuenta" if self.registro else "Iniciar sesión")
        self.setMinimumWidth(340)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("<h2>Tablero Digital</h2>" + (
            "Primera vez: crea tu usuario (los datos quedan solo en este equipo)." if self.registro
            else "Inicia sesión para continuar.")))
        form = QFormLayout()
        self.nombre, self.clave = QLineEdit(), QLineEdit()
        self.clave.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Usuario", self.nombre)
        form.addRow("Clave", self.clave)
        lay.addLayout(form)
        self.error = QLabel("")
        self.error.setStyleSheet("color:#D32F2F;")
        lay.addWidget(self.error)
        b = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        b.accepted.connect(self._ok)
        b.rejected.connect(self.reject)
        lay.addWidget(b)

    def _ok(self):
        try:
            f = self.acceso.registrar if self.registro else self.acceso.entrar
            self.usuario = f(self.nombre.text(), self.clave.text())
            self.accept()
        except ErrorAcceso as e:
            self.error.setText(str(e))
