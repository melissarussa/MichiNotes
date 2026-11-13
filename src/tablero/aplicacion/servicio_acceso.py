"""Casos de uso de acceso: crear cuenta, iniciar sesión y recuperar la contraseña.

La app es local (sin servidor de correo), así que la recuperación usa un código de un solo uso que se
muestra al crear la cuenta. Solo se guarda su hash; al usarlo se genera uno nuevo."""
import re
import secrets

from ..dominio.usuario import Usuario
from ..infraestructura import seguridad
from ..infraestructura.repositorios.sqlite_usuarios import RepoUsuarios

MIN_NOMBRE = 2
MIN_CLAVE = 4
MAX_INTENTOS_RECUPERACION = 5
_ALFABETO_CODIGO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"    # sin 0/O/1/I para evitar confusiones
_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ErrorAcceso(Exception):
    pass


def _normalizar_codigo(codigo: str) -> str:
    return re.sub(r"[\s-]", "", codigo or "").upper()


class ServicioAcceso:
    def __init__(self, repo: RepoUsuarios):
        self.repo = repo
        self._fallos: dict[str, int] = {}     # intentos de recuperación fallidos por identificador

    def hay_usuarios(self) -> bool:
        return self.repo.contar() > 0

    # ---- crear cuenta
    def registrar(self, nombre: str, clave: str, correo: str | None = None,
                  confirmar: str | None = None) -> Usuario:
        nombre = (nombre or "").strip()
        correo = (correo or "").strip() or None
        if len(nombre) < MIN_NOMBRE:
            raise ErrorAcceso(f"El nombre de usuario debe tener al menos {MIN_NOMBRE} caracteres.")
        if "@" in nombre:
            raise ErrorAcceso("El nombre de usuario no puede contener «@».")
        if correo is not None and not _CORREO.match(correo):
            raise ErrorAcceso("Escriba un correo válido (por ejemplo, nombre@correo.com).")
        self._validar_clave(clave, confirmar)
        if self.repo.por_nombre(nombre):
            raise ErrorAcceso("Ese nombre de usuario ya existe.")
        if correo and self.repo.por_correo(correo):
            raise ErrorAcceso("Ese correo ya está registrado.")
        return self.repo.crear(nombre, seguridad.crear_hash(clave), correo)

    # ---- iniciar sesión (correo o nombre de usuario)
    def entrar(self, identificador: str, clave: str) -> Usuario:
        r = self.repo.por_identificador((identificador or "").strip())
        if not r or not r[1] or not seguridad.verificar(clave, r[1]):
            raise ErrorAcceso("Usuario o contraseña incorrectos.")
        return r[0]

    # ---- recuperar contraseña
    def nuevo_codigo_recuperacion(self, usuario_id: str) -> str:
        """Genera un código nuevo (anula el anterior) y lo devuelve en claro UNA sola vez."""
        codigo = self._generar_codigo()
        self.repo.guardar_hash_recuperacion(usuario_id, seguridad.crear_hash(_normalizar_codigo(codigo)))
        return codigo

    def recuperar_clave(self, identificador: str, codigo: str, nueva_clave: str,
                        confirmar: str | None = None) -> tuple[Usuario, str]:
        """Restablece la contraseña con el código de recuperación.
        Devuelve (usuario, código_nuevo): el código usado deja de servir."""
        ident = (identificador or "").strip()
        clave_fallos = ident.lower()
        if self._fallos.get(clave_fallos, 0) >= MAX_INTENTOS_RECUPERACION:
            raise ErrorAcceso("Demasiados intentos fallidos. Cierra y abre la aplicación para intentarlo de nuevo.")
        self._validar_clave(nueva_clave, confirmar)
        r = self.repo.por_identificador(ident)
        hash_codigo = self.repo.hash_recuperacion(r[0].id) if r else None
        cod = _normalizar_codigo(codigo)
        if not r or not hash_codigo or not cod or not seguridad.verificar(cod, hash_codigo):
            self._fallos[clave_fallos] = self._fallos.get(clave_fallos, 0) + 1
            raise ErrorAcceso("El usuario o el código de recuperación no son correctos.")
        usuario = r[0]
        nuevo = self._generar_codigo()
        self.repo.cambiar_clave(usuario.id, seguridad.crear_hash(nueva_clave),
                                seguridad.crear_hash(_normalizar_codigo(nuevo)))
        self._fallos.pop(clave_fallos, None)
        return usuario, nuevo

    # ---- internos
    @staticmethod
    def _validar_clave(clave: str, confirmar: str | None) -> None:
        if len(clave or "") < MIN_CLAVE:
            raise ErrorAcceso(f"La contraseña debe tener al menos {MIN_CLAVE} caracteres.")
        if confirmar is not None and clave != confirmar:
            raise ErrorAcceso("Las contraseñas no coinciden.")

    @staticmethod
    def _generar_codigo() -> str:
        c = "".join(secrets.choice(_ALFABETO_CODIGO) for _ in range(12))
        return f"{c[:4]}-{c[4:8]}-{c[8:]}"
