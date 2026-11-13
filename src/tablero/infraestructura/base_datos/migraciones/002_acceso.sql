-- Acceso: código de recuperación (solo su hash) y correo único por usuario.
ALTER TABLE usuarios ADD COLUMN hash_recuperacion TEXT;

CREATE UNIQUE INDEX idx_usuarios_correo
    ON usuarios(correo COLLATE NOCASE)
    WHERE correo IS NOT NULL AND correo <> '';
