"""La escena contiene todos los ítems del tablero y atiende las herramientas (crear, dibujar, borrar)."""

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsScene, QMenu

from ...dominio.elementos import nuevo_elemento
from .fabrica import crear_item
from .items.base import ItemBase
from .items.dibujo import ItemDibujo, pluma

LIMITE = 20000


class EscenaTablero(QGraphicsScene):
    def __init__(self, ctx, opciones: dict, parent=None):
        super().__init__(parent)
        self.ctx = ctx
        self.opciones = opciones          # compartido con los paneles (color, grosor, forma...)
        self.tablero_id: str | None = None
        self.config: dict = {}
        self.herramienta = "seleccionar"
        self._items: dict[str, ItemBase] = {}
        self._posiciones: dict[str, QPointF] = {}
        self._puntos: list[list[float]] = []
        self._previa: QGraphicsPathItem | None = None
        self._borrados: set[str] = set()
        self.setSceneRect(-LIMITE / 2, -LIMITE / 2, LIMITE, LIMITE)
        ctx.bus.suscribir("elemento_creado", self._al_crear)
        ctx.bus.suscribir("elemento_actualizado", self._al_actualizar)
        ctx.bus.suscribir("elemento_eliminado", self._al_eliminar)

    # ---- carga
    def cargar(self, tablero_id: str) -> None:
        self.clear()
        self._items.clear()
        self._previa = None
        self.tablero_id = tablero_id
        t = self.ctx.tableros.obtener(tablero_id)
        self.config = dict(t.config) if t else {}
        for e in self.ctx.repo_elementos.listar(tablero_id):
            self._agregar(e)
        self.update()

    def _agregar(self, e) -> None:
        if e.id in self._items:
            self._items[e.id].aplicar(e)
            return
        item = crear_item(e, self.ctx)
        self._items[e.id] = item
        self.addItem(item)

    def _al_crear(self, elemento) -> None:
        if elemento.tablero_id == self.tablero_id:
            self._agregar(elemento)

    def _al_actualizar(self, elemento) -> None:
        item = self._items.get(elemento.id)
        if item is not None:
            item.aplicar(elemento)

    def _al_eliminar(self, elemento_id) -> None:
        item = self._items.pop(elemento_id, None)
        if item is not None:
            self.removeItem(item)

    def items_tablero(self) -> list[ItemBase]:
        return [i for i in self.selectedItems() if isinstance(i, ItemBase)]

    # ---- fondo del lienzo
    def drawBackground(self, painter, rect: QRectF) -> None:
        fondo = QColor(self.config.get("fondo") or "#FAFAFA")
        painter.fillRect(rect, fondo)
        estilo = self.config.get("lienzo", "cuadricula")
        if estilo == "liso":
            return
        paso = 40
        linea = QColor(255, 255, 255, 28) if fondo.lightness() < 128 else QColor(0, 0, 0, 30)
        izq, arriba = int(rect.left() // paso) * paso, int(rect.top() // paso) * paso
        if estilo == "puntos":
            painter.setPen(QPen(linea, 3))
            x = izq
            while x < rect.right():
                y = arriba
                while y < rect.bottom():
                    painter.drawPoint(QPointF(x, y))
                    y += paso
                x += paso
        else:
            painter.setPen(QPen(linea, 1))
            x = izq
            while x < rect.right():
                painter.drawLine(QPointF(x, rect.top()), QPointF(x, rect.bottom()))
                x += paso
            y = arriba
            while y < rect.bottom():
                painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))
                y += paso

    # ---- creación de elementos
    def crear_en(self, tipo: str, pos: QPointF, **props):
        if not self.tablero_id:
            return None
        e = nuevo_elemento(tipo, self.tablero_id, pos.x(), pos.y(), **props)
        return self.ctx.servicio.crear(e)

    def _propiedades_nuevas(self, tipo: str) -> dict:
        fmt = {k: v for k, v in self.opciones.get("texto", {}).items() if v not in (None, "")}
        if tipo == "nota":
            return {"texto": "", "color": self.opciones.get("color_nota", "#FFEB3B"), **fmt}
        if tipo == "lista":
            return {"titulo": "Mi lista", "items": [{"texto": "Tarea 1", "hecho": False}], **fmt}
        if tipo == "enlace":
            return {"titulo": "Enlace", "url": "", **fmt}
        if tipo == "texto":
            return {"texto": "Texto", **fmt}
        if tipo == "figura":
            f = self.opciones.get("figura", {})
            return {"forma": f.get("forma", "rectangulo"), "relleno": f.get("relleno", ""),
                    "borde": f.get("borde", "#333333"), "grosor": f.get("grosor", 2)}
        return {}

    def crear_con_herramienta(self, tipo: str, pos: QPointF) -> None:
        item = self.crear_en(tipo, pos, **self._propiedades_nuevas(tipo))
        if item is not None:
            self.clearSelection()
            it = self._items.get(item.id)
            if it:
                it.setSelected(True)
                if tipo in ("nota", "lista", "enlace", "texto"):
                    it.editar()

    # ---- ratón según herramienta
    def mousePressEvent(self, ev) -> None:
        h = self.herramienta
        if ev.button() != Qt.MouseButton.LeftButton or h == "seleccionar":
            super().mousePressEvent(ev)
            self._posiciones = {i.e.id: QPointF(i.pos()) for i in self.items_tablero()}
            return
        p = ev.scenePos()
        if h in ("nota", "lista", "enlace", "texto", "figura"):
            self.crear_con_herramienta(h, p)
            ev.accept()
        elif h == "pincel":
            self._puntos = [[p.x(), p.y()]]
            self._previa = QGraphicsPathItem()
            self._previa.setPen(pluma(self._props_pincel()))
            self._previa.setZValue(1e9)
            self.addItem(self._previa)
            self._actualizar_previa()
            ev.accept()
        elif h == "borrador":
            self._borrados = set()
            self._borrar_en(p)
            ev.accept()

    def mouseMoveEvent(self, ev) -> None:
        h = self.herramienta
        if h == "pincel" and self._previa is not None:
            p = ev.scenePos()
            ux, uy = self._puntos[-1]
            if (p.x() - ux) ** 2 + (p.y() - uy) ** 2 >= 2.5:
                self._puntos.append([p.x(), p.y()])
                self._actualizar_previa()
            ev.accept()
        elif h == "borrador" and ev.buttons() & Qt.MouseButton.LeftButton:
            self._borrar_en(ev.scenePos())
            ev.accept()
        else:
            super().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, ev) -> None:
        h = self.herramienta
        if h == "pincel" and self._previa is not None:
            self.removeItem(self._previa)
            self._previa = None
            if self._puntos:
                self.crear_en("dibujo", QPointF(0, 0), puntos=[[round(x, 1), round(y, 1)] for x, y in self._puntos],
                              **self._props_pincel())
            self._puntos = []
            ev.accept()
            return
        if h == "borrador":
            self.ctx.servicio.eliminar_varios(list(self._borrados))
            self._borrados = set()
            ev.accept()
            return
        super().mouseReleaseEvent(ev)
        # mover varios ítems seleccionados = una sola acción en el historial
        mov = {}
        for item in self.items_tablero():
            antes = self._posiciones.get(item.e.id)
            if antes is not None and item.pos() != antes:
                mov[item.e.id] = (item.pos().x(), item.pos().y())
        if mov:
            self.ctx.servicio.mover_varios(mov)
        self._posiciones = {}

    def girar_seleccion(self, grados: float) -> None:
        """Gira las figuras seleccionadas (grados > 0: hacia la derecha)."""
        for it in self.items_tablero():
            if it.girable and not it.e.bloqueado:
                self.ctx.servicio.editar_propiedades(it.e.id, rotacion=(float(it.p.get("rotacion", 0)) + grados) % 360)

    def _props_pincel(self) -> dict:
        p = self.opciones.get("pincel", {})
        return {"color": p.get("color", "#222222"), "grosor": p.get("grosor", 4), "estilo": p.get("estilo", "duro")}

    def _actualizar_previa(self) -> None:
        from .items.dibujo import trazado
        self._previa.setPath(trazado(self._puntos))

    def _borrar_en(self, p: QPointF) -> None:
        zona = QRectF(p.x() - 7, p.y() - 7, 14, 14)
        for it in self.items(zona):
            if isinstance(it, ItemDibujo) and not it.e.bloqueado and it.e.id not in self._borrados:
                self._borrados.add(it.e.id)
                it.setOpacity(0.25)       # vista previa: se verá borrado al soltar

    # ---- menú contextual
    def contextMenuEvent(self, ev) -> None:
        item = self.itemAt(ev.scenePos(), __import__("PySide6.QtGui", fromlist=["QTransform"]).QTransform())
        menu = QMenu()
        srv = self.ctx.servicio
        if isinstance(item, ItemBase):
            if not item.isSelected():
                self.clearSelection()
                item.setSelected(True)
            sel = self.items_tablero()
            if len(sel) == 1 and not isinstance(item, ItemDibujo):
                menu.addAction("Editar…", item.editar)
            if item.girable and not item.e.bloqueado:
                menu.addAction("Girar 90° a la derecha", lambda: self.girar_seleccion(90))
                menu.addAction("Girar 90° a la izquierda", lambda: self.girar_seleccion(-90))
                menu.addAction("Quitar giro", lambda: [srv.editar_propiedades(i.e.id, rotacion=0) for i in sel if i.girable])
            menu.addAction("Duplicar", lambda: [srv.duplicar(i.e.id) for i in sel])
            menu.addAction("Traer al frente", lambda: [srv.traer_al_frente(i.e.id) for i in sel])
            menu.addAction("Enviar al fondo", lambda: [srv.enviar_al_fondo(i.e.id) for i in sel])
            menu.addAction("Bloquear / desbloquear", lambda: [srv.alternar_bloqueo(i.e.id) for i in sel])
            menu.addSeparator()
            menu.addAction("Eliminar (a la papelera)", lambda: srv.eliminar_varios([i.e.id for i in sel]))
        else:
            for etiqueta, tipo in (("Nueva nota", "nota"), ("Nueva lista", "lista"),
                                   ("Nuevo enlace", "enlace"), ("Nuevo texto", "texto")):
                menu.addAction(etiqueta, lambda t=tipo: self.crear_con_herramienta(t, ev.scenePos()))
        menu.exec(ev.screenPos())
        ev.accept()

    def mouseDoubleClickEvent(self, ev) -> None:
        if self.herramienta == "mano":      # con la Mano no se edita ni se crea nada
            ev.accept()
            return
        if self.herramienta == "seleccionar" and self.itemAt(ev.scenePos(), __import__("PySide6.QtGui", fromlist=["QTransform"]).QTransform()) is None:
            self.crear_con_herramienta("nota", ev.scenePos())
            ev.accept()
            return
        super().mouseDoubleClickEvent(ev)
