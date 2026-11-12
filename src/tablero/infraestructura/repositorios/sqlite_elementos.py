import json
import sqlite3

from ...dominio.elementos import Elemento
from ...dominio.utiles import ahora, nuevo_id


def _a_elemento(f: sqlite3.Row) -> Elemento:
    return Elemento(
        id=f["id"], tablero_id=f["tablero_id"], tipo=f["tipo"], x=f["x"], y=f["y"],
        ancho=f["ancho"], alto=f["alto"], z_index=f["z_index"], bloqueado=bool(f["bloqueado"]),
        propiedades=json.loads(f["propiedades"]), padre_id=f["padre_id"], revision=f["revision"],
        creado_en=f["creado_en"], actualizado_en=f["actualizado_en"], eliminado_en=f["eliminado_en"])


class RepoElementos:
    def __init__(self, con: sqlite3.Connection, usuario_id: str | None = None):
        self.con = con
        self.usuario_id = usuario_id

    def _registrar(self, tablero_id, elemento_id, operacion, datos=None):
        self.con.execute(
            "INSERT INTO cambios (id, tablero_id, elemento_id, usuario_id, operacion, datos_json, marca_tiempo) "
            "VALUES (?,?,?,?,?,?,?)",
            (nuevo_id(), tablero_id, elemento_id, self.usuario_id, operacion,
             json.dumps(datos or {}, ensure_ascii=False), ahora()))

    def crear(self, e: Elemento) -> Elemento:
        with self.con:
            self.con.execute(
                "INSERT INTO elementos (id, tablero_id, padre_id, tipo, x, y, ancho, alto, z_index, bloqueado, "
                "propiedades, creado_por, creado_en, actualizado_en, revision) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (e.id, e.tablero_id, e.padre_id, e.tipo, e.x, e.y, e.ancho, e.alto, e.z_index, int(e.bloqueado),
                 json.dumps(e.propiedades, ensure_ascii=False), self.usuario_id, e.creado_en, e.actualizado_en,
                 e.revision))
            self._registrar(e.tablero_id, e.id, "crear", {"tipo": e.tipo})
        return e

    def obtener(self, elemento_id: str) -> Elemento | None:
        f = self.con.execute("SELECT * FROM elementos WHERE id=?", (elemento_id,)).fetchone()
        return _a_elemento(f) if f else None

    def listar(self, tablero_id: str) -> list[Elemento]:
        filas = self.con.execute(
            "SELECT * FROM elementos WHERE tablero_id=? AND eliminado_en IS NULL ORDER BY z_index, creado_en",
            (tablero_id,)).fetchall()
        return [_a_elemento(f) for f in filas]

    def listar_eliminados(self, tablero_id: str) -> list[Elemento]:
        filas = self.con.execute(
            "SELECT * FROM elementos WHERE tablero_id=? AND eliminado_en IS NOT NULL ORDER BY eliminado_en DESC",
            (tablero_id,)).fetchall()
        return [_a_elemento(f) for f in filas]

    def actualizar(self, e: Elemento, operacion: str = "editar") -> None:
        """Guarda posición, tamaño, capa, bloqueo y propiedades. Sube la revisión."""
        t = ahora()
        with self.con:
            self.con.execute(
                "UPDATE elementos SET x=?, y=?, ancho=?, alto=?, z_index=?, bloqueado=?, propiedades=?, "
                "actualizado_en=?, revision=revision+1 WHERE id=?",
                (e.x, e.y, e.ancho, e.alto, e.z_index, int(e.bloqueado),
                 json.dumps(e.propiedades, ensure_ascii=False), t, e.id))
            self._registrar(e.tablero_id, e.id, operacion, {"x": e.x, "y": e.y})
        e.actualizado_en = t
        e.revision += 1

    def marcar_eliminado(self, elemento_id: str) -> None:
        f = self.con.execute("SELECT tablero_id FROM elementos WHERE id=?", (elemento_id,)).fetchone()
        with self.con:
            self.con.execute("UPDATE elementos SET eliminado_en=?, revision=revision+1 WHERE id=?",
                             (ahora(), elemento_id))
            if f:
                self._registrar(f["tablero_id"], elemento_id, "eliminar")

    def restaurar(self, elemento_id: str) -> None:
        f = self.con.execute("SELECT tablero_id FROM elementos WHERE id=?", (elemento_id,)).fetchone()
        with self.con:
            self.con.execute("UPDATE elementos SET eliminado_en=NULL, revision=revision+1 WHERE id=?",
                             (elemento_id,))
            if f:
                self._registrar(f["tablero_id"], elemento_id, "restaurar")

    def borrar_definitivo(self, elemento_id: str) -> None:
        with self.con:
            self.con.execute("DELETE FROM cambios WHERE elemento_id=?", (elemento_id,))
            self.con.execute("DELETE FROM elementos WHERE id=?", (elemento_id,))

    def siguiente_z(self, tablero_id: str) -> int:
        f = self.con.execute("SELECT COALESCE(MAX(z_index), 0) + 1 AS z FROM elementos WHERE tablero_id=?",
                             (tablero_id,)).fetchone()
        return f["z"]

    def minimo_z(self, tablero_id: str) -> int:
        f = self.con.execute("SELECT COALESCE(MIN(z_index), 0) - 1 AS z FROM elementos WHERE tablero_id=?",
                             (tablero_id,)).fetchone()
        return f["z"]
