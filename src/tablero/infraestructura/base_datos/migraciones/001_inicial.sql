CREATE TABLE usuarios (
    id          TEXT PRIMARY KEY,
    nombre      TEXT NOT NULL,
    correo      TEXT,
    hash_clave  TEXT,
    creado_en   TEXT NOT NULL
);

CREATE TABLE tableros (
    id              TEXT PRIMARY KEY,
    propietario_id  TEXT REFERENCES usuarios(id),
    nombre          TEXT NOT NULL,
    config_json     TEXT NOT NULL DEFAULT '{}',
    creado_en       TEXT NOT NULL,
    actualizado_en  TEXT NOT NULL,
    eliminado_en    TEXT
);

CREATE TABLE elementos (
    id                  TEXT PRIMARY KEY,
    tablero_id          TEXT NOT NULL REFERENCES tableros(id),
    padre_id            TEXT REFERENCES elementos(id),
    tipo                TEXT NOT NULL,
    x                   REAL NOT NULL DEFAULT 0,
    y                   REAL NOT NULL DEFAULT 0,
    ancho               REAL NOT NULL DEFAULT 200,
    alto                REAL NOT NULL DEFAULT 150,
    z_index             INTEGER NOT NULL DEFAULT 0,
    prioridad_absoluta  INTEGER NOT NULL DEFAULT 0,
    bloqueado           INTEGER NOT NULL DEFAULT 0,
    propiedades         TEXT NOT NULL DEFAULT '{}',
    version_tipo        INTEGER NOT NULL DEFAULT 1,
    creado_por          TEXT REFERENCES usuarios(id),
    creado_en           TEXT NOT NULL,
    actualizado_en      TEXT NOT NULL,
    revision            INTEGER NOT NULL DEFAULT 0,
    eliminado_en        TEXT
);

CREATE INDEX idx_elem_tablero ON elementos(tablero_id, eliminado_en);
CREATE INDEX idx_elem_capa    ON elementos(tablero_id, z_index);

CREATE TABLE recursos (
    id               TEXT PRIMARY KEY,
    tablero_id       TEXT REFERENCES tableros(id),
    nombre_original  TEXT,
    tipo_mime        TEXT,
    ruta_relativa    TEXT NOT NULL,
    hash_sha256      TEXT,
    tamano_bytes     INTEGER
);

CREATE TABLE calendarios (
    id          TEXT PRIMARY KEY,
    usuario_id  TEXT REFERENCES usuarios(id),
    nombre      TEXT NOT NULL,
    color       TEXT,
    visible     INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE eventos_calendario (
    id             TEXT PRIMARY KEY,
    calendario_id  TEXT REFERENCES calendarios(id),
    tablero_id     TEXT REFERENCES tableros(id),
    titulo         TEXT NOT NULL,
    descripcion    TEXT,
    color          TEXT,
    inicio         TEXT NOT NULL,
    fin            TEXT,
    aviso_minutos  INTEGER,
    notificado     INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_evento_inicio ON eventos_calendario(inicio);

CREATE TABLE cambios (
    id            TEXT PRIMARY KEY,
    tablero_id    TEXT NOT NULL REFERENCES tableros(id),
    elemento_id   TEXT REFERENCES elementos(id),
    usuario_id    TEXT REFERENCES usuarios(id),
    operacion     TEXT NOT NULL,
    datos_json    TEXT NOT NULL DEFAULT '{}',
    marca_tiempo  TEXT NOT NULL,
    sincronizado  INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_cambios_pendientes ON cambios(sincronizado, marca_tiempo);

CREATE TABLE configuracion (
    clave  TEXT PRIMARY KEY,
    valor  TEXT
);
