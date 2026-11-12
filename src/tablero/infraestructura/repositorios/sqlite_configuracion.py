import sqlite3


class RepoConfiguracion:
    def __init__(self, con: sqlite3.Connection):
        self.con = con

    def obtener(self, clave: str, defecto: str | None = None) -> str | None:
        f = self.con.execute("SELECT valor FROM configuracion WHERE clave=?", (clave,)).fetchone()
        return f["valor"] if f else defecto

    def guardar(self, clave: str, valor: str) -> None:
        with self.con:
            self.con.execute("INSERT INTO configuracion (clave, valor) VALUES (?,?) "
                             "ON CONFLICT(clave) DO UPDATE SET valor=excluded.valor", (clave, valor))
