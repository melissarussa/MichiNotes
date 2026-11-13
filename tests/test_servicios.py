import pytest

from tablero.aplicacion.servicio_acceso import ErrorAcceso, ServicioAcceso
from tablero.dominio.calendario import Evento
from tablero.dominio.elementos import nuevo_elemento
from tablero.infraestructura import recursos, respaldo
from tablero.infraestructura.base_datos.conexion import abrir_conexion
from tablero.infraestructura.repositorios.sqlite_calendario import RepoCalendario
from tablero.infraestructura.repositorios.sqlite_configuracion import RepoConfiguracion
from tablero.infraestructura.repositorios.sqlite_tableros import RepoTableros
from tablero.infraestructura.repositorios.sqlite_usuarios import RepoUsuarios


def test_crear_mover_deshacer_rehacer(servicio, tablero):
    e = servicio.crear(nuevo_elemento("nota", tablero.id, 10, 20, texto="hola"))
    assert [x.id for x in servicio.repo.listar(tablero.id)] == [e.id]
    servicio.mover(e.id, 300, 400)
    assert (servicio.repo.obtener(e.id).x, servicio.repo.obtener(e.id).y) == (300, 400)
    servicio.historial.deshacer()
    assert servicio.repo.obtener(e.id).x == 10
    servicio.historial.rehacer()
    assert servicio.repo.obtener(e.id).x == 300


def test_deshacer_crear_va_al_basurero_y_rehacer_lo_trae(servicio, tablero):
    e = servicio.crear(nuevo_elemento("nota", tablero.id, 0, 0))
    servicio.historial.deshacer()
    assert servicio.repo.listar(tablero.id) == []
    assert len(servicio.repo.listar_eliminados(tablero.id)) == 1
    servicio.historial.rehacer()
    assert len(servicio.repo.listar(tablero.id)) == 1
    assert servicio.eventos[-1] == "elemento_creado"


def test_eliminar_restaurar(servicio, tablero):
    e = servicio.crear(nuevo_elemento("lista", tablero.id, 0, 0, items=[]))
    servicio.eliminar(e.id)
    assert servicio.repo.listar(tablero.id) == []
    servicio.restaurar(e.id)
    assert len(servicio.repo.listar(tablero.id)) == 1
    servicio.eliminar(e.id)
    servicio.borrar_definitivo(e.id)
    assert servicio.repo.obtener(e.id) is None


def test_editar_propiedades_conserva_otras(servicio, tablero):
    e = servicio.crear(nuevo_elemento("nota", tablero.id, 0, 0, texto="a", color="#fff"))
    servicio.editar_propiedades(e.id, texto="b")
    p = servicio.repo.obtener(e.id).propiedades
    assert p == {"texto": "b", "color": "#fff"}
    assert servicio.editar_propiedades(e.id, texto="b") is False   # sin cambios: no ensucia el historial


def test_capas_y_bloqueo(servicio, tablero):
    a = servicio.crear(nuevo_elemento("nota", tablero.id, 0, 0))
    b = servicio.crear(nuevo_elemento("nota", tablero.id, 0, 0))
    assert servicio.repo.obtener(a.id).z_index < servicio.repo.obtener(b.id).z_index
    servicio.traer_al_frente(a.id)
    assert servicio.repo.obtener(a.id).z_index > servicio.repo.obtener(b.id).z_index
    servicio.enviar_al_fondo(a.id)
    assert servicio.repo.obtener(a.id).z_index < servicio.repo.obtener(b.id).z_index
    servicio.alternar_bloqueo(a.id)
    assert servicio.repo.obtener(a.id).bloqueado


def test_duplicar_y_revision_y_cambios(servicio, tablero, con):
    e = servicio.crear(nuevo_elemento("dibujo", tablero.id, 0, 0, puntos=[[1, 1], [2, 2]]))
    c = servicio.duplicar(e.id)
    assert c.id != e.id and (c.x, c.y) == (24, 24)
    servicio.mover(e.id, 5, 5)
    assert servicio.repo.obtener(e.id).revision == 1
    ops = [r[0] for r in con.execute("SELECT operacion FROM cambios WHERE elemento_id=?", (e.id,))]
    assert ops == ["crear", "editar"]


def test_campo_no_editable(servicio, tablero):
    e = servicio.crear(nuevo_elemento("nota", tablero.id, 0, 0))
    with pytest.raises(ValueError):
        servicio.modificar(e.id, tipo="lista")


