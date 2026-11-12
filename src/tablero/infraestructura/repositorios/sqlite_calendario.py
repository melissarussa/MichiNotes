import sqlite3

from ...dominio.calendario import Evento
from ...dominio.utiles import nuevo_id


def _a_evento(f: sqlite3.Row) -> Evento:
    return Evento(id=f["id"], titulo=f["titulo"], inicio=f["inicio"], fin=f["fin"],
                  calendario_id=f["calendario_id"], tablero_id=f["tablero_id"],
                  descripcion=f["descripcion"] or "", color=f["color"] or "#4F8EF7",
                  aviso_minutos=f["aviso_minutos"], notificado=bool(f["notificado"]))


class RepoCalendario:
    def __init__(self, con: sqlite3.Connection, usuario_id: str | None = None):
        self.con = con
        self.usuario_id = usuario_id

    # --- calendarios (los de "Calendarios usuarios" del mockup)
    def asegurar_calendario_por_defecto(self) -> str:
        f = self.con.execute("SELECT id FROM calendarios WHERE usuario_id IS ? LIMIT 1",
                             (self.usuario_id,)).fetchone()
        if f:
            return f["id"]
        return self.crear_calendario("Mi calendario", "#4F8EF7")

    def crear_calendario(self, nombre: str, color: str = "#4F8EF7") -> str:
        cid = nuevo_id()
        with self.con:
            self.con.execute("INSERT INTO calendarios (id, usuario_id, nombre, color) VALUES (?,?,?,?)",
                             (cid, self.usuario_id, nombre, color))
        return cid

    def listar_calendarios(self) -> list[sqlite3.Row]:
        return self.con.execute("SELECT * FROM calendarios WHERE usuario_id IS ? ORDER BY nombre",
                                (self.usuario_id,)).fetchall()

    def fijar_visible(self, calendario_id: str, visible: bool) -> None:
        with self.con:
            self.con.execute("UPDATE calendarios SET visible=? WHERE id=?", (int(visible), calendario_id))

    # --- eventos
    def crear_evento(self, ev: Evento) -> Evento:
        if not ev.id:
            ev.id = nuevo_id()
        if not ev.calendario_id:
            ev.calendario_id = self.asegurar_calendario_por_defecto()
        with self.con:
            self.con.execute(
                "INSERT INTO eventos_calendario (id, calendario_id, tablero_id, titulo, descripcion, color, "
                "inicio, fin, aviso_minutos, notificado) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (ev.id, ev.calendario_id, ev.tablero_id, ev.titulo, ev.descripcion, ev.color, ev.inicio,
                 ev.fin, ev.aviso_minutos, int(ev.notificado)))
        return ev

    def actualizar_evento(self, ev: Evento) -> None:
        with self.con:
            self.con.execute(
                "UPDATE eventos_calendario SET calendario_id=?, tablero_id=?, titulo=?, descripcion=?, color=?, "
                "inicio=?, fin=?, aviso_minutos=?, notificado=? WHERE id=?",
                (ev.calendario_id, ev.tablero_id, ev.titulo, ev.descripcion, ev.color, ev.inicio, ev.fin,
                 ev.aviso_minutos, int(ev.notificado), ev.id))

    def eliminar_evento(self, evento_id: str) -> None:
        with self.con:
            self.con.execute("DELETE FROM eventos_calendario WHERE id=?", (evento_id,))

    def listar_eventos(self, desde: str, hasta: str) -> list[Evento]:
        """Eventos con inicio en [desde, hasta) de los calendarios visibles del usuario."""
        filas = self.con.execute(
            "SELECT e.* FROM eventos_calendario e JOIN calendarios c ON c.id = e.calendario_id "
            "WHERE c.usuario_id IS ? AND c.visible=1 AND e.inicio >= ? AND e.inicio < ? ORDER BY e.inicio",
            (self.usuario_id, desde, hasta)).fetchall()
        return [_a_evento(f) for f in filas]

    def eventos_por_avisar(self, ahora_iso: str) -> list[Evento]:
        """Eventos con aviso configurado cuya hora de aviso ya llegó y que aún no se notificaron."""
        from datetime import datetime, timedelta
        ahora_dt = datetime.fromisoformat(ahora_iso)
        res = []
        filas = self.con.execute(
            "SELECT e.* FROM eventos_calendario e JOIN calendarios c ON c.id = e.calendario_id "
            "WHERE c.usuario_id IS ? AND e.aviso_minutos IS NOT NULL AND e.notificado=0 AND e.inicio >= ?",
            (self.usuario_id, (ahora_dt - timedelta(hours=1)).isoformat(timespec="minutes"))).fetchall()
        for f in filas:
            ev = _a_evento(f)
            if datetime.fromisoformat(ev.inicio) - timedelta(minutes=ev.aviso_minutos) <= ahora_dt:
                res.append(ev)
        return res

    def marcar_notificado(self, evento_id: str) -> None:
        with self.con:
            self.con.execute("UPDATE eventos_calendario SET notificado=1 WHERE id=?", (evento_id,))
