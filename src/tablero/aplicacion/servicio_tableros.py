"""Casos de uso sobre los elementos del tablero. Todo pasa por aquí: guarda en la base,
registra el comando para deshacer y avisa a la interfaz mediante el bus."""
from .bus_eventos import BusEventos
from .comandos import Comando, Historial
from ..dominio.elementos import Elemento
from ..infraestructura.repositorios.sqlite_elementos import RepoElementos

CAMPOS = ("x", "y", "ancho", "alto", "z_index", "bloqueado", "propiedades")


class ServicioElementos:
    def __init__(self, repo: RepoElementos, bus: BusEventos, historial: Historial):
        self.repo, self.bus, self.historial = repo, bus, historial

    # ---- internos (no tocan el historial)
    def _aplicar(self, estado: Elemento) -> None:
        e = estado.copia()
        self.repo.actualizar(e)
        self.bus.emitir("elemento_actualizado", elemento=e)

    def _quitar(self, elemento_id: str) -> None:
        self.repo.marcar_eliminado(elemento_id)
        self.bus.emitir("elemento_eliminado", elemento_id=elemento_id)

    def _poner(self, elemento_id: str) -> None:
        self.repo.restaurar(elemento_id)
        self.bus.emitir("elemento_creado", elemento=self.repo.obtener(elemento_id))

    # ---- casos de uso
    def crear(self, e: Elemento) -> Elemento:
        if e.z_index == 0:
            e.z_index = self.repo.siguiente_z(e.tablero_id)
        self.repo.crear(e)
        self.bus.emitir("elemento_creado", elemento=e)
        # el elemento ya existe: "hacer" (al rehacer) lo restaura; "deshacer" lo manda al basurero
        self.historial.ejecutar(Comando(f"Crear {e.tipo}", lambda: None, lambda: self._quitar(e.id)))
        self.historial._deshacer[-1].hacer = lambda: self._poner(e.id)
        return e

    def modificar(self, elemento_id: str, descripcion: str = "Editar", **campos) -> bool:
        antes = self.repo.obtener(elemento_id)
        if antes is None:
            return False
        despues = antes.copia()
        for k, v in campos.items():
            if k not in CAMPOS:
                raise ValueError(f"Campo no editable: {k}")
            setattr(despues, k, v)
        if all(getattr(antes, k) == getattr(despues, k) for k in CAMPOS):
            return False
        self.historial.ejecutar(Comando(descripcion, lambda: self._aplicar(despues), lambda: self._aplicar(antes)))
        return True

    def mover(self, elemento_id: str, x: float, y: float) -> bool:
        return self.modificar(elemento_id, "Mover", x=x, y=y)

    def editar_propiedades(self, elemento_id: str, **props) -> bool:
        e = self.repo.obtener(elemento_id)
        if e is None:
            return False
        nuevas = {**e.propiedades, **props}
        return self.modificar(elemento_id, "Editar", propiedades=nuevas)

    def mover_varios(self, movimientos: dict[str, tuple[float, float]]) -> bool:
        """Mueve varios elementos como UNA sola acción (un Ctrl+Z los regresa a todos)."""
        pares = []
        for eid, (x, y) in movimientos.items():
            antes = self.repo.obtener(eid)
            if antes is None or (antes.x, antes.y) == (x, y):
                continue
            despues = antes.copia()
            despues.x, despues.y = x, y
            pares.append((antes, despues))
        if not pares:
            return False
        self.historial.ejecutar(Comando(
            "Mover", lambda: [self._aplicar(d) for _, d in pares], lambda: [self._aplicar(a) for a, _ in pares]))
        return True

    def eliminar_varios(self, ids: list[str]) -> None:
        ids = [i for i in ids if (e := self.repo.obtener(i)) and not e.eliminado_en]
        if not ids:
            return
        self.historial.ejecutar(Comando(
            "Eliminar", lambda: [self._quitar(i) for i in ids], lambda: [self._poner(i) for i in ids]))

    def eliminar(self, elemento_id: str) -> None:
        e = self.repo.obtener(elemento_id)
        if e is None or e.eliminado_en:
            return
        self.historial.ejecutar(Comando("Eliminar", lambda: self._quitar(elemento_id),
                                        lambda: self._poner(elemento_id)))

    def restaurar(self, elemento_id: str) -> None:
        """Saca del basurero (también entra al historial)."""
        self.historial.ejecutar(Comando("Restaurar", lambda: self._poner(elemento_id),
                                        lambda: self._quitar(elemento_id)))

    def borrar_definitivo(self, elemento_id: str) -> None:
        self.repo.borrar_definitivo(elemento_id)
        self.bus.emitir("basurero_cambio")

    def traer_al_frente(self, elemento_id: str) -> bool:
        e = self.repo.obtener(elemento_id)
        return self.modificar(elemento_id, "Traer al frente", z_index=self.repo.siguiente_z(e.tablero_id)) if e else False

    def enviar_al_fondo(self, elemento_id: str) -> bool:
        e = self.repo.obtener(elemento_id)
        return self.modificar(elemento_id, "Enviar al fondo", z_index=self.repo.minimo_z(e.tablero_id)) if e else False

    def alternar_bloqueo(self, elemento_id: str) -> bool:
        e = self.repo.obtener(elemento_id)
        return self.modificar(elemento_id, "Bloquear", bloqueado=not e.bloqueado) if e else False

    def duplicar(self, elemento_id: str, desplazamiento: float = 24) -> Elemento | None:
        e = self.repo.obtener(elemento_id)
        if e is None:
            return None
        from ..dominio.utiles import ahora, nuevo_id
        c = e.copia()
        c.id, c.x, c.y, c.z_index, c.revision = nuevo_id(), e.x + desplazamiento, e.y + desplazamiento, 0, 0
        c.creado_en = c.actualizado_en = ahora()
        c.eliminado_en = None
        return self.crear(c)
