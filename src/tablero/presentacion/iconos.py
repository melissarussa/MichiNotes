"""Iconos SVG recoloreables. Todos los de recursos/iconos son vectores de un solo color.

Los archivos vienen en COLOR_ICONO, pero aquí se vuelven a pintar al vuelo para tener también
la versión clara (botón marcado, que tiene fondo oscuro) y la apagada (botón desactivado).
Qt elige sola la versión: un QToolButton marcado usa State.On, uno desactivado usa Mode.Disabled.
"""
import re
from functools import lru_cache
from pathlib import Path

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QImage, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from ..config import ruta_recurso

COLOR_ICONO = "#887C6E"     # icono normal
COLOR_ACTIVO = "#F3EFE8"    # icono sobre fondo oscuro (botón marcado / insignia)
COLOR_APAGADO = "#B5AD9F"   # icono desactivado
_TAM = 64                   # se dibuja grande y Qt lo reduce suave


@lru_cache(maxsize=None)
def _svg(nombre: str) -> str:
    return Path(ruta_recurso("iconos", nombre)).read_text(encoding="utf-8")


@lru_cache(maxsize=None)
def pixmap(nombre: str, color: str = COLOR_ICONO, tam: int = _TAM) -> QPixmap:
    """El icono como imagen, pintado del color pedido."""
    svg = re.sub(r'(fill|stroke)="(?!none")[^"]*"', rf'\1="{color}"', _svg(nombre))
    img = QImage(tam, tam, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    pintor = QPainter(img)
    QSvgRenderer(QByteArray(svg.encode("utf-8"))).render(pintor)
    pintor.end()
    return QPixmap.fromImage(img)


@lru_cache(maxsize=None)
def icono(nombre: str, normal: str = COLOR_ICONO, marcado: str = COLOR_ACTIVO) -> QIcon:
    """QIcon con tres versiones: normal, marcado (checked) y desactivado."""
    ic = QIcon()
    ic.addPixmap(pixmap(nombre, normal), QIcon.Mode.Normal, QIcon.State.Off)
    ic.addPixmap(pixmap(nombre, marcado), QIcon.Mode.Normal, QIcon.State.On)
    ic.addPixmap(pixmap(nombre, COLOR_APAGADO), QIcon.Mode.Disabled, QIcon.State.Off)
    ic.addPixmap(pixmap(nombre, COLOR_APAGADO), QIcon.Mode.Disabled, QIcon.State.On)
    return ic
