import sqlite3

from ...dominio.usuario import Usuario
from ...dominio.utiles import ahora, nuevo_id


class RepoUsuarios:
    def __init__(self, con: sqlite3.Connection):
        self.con = con

    def contar(self) -> int:
        return self.con.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]

    def crear(self, nombre: str, hash_clave: str | None, correo: str | None = None) -> Usuario:
        uid = nuevo_id()
        with self.con:
            self.con.execute("INSERT INTO usuarios (id, nombre, correo, hash_clave, creado_en) VALUES (?,?,?,?,?)",
                             (uid, nombre, correo, hash_clave, ahora()))
        return Usuario(uid, nombre, correo)

    def por_nombre(self, nombre: str) -> tuple[Usuario, str | None] | None:
        f = self.con.execute("SELECT * FROM usuarios WHERE nombre=? COLLATE NOCASE", (nombre,)).fetchone()
        if not f:
            return None
        return Usuario(f["id"], f["nombre"], f["correo"]), f["hash_clave"]