def test_acceso(con):
    s = ServicioAcceso(RepoUsuarios(con))
    assert not s.hay_usuarios()
    s.registrar("Luis", "abcd")
    assert s.hay_usuarios()
    assert s.entrar("luis", "abcd").nombre == "Luis"
    for malo in (("Luis", "x1234"), ("nadie", "abcd")):
        with pytest.raises(ErrorAcceso):
            s.entrar(*malo)
    with pytest.raises(ErrorAcceso):
        s.registrar("Luis", "abcd")
    with pytest.raises(ErrorAcceso):
        s.registrar("L", "abcd")


def test_tableros(con, usuario):
    r = RepoTableros(con, usuario.id)
    a, b = r.crear("Clase"), r.crear("Casa")
    assert {t.nombre for t in r.listar()} == {"Clase", "Casa"}
    assert [t.nombre for t in r.listar("cla")] == ["Clase"]
    r.renombrar(a.id, "Clase 2")
    r.guardar_config(a.id, {"lienzo": "puntos"})
    assert r.obtener(a.id).config == {"lienzo": "puntos"}
    r.eliminar(b.id)
    assert [t.id for t in r.listar_eliminados()] == [b.id]
    r.restaurar(b.id)
    assert len(r.listar()) == 2
    otro = RepoTableros(con, "otro-usuario")
    assert otro.listar() == []


def test_calendario(con, usuario):
    r = RepoCalendario(con, usuario.id)
    ev = r.crear_evento(Evento("", "Reunión", "2026-10-29T09:00", "2026-10-29T10:00", aviso_minutos=15))
    r.crear_evento(Evento("", "Otro día", "2026-11-05T09:00"))
    sem = r.listar_eventos("2026-10-26T00:00", "2026-11-02T00:00")
    assert [e.titulo for e in sem] == ["Reunión"]
    assert r.eventos_por_avisar("2026-10-29T08:40") == []
    assert [e.id for e in r.eventos_por_avisar("2026-10-29T08:50")] == [ev.id]
    r.marcar_notificado(ev.id)
    assert r.eventos_por_avisar("2026-10-29T08:50") == []
    ev.titulo = "Reunión 2"
    r.actualizar_evento(ev)
    cal = r.listar_calendarios()[0]
    r.fijar_visible(cal["id"], False)
    assert r.listar_eventos("2026-10-26T00:00", "2026-11-02T00:00") == []
    r.fijar_visible(cal["id"], True)
    r.eliminar_evento(ev.id)
    assert r.listar_eventos("2026-10-26T00:00", "2026-11-02T00:00") == []


def test_configuracion(con):
    c = RepoConfiguracion(con)
    assert c.obtener("tema", "claro") == "claro"
    c.guardar("tema", "oscuro")
    c.guardar("tema", "claro")
    assert c.obtener("tema") == "claro"


def test_respaldo_e_imagenes(tmp_path, tablero):
    datos = tmp_path / "datos"
    datos.mkdir()
    con = abrir_conexion(datos / "tablero.db")
    from tablero.infraestructura.base_datos.migrador import migrar
    migrar(con)
    u = RepoUsuarios(con).crear("Ana", None)
    t = RepoTableros(con, u.id).crear("T1")
    img = tmp_path / "foto.png"
    img.write_bytes(b"\x89PNG-falso")
    rel = recursos.importar_imagen(con, datos, t.id, img)
    assert (datos / rel).read_bytes() == b"\x89PNG-falso"
    assert recursos.importar_imagen(con, datos, t.id, img) == rel
    assert con.execute("SELECT COUNT(*) FROM recursos").fetchone()[0] == 1
    destino = respaldo.crear_respaldo(con, datos)
    assert destino.exists()
    RepoTableros(con, u.id).eliminar(t.id)
    RepoTableros(con, u.id).crear("T2")
    respaldo.restaurar_respaldo(con, datos, destino)
    assert [x.nombre for x in RepoTableros(con, u.id).listar()] == ["T1"]
    assert con.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


def test_acciones_agrupadas(servicio, tablero):
    a = servicio.crear(nuevo_elemento("nota", tablero.id, 0, 0))
    b = servicio.crear(nuevo_elemento("nota", tablero.id, 10, 10))
    servicio.mover_varios({a.id: (50, 50), b.id: (60, 60)})
    servicio.historial.deshacer()      # UN solo deshacer regresa a los dos
    assert (servicio.repo.obtener(a.id).x, servicio.repo.obtener(b.id).x) == (0, 10)
    servicio.eliminar_varios([a.id, b.id])
    assert servicio.repo.listar(tablero.id) == []
    servicio.historial.deshacer()
    assert len(servicio.repo.listar(tablero.id)) == 2


