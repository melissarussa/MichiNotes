import json
import sqlite3

from ...dominio.tablero import Tablero
from ...dominio.utiles import ahora, nuevo_id


def _a_tablero(f: sqlite3.Row) -> Tablero:
    return Tablero(id=f["id"], nombre=f["nombre"], propietario_id=f["propietario_id"],
                   config=json.loads(f["config_json"]), creado_en=f["creado_en"],
                   actualizado_en=f["actualizado_en"], eliminado_en=f["eliminado_en"])


class RepoTableros:
    def __init__(self, con: sqlite3.Connection, usuario_id: str | None = None):
        self.con = con
        self.usuario_id = usuario_id

    def crear(self, nombre: str) -> Tablero:
        t, tid = ahora(), nuevo_id()
        with self.con:
            self.con.execute(
                "INSERT INTO tableros (id, propietario_id, nombre, creado_en, actualizado_en) VALUES (?,?,?,?,?)",
                (tid, self.usuario_id, nombre, t, t))
        return self.obtener(tid)

    def obtener(self, tablero_id: str) -> Tablero | None:
        f = self.con.execute("SELECT * FROM tableros WHERE id=?", (tablero_id,)).fetchone()
        return _a_tablero(f) if f else None

    def listar(self, texto: str = "") -> list[Tablero]:
        filas = self.con.execute(
            "SELECT * FROM tableros WHERE eliminado_en IS NULL AND (propietario_id IS ? OR propietario_id=?) "
            "AND nombre LIKE ? ORDER BY actualizado_en DESC",
            (self.usuario_id, self.usuario_id, f"%{texto}%")).fetchall()
        return [_a_tablero(f) for f in filas]

    def renombrar(self, tablero_id: str, nombre: str) -> None:
        with self.con:
            self.con.execute("UPDATE tableros SET nombre=?, actualizado_en=? WHERE id=?",
                             (nombre, ahora(), tablero_id))

    def guardar_config(self, tablero_id: str, config: dict) -> None:
        with self.con:
            self.con.execute("UPDATE tableros SET config_json=?, actualizado_en=? WHERE id=?",
                             (json.dumps(config), ahora(), tablero_id))

    def tocar(self, tablero_id: str) -> None:
        with self.con:
            self.con.execute("UPDATE tableros SET actualizado_en=? WHERE id=?", (ahora(), tablero_id))

    def eliminar(self, tablero_id: str) -> None:
        with self.con:
            self.con.execute("UPDATE tableros SET eliminado_en=? WHERE id=?", (ahora(), tablero_id))

    def restaurar(self, tablero_id: str) -> None:
        with self.con:
            self.con.execute("UPDATE tableros SET eliminado_en=NULL WHERE id=?", (tablero_id,))

    def listar_eliminados(self) -> list[Tablero]:
        filas = self.con.execute(
            "SELECT * FROM tableros WHERE eliminado_en IS NOT NULL AND (propietario_id IS ? OR propietario_id=?) "
            "ORDER BY eliminado_en DESC", (self.usuario_id, self.usuario_id)).fetchall()
        return [_a_tablero(f) for f in filas]
