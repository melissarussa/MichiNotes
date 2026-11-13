"""Carga la fuente Dongle y aplica la hoja de estilos (claro.qss) a toda la aplicación."""
from pathlib import Path

from PySide6.QtGui import QFontDatabase

from ..config import ruta_recurso

ESTILOS = Path(__file__).parent / "estilos"
FUENTE = "Dongle"
# Dongle es una fuente muy pequeña (sus letras miden ~55% de una fuente normal),
# por eso todos los tamaños del .qss son más grandes de lo habitual.
ESCALA_FUENTE = 1.8


def cargar_fuentes() -> str | None:
    familia = None
    for archivo in ("Dongle-Regular.ttf", "Dongle-Bold.ttf", "Dongle-Light.ttf"):
        ident = QFontDatabase.addApplicationFont(ruta_recurso("fuentes", archivo))
        if ident != -1 and familia is None:
            familia = QFontDatabase.applicationFontFamilies(ident)[0]
    return familia


def aplicar_estilo(app) -> None:
    familia = cargar_fuentes()
    qss = (ESTILOS / "claro.qss").read_text(encoding="utf-8")
    qss = qss.replace("@RECURSOS@", Path(ruta_recurso("iconos", "")).as_posix())
    qss = qss.replace("@FUENTE@", f'"{familia}"' if familia else "sans-serif")
    app.setStyleSheet(qss)