def test_contexto(tmp_path, con, usuario):
    from tablero.aplicacion.contexto import Contexto
    ctx = Contexto(con, tmp_path, usuario)
    ctx.guardar_widgets_notas([{"id": "1", "texto": "hola"}])
    assert ctx.widgets_notas()[0]["texto"] == "hola"
    assert len(ctx.calendario.listar_calendarios()) == 1


# ---------------------------------------------------------------- acceso con correo y recuperación
def test_registro_con_correo_y_login_por_correo(con):
    s = ServicioAcceso(RepoUsuarios(con))
    u = s.registrar("Marta", "secreto", "Marta@Correo.com", "secreto")
    assert u.correo == "Marta@Correo.com"
    assert s.entrar("marta@correo.com", "secreto").id == u.id      # por correo (sin distinguir mayúsculas)
    assert s.entrar("MARTA", "secreto").id == u.id                 # por nombre de usuario
    with pytest.raises(ErrorAcceso):
        s.registrar("Otra", "secreto", "marta@correo.com")          # correo repetido
    for nombre, clave, correo, conf in (("Ana", "secreto", "no-es-correo", None),
                                        ("Ana", "secreto", "a@b.com", "distinta"),
                                        ("a@b", "secreto", None, None),
                                        ("Ana", "abc", None, None)):
        with pytest.raises(ErrorAcceso):
            s.registrar(nombre, clave, correo, conf)


def test_recuperar_clave(con):
    s = ServicioAcceso(RepoUsuarios(con))
    u = s.registrar("Luis", "vieja123", "luis@correo.com")
    codigo = s.nuevo_codigo_recuperacion(u.id)
    assert len(codigo) == 14 and codigo.count("-") == 2
    with pytest.raises(ErrorAcceso):                                # código incorrecto
        s.recuperar_clave("luis", "AAAA-AAAA-AAAA", "nueva123", "nueva123")
    with pytest.raises(ErrorAcceso):                                # confirmación distinta
        s.recuperar_clave("luis", codigo, "nueva123", "otra")
    # acepta correo o usuario, minúsculas y sin guiones
    usuario, nuevo = s.recuperar_clave("LUIS@correo.com", codigo.lower().replace("-", " "), "nueva123", "nueva123")
    assert usuario.id == u.id and nuevo != codigo
    assert s.entrar("luis", "nueva123").id == u.id
    with pytest.raises(ErrorAcceso):
        s.entrar("luis", "vieja123")
    with pytest.raises(ErrorAcceso):                                # el código usado ya no sirve
        s.recuperar_clave("luis", codigo, "otra1234", "otra1234")
    s.recuperar_clave("luis", nuevo, "tercera1", "tercera1")        # el nuevo sí


def test_recuperar_limita_intentos_y_no_revela_si_existe(con):
    s = ServicioAcceso(RepoUsuarios(con))
    s.registrar("Eva", "clave1", "eva@correo.com")                  # sin código de recuperación (cuenta antigua)
    mensajes = set()
    for _ in range(5):
        with pytest.raises(ErrorAcceso) as e:
            s.recuperar_clave("eva", "AAAA-BBBB-CCCC", "nueva123", "nueva123")
        mensajes.add(str(e.value))
    with pytest.raises(ErrorAcceso) as e:
        s.recuperar_clave("nadie", "AAAA-BBBB-CCCC", "nueva123", "nueva123")
    assert str(e.value) in mensajes                                 # mismo mensaje que usuario real
    with pytest.raises(ErrorAcceso) as e:                           # a la sexta, bloqueo
        s.recuperar_clave("eva", "AAAA-BBBB-CCCC", "nueva123", "nueva123")
    assert "Demasiados intentos" in str(e.value)


def test_migracion_002_conserva_usuarios_existentes(tmp_path):
    from tablero.infraestructura.base_datos import migrador
    c = abrir_conexion(":memory:")
    primera = sorted(migrador.CARPETA.glob("001_*.sql"))[0]
    c.executescript(primera.read_text(encoding="utf-8"))
    c.execute("PRAGMA user_version = 1")
    c.execute("INSERT INTO usuarios (id, nombre, hash_clave, creado_en) VALUES ('1','Vieja',NULL,'x')")
    c.commit()
    migrador.migrar(c)
    assert c.execute("PRAGMA user_version").fetchone()[0] == 2
    assert RepoUsuarios(c).por_nombre("vieja")[0].id == "1"
