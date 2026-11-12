# Tablero Digital (versión funcional básica)

App de escritorio offline: Python + PySide6 + SQLite.

## Ejecutar
```
python -m venv .venv
.venv\Scripts\activate        # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
python main.py
```
La primera vez crea tu usuario. Los datos quedan en la carpeta de datos del usuario
(menú ☰ → "Abrir carpeta de datos"), no en el proyecto.

## Pruebas (sin interfaz)
`pytest -q`

## Qué incluye
Login · panel de tableros (crear/buscar/renombrar/eliminar/restaurar) · lienzo con zoom y cuadrícula/puntos/liso ·
notas, listas con casillas, enlaces, texto, figuras, pincel (4 tipos), borrador, imágenes · formato de texto ·
capas (frente/fondo), bloqueo, duplicar · papelera + deshacer/rehacer · calendario semanal con avisos ·
widget de notas de escritorio · respaldo/restauración.

## Por incluir
vinculacion de usuario y panel de usuario (cambio de contraseña, nombre de usuario)
conectores entre figuras
figuras personalizadas
recorte de imágenes
instalador (.exe)


## Estructura
`src/tablero/dominio` datos puros · `aplicacion` casos de uso (comandos, servicios) ·
`infraestructura` SQLite/respaldo · `presentacion` ventanas Qt.
