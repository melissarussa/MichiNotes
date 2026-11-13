import sqlite3

from ...dominio.usuario import Usuario
from ...dominio.utiles import ahora, nuevo_id


class RepoUsuarios:
    def __init__(self, con: sqlite3.Connection):
        self.con = con

    def contar(self) -> int:
        return self.con.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]

    def crear(self, nombre: str, hash_clave: str | None, correo: str | None = None,
              hash_recuperacion: str | None = None) -> Usuario:
        uid = nuevo_id()
        with self.con:
            self.con.execute(
                "INSERT INTO usuarios (id, nombre, correo, hash_clave, hash_recuperacion, creado_en) "
                "VALUES (?,?,?,?,?,?)",
                (uid, nombre, correo, hash_clave, hash_recuperacion, ahora()))
        return Usuario(uid, nombre, correo)

    @staticmethod
    def _a_usuario(f: sqlite3.Row) -> Usuario:
        return Usuario(f["id"], f["nombre"], f["correo"])

    def por_nombre(self, nombre: str) -> tuple[Usuario, str | None] | None:
        f = self.con.execute("SELECT * FROM usuarios WHERE nombre=? COLLATE NOCASE", (nombre,)).fetchone()
        return (self._a_usuario(f), f["hash_clave"]) if f else None

    def por_correo(self, correo: str) -> Usuario | None:
        f = self.con.execute("SELECT * FROM usuarios WHERE correo=? COLLATE NOCASE", (correo,)).fetchone()
        return self._a_usuario(f) if f else None

    def por_identificador(self, ident: str) -> tuple[Usuario, str | None] | None:
        """Busca por nombre de usuario o por correo (sin distinguir mayúsculas)."""
        f = self.con.execute(
            "SELECT * FROM usuarios WHERE nombre=? COLLATE NOCASE OR correo=? COLLATE NOCASE",
            (ident, ident)).fetchone()
        return (self._a_usuario(f), f["hash_clave"]) if f else None

    def hash_recuperacion(self, usuario_id: str) -> str | None:
        f = self.con.execute("SELECT hash_recuperacion FROM usuarios WHERE id=?", (usuario_id,)).fetchone()
        return f["hash_recuperacion"] if f else None

    def guardar_hash_recuperacion(self, usuario_id: str, hash_codigo: str) -> None:
        with self.con:
            self.con.execute("UPDATE usuarios SET hash_recuperacion=? WHERE id=?", (hash_codigo, usuario_id))

    def cambiar_clave(self, usuario_id: str, hash_clave: str, hash_recuperacion: str | None = None) -> None:
        """Cambia la clave (y, si se da, el código de recuperación) en una sola transacción."""
        with self.con:
            self.con.execute("UPDATE usuarios SET hash_clave=? WHERE id=?", (hash_clave, usuario_id))
            if hash_recuperacion is not None:
                self.con.execute("UPDATE usuarios SET hash_recuperacion=? WHERE id=?",
                                 (hash_recuperacion, usuario_id))
