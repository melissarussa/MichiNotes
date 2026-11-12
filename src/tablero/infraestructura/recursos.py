"""Imágenes importadas: se copian a la carpeta de datos (copia, no enlace) y se registran en 'recursos'."""
import hashlib
import mimetypes
import shutil
import sqlite3
from pathlib import Path

from ..dominio.utiles import nuevo_id


def importar_imagen(con: sqlite3.Connection, carpeta_datos: Path, tablero_id: str, origen: Path | str) -> str:
    """Devuelve la ruta relativa (a carpeta_datos) de la copia."""
    origen = Path(origen)
    contenido = origen.read_bytes()
    sha = hashlib.sha256(contenido).hexdigest()
    rel = Path("recursos") / tablero_id / f"{sha[:16]}{origen.suffix.lower()}"
    destino = carpeta_datos / rel
    destino.parent.mkdir(parents=True, exist_ok=True)
    if not destino.exists():
        shutil.copyfile(origen, destino)
    ya = con.execute("SELECT 1 FROM recursos WHERE hash_sha256=? AND tablero_id=?", (sha, tablero_id)).fetchone()
    if not ya:
        with con:
            con.execute(
                "INSERT INTO recursos (id, tablero_id, nombre_original, tipo_mime, ruta_relativa, hash_sha256, "
                "tamano_bytes) VALUES (?,?,?,?,?,?,?)",
                (nuevo_id(), tablero_id, origen.name, mimetypes.guess_type(origen.name)[0],
                 rel.as_posix(), sha, len(contenido)))
    return rel.as_posix()
