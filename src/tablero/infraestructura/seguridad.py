"""Hash de contraseñas: argon2 si está instalado; si no, scrypt de la biblioteca estándar."""
import base64
import hashlib
import hmac
import os

try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError, InvalidHashError
    _ph = PasswordHasher()
except ImportError:      # pragma: no cover
    _ph = None


def crear_hash(clave: str) -> str:
    if _ph:
        return _ph.hash(clave)
    sal = os.urandom(16)
    h = hashlib.scrypt(clave.encode(), salt=sal, n=2**14, r=8, p=1)
    return "scrypt$" + base64.b64encode(sal).decode() + "$" + base64.b64encode(h).decode()


def verificar(clave: str, hash_guardado: str) -> bool:
    if hash_guardado.startswith("scrypt$"):
        _, sal, h = hash_guardado.split("$")
        calc = hashlib.scrypt(clave.encode(), salt=base64.b64decode(sal), n=2**14, r=8, p=1)
        return hmac.compare_digest(calc, base64.b64decode(h))
    if _ph is None:      # pragma: no cover
        return False
    try:
        return _ph.verify(hash_guardado, clave)
    except (VerifyMismatchError, InvalidHashError):
        return False
