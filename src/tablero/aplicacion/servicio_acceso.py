from ..dominio.usuario import Usuario
from ..infraestructura import seguridad
from ..infraestructura.repositorios.sqlite_usuarios import RepoUsuarios


class ErrorAcceso(Exception):
    pass


class ServicioAcceso:
    def __init__(self, repo: RepoUsuarios):
        self.repo = repo

    def hay_usuarios(self) -> bool:
        return self.repo.contar() > 0

    def registrar(self, nombre: str, clave: str) -> Usuario:
        nombre = nombre.strip()
        if len(nombre) < 2:
            raise ErrorAcceso("El nombre debe tener al menos 2 caracteres.")
        if len(clave) < 4:
            raise ErrorAcceso("La clave debe tener al menos 4 caracteres.")
        if self.repo.por_nombre(nombre):
            raise ErrorAcceso("Ese usuario ya existe.")
        return self.repo.crear(nombre, seguridad.crear_hash(clave))

    def entrar(self, nombre: str, clave: str) -> Usuario:
        r = self.repo.por_nombre(nombre.strip())
        if not r or not r[1] or not seguridad.verificar(clave, r[1]):
            raise ErrorAcceso("Usuario o clave incorrectos.")
        return r[0]
