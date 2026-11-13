# MichiNotes — Tablero Digital

Aplicación de escritorio **offline** para organizar ideas en tableros visuales: notas, listas, enlaces, texto, figuras, dibujo a mano alzada e imágenes sobre un lienzo infinito, más un calendario semanal con avisos y widgets de notas que se quedan en el escritorio.

Proyecto de **Prácticas II**. Desarrollado en **Python + PySide6 (Qt) + SQLite**. No necesita internet ni servidores: todo se guarda en el computador del usuario.

---

## Contenido

1. [Características](#características)
2. [Requisitos](#requisitos)
3. [Instalación](#instalación)
   - [Opción A — Usar el ejecutable (usuario final, Windows)](#opción-a--usar-el-ejecutable-usuario-final-windows)
   - [Opción B — Ejecutar desde el código fuente (Windows, Linux, macOS)](#opción-b--ejecutar-desde-el-código-fuente-windows-linux-macos)
   - [Opción C — Generar el ejecutable `.exe` (Windows)](#opción-c--generar-el-ejecutable-exe-windows)
4. [Primer uso](#primer-uso)
5. [Guía rápida de uso](#guía-rápida-de-uso)
6. [Atajos de teclado](#atajos-de-teclado)
7. [Dónde se guardan los datos y respaldos](#dónde-se-guardan-los-datos-y-respaldos)
8. [Pruebas automáticas](#pruebas-automáticas)
9. [Estructura del proyecto](#estructura-del-proyecto)
10. [Tecnologías](#tecnologías)
11. [Solución de problemas](#solución-de-problemas)

---

## Características

**Cuenta y acceso**
- Crear cuenta con nombre de usuario, correo y contraseña.
- Iniciar sesión con **correo o nombre de usuario**.
- Recuperar la contraseña con un **código de recuperación** de un solo uso (se muestra al crear la cuenta; funciona sin conexión).
- Las contraseñas se guardan cifradas (hash con Argon2); nunca en texto plano.
- Cerrar sesión y entrar con otro usuario sin cerrar la aplicación.

**Panel de tableros**
- Crear, buscar, renombrar y eliminar tableros.
- Los tableros eliminados van a una papelera de la que se pueden restaurar.

**Lienzo del tablero**
- Zoom y desplazamiento; fondo con cuadrícula, puntos o liso.
- **Notas**, **listas con casillas**, **enlaces** y **texto** con formato (fuente, tamaño, negrita, cursiva, subrayado, alineación).
- **Figuras** (con rotación a 90° o libre).
- **Pincel** con 4 tipos de trazo (duro redondo, resaltador, suave texturizado y óleo) y **borrador**.
- **Imágenes** importadas desde el computador.
- Capas (traer al frente / enviar al fondo), bloquear, duplicar y eliminar elementos.
- **Deshacer / rehacer** (hasta 200 pasos) y **papelera** de elementos por tablero.

**Calendario**
- Vista semanal por horas, mini calendario y varios calendarios con color.
- Eventos con título, descripción, fecha, hora de inicio y fin, color y **tablero asociado**.
- **Avisos** (5 min, 15 min, 30 min, 1 hora o 1 día antes) mediante notificación del sistema.

**Widgets de escritorio**
- Notas adhesivas siempre visibles, sin bordes, que recuerdan su texto y su posición.

**Respaldo**
- Guardar una copia de toda la información en un archivo `.db` y restaurarla cuando se necesite (incluye las imágenes importadas).

---

## Requisitos

| | Ejecutable (Opción A) | Código fuente (Opciones B y C) |
|---|---|---|
| Sistema operativo | Windows 10 u 11 (64 bits) | Windows 10/11, Linux o macOS |
| Python | No hace falta | **3.10 o superior** (3.11–3.13 recomendado) |
| Internet | No | Solo durante la instalación de librerías |
| Espacio en disco | ≈ 150 MB | ≈ 600 MB (entorno virtual + librerías) |

Librerías de Python (en `requirements.txt`): `PySide6`, `argon2-cffi`, `pytest`.

---

## Instalación

### Opción A — Usar el ejecutable (usuario final, Windows)

Es la forma más simple: no hay que instalar Python ni nada más.

1. Obtenga el archivo **`MichiNotes.exe`** (se genera con la Opción C; está en la carpeta `dist`).
2. Cópielo a la carpeta que prefiera (Escritorio, Documentos, un USB…).
3. Haga **doble clic** sobre `MichiNotes.exe`.

> **Aviso de Windows (SmartScreen):** como el programa no está firmado digitalmente, Windows puede mostrar "Windows protegió su PC". Pulse **Más información → Ejecutar de todas formas**. Solo ocurre la primera vez.

> **Importante:** el `.exe` es portable, no es un instalador. No crea accesos directos ni entradas en "Programas". Si desea un acceso directo, haga clic derecho sobre el `.exe` → *Enviar a → Escritorio (crear acceso directo)*.

Los datos del usuario **no** quedan junto al `.exe`, sino en su carpeta personal de Windows (ver [Dónde se guardan los datos](#dónde-se-guardan-los-datos-y-respaldos)). Por eso puede mover o actualizar el `.exe` sin perder información.

### Opción B — Ejecutar desde el código fuente (Windows, Linux, macOS)

1. **Instale Python 3.10 o superior** desde <https://www.python.org/downloads/>.
   En Windows, durante la instalación marque la casilla **"Add python.exe to PATH"**.
2. **Abra una terminal** dentro de la carpeta del proyecto (la que contiene `main.py`).
3. **Cree un entorno virtual** (una "caja" aislada para las librerías del proyecto):

   ```
   python -m venv .venv
   ```
4. **Actívelo:**

   ```
   .venv\Scripts\activate          # Windows (CMD o PowerShell)
   source .venv/bin/activate       # Linux / macOS
   ```
   Verá `(.venv)` al inicio de la línea de la terminal.
5. **Instale las librerías:**

   ```
   pip install -r requirements.txt
   ```
6. **Inicie la aplicación:**

   ```
   python main.py
   ```

Para volver a abrirla otro día solo repita los pasos 2, 4 y 6 (el entorno y las librerías ya quedaron instalados).

> En PowerShell, si el paso 4 muestra un error de "ejecución de scripts deshabilitada", ejecute una vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` o use CMD en su lugar.

> En Linux, si la ventana no abre y aparece un error sobre `xcb`, instale las librerías del sistema que usa Qt: `sudo apt install libxcb-cursor0 libxkbcommon-x11-0`.

### Opción C — Generar el ejecutable `.exe` (Windows)

Sirve para entregar la aplicación a otras personas sin que tengan que instalar Python. Requiere Python 3.10+ instalado (paso 1 de la Opción B).

1. Abra la carpeta del proyecto.
2. Haga **doble clic en `construir_exe.bat`**.
3. El script hace todo solo (tarda unos minutos):
   1. crea el entorno virtual,
   2. instala las librerías y PyInstaller,
   3. genera el ejecutable,
   4. verifica que exista y abre la carpeta de resultado.
4. El archivo final queda en **`dist\MichiNotes.exe`**. Ese es el único archivo que hay que entregar.

Equivalente manual, con el entorno virtual activo:

```
pip install pyinstaller
pyinstaller --noconfirm --clean MichiNotes.spec
```

Si el `.exe` no abre y necesita ver el error, ejecute `construir_exe.bat debug`: genera `dist\MichiNotes_debug.exe`, que muestra una consola con los mensajes.

---

## Primer uso

1. Al abrir la aplicación aparece la pantalla de acceso. Pulse **"¿No tiene cuenta? Crear cuenta"**.
2. Escriba **nombre de usuario** (mínimo 2 caracteres, sin «@»), **correo**, **contraseña** (mínimo 4 caracteres) y su confirmación.
3. Se muestra el **código de recuperación**. **Anótelo o cópielo** ("Copiar código") y guárdelo en un lugar seguro: es la única forma de restablecer la contraseña si la olvida. Al usarlo se genera uno nuevo.
4. Pulse **Continuar**: entra al panel de tableros.

En los siguientes usos basta con escribir correo o usuario y contraseña, y pulsar **Ingresar**.

**¿Olvidó la contraseña?** En la pantalla de acceso pulse "¿olvidó su contraseña?", escriba su usuario o correo, el código de recuperación y la nueva contraseña.

---

## Guía rápida de uso

**Barra superior:** *Tableros* (panel de trabajo) · *Tablero actual* · *Calendario* · *Menú*.

**Tableros**
1. En *Tableros* pulse **Nuevo tablero**, escriba un nombre y se abrirá.
2. Para abrir uno existente, haga **doble clic** sobre él. Puede filtrarlos con el buscador.
3. **Renombrar**, **Eliminar** y **Eliminados** (papelera, para restaurar) están en la misma barra.

**Dentro de un tablero**
- La barra de herramientas permite elegir: seleccionar, mano, notas, pincel, borrador, figuras, imagen y texto. Al elegir una herramienta aparece a la derecha su panel de opciones (color, tipo, tamaño, etc.).
- **Notas / listas / enlaces:** elija el tipo y el color, y haga clic en el lienzo para crearla. Doble clic para editarla. También puede hacer **doble clic en un espacio vacío** para crear una nota rápida.
- **Clic derecho** sobre un elemento: menú con editar, girar, duplicar, traer al frente, enviar al fondo, bloquear y eliminar (a la papelera).
- **Lienzo:** con nada seleccionado, el panel *Lienzo* permite cambiar entre cuadrícula, puntos o liso, y el color de fondo.
- **Papelera del tablero:** los elementos eliminados se pueden restaurar, borrar para siempre o vaciar.
- Todo se guarda automáticamente.

**Calendario**
- **Evento** (o doble clic en una celda de hora) abre el formulario del evento; ahí se elige calendario, aviso, color y tablero asociado.
- Use las flechas y **Hoy** para moverse entre semanas, o el mini calendario para saltar a una fecha.
- **Nuevo calendario** crea calendarios adicionales (por ejemplo "Estudio", "Personal").
- Los avisos llegan como notificación del sistema mientras la aplicación esté abierta.

**Widgets de escritorio**
- *Menú → Nuevo Widget* crea una nota adhesiva flotante. Se arrastra desde cualquier punto, guarda su texto sola y se cierra con la **X**. Al volver a abrir la aplicación reaparecen donde quedaron.

**Menú (☰)**

| Opción | Qué hace |
|---|---|
| Panel de trabajo | Ir a la lista de tableros |
| Calendario | Ir al calendario |
| Nuevo Widget | Crear una nota de escritorio |
| Guardar | Crear un respaldo de toda la información |
| Restaurar guardado | Reemplazar la información actual por la de un respaldo |
| Atajos de teclado | Mostrar la lista de atajos |
| Cerrar sesión | Volver a la pantalla de acceso |
| Salir | Cerrar la aplicación |

---

## Atajos de teclado

| Atajo | Acción |
|---|---|
| `V` | Seleccionar |
| `H` | Mano (mover la vista sin tocar elementos) |
| `N` | Notas |
| `B` | Pincel |
| `E` | Borrador |
| `S` | Figuras |
| `I` | Imagen |
| `T` | Texto |
| `Esc` | Quitar selección y volver a Seleccionar |
| `Ctrl + Z` | Deshacer |
| `Ctrl + Y` / `Ctrl + Shift + Z` | Rehacer |
| `Ctrl + D` | Duplicar |
| `Supr` / `Retroceso` | Eliminar lo seleccionado |
| `Ctrl + A` | Seleccionar todo |
| `Ctrl + rueda del mouse` | Zoom |
| `Ctrl + 0` | Zoom al 100 % |
| Botón central del mouse (arrastrar) | Mover el lienzo |
| `R` / `Shift + R` | Girar la figura 90° (derecha / izquierda) |
| Arrastrar el círculo sobre una figura | Girar libremente (con `Shift`, de 15° en 15°) |

Las teclas de herramienta no se activan mientras se escribe dentro de un cuadro de texto.

---

## Dónde se guardan los datos y respaldos

La información **no** está dentro de la carpeta del programa. Se guarda en la carpeta de datos de la aplicación de cada usuario del sistema:

| Sistema | Carpeta |
|---|---|
| Windows | `%APPDATA%\MichiNotes\` (escriba eso en la barra de direcciones del Explorador) |
| Linux | `~/.local/share/MichiNotes/` |
| macOS | `~/Library/Application Support/MichiNotes/` |

Dentro está `tablero.db` (base de datos SQLite con usuarios, tableros, elementos, calendario y configuración) y la carpeta `recursos/` con las imágenes importadas. Si no encuentra el archivo, revise si dentro de esa carpeta hay otra subcarpeta `MichiNotes`.

**Hacer un respaldo:** *Menú → Guardar* → elija dónde guardar el archivo `.db`. Junto a él se crea una carpeta `<nombre>_recursos` con las imágenes. **Guarde ambos juntos.**

**Restaurar un respaldo:** *Menú → Restaurar guardado* → elija el `.db` (con su carpeta `_recursos` al lado). Esto **reemplaza todo** el contenido actual por el del respaldo; la aplicación pide confirmación antes.

**Pasar la información a otro computador:** haga un respaldo, copie el `.db` y su carpeta `_recursos` al otro equipo, abra MichiNotes allí, cree una cuenta cualquiera y use *Restaurar guardado*.

**Desinstalar:** elimine `MichiNotes.exe` (o la carpeta del proyecto). Si además quiere borrar toda la información, elimine la carpeta de datos indicada arriba.

---

## Pruebas automáticas

Las pruebas verifican la base de datos y los servicios sin abrir ninguna ventana. Con el entorno virtual activo:

```
pytest -q
```

Resultado esperado: `20 passed`.

---

## Estructura del proyecto

```
MichiNotes/
├── main.py                  Punto de entrada
├── requirements.txt         Librerías necesarias
├── MichiNotes.spec          Configuración de PyInstaller
├── construir_exe.bat        Genera dist\MichiNotes.exe en Windows
├── recursos/                Iconos, logo, imagen de acceso y fuente Dongle
├── tests/                   Pruebas automáticas (pytest)
└── src/tablero/
    ├── config.py            Rutas y carpeta de datos
    ├── dominio/             Entidades puras: usuario, tablero, elementos, calendario
    ├── aplicacion/          Casos de uso: servicios, comandos (deshacer/rehacer), bus de eventos
    ├── infraestructura/     SQLite, migraciones, repositorios, seguridad (hash) y respaldos
    └── presentacion/        Interfaz Qt: login, panel de tableros, lienzo, calendario, widgets
```

La arquitectura está separada en capas: la interfaz (`presentacion`) llama a los casos de uso (`aplicacion`), que trabajan con entidades (`dominio`) y guardan mediante repositorios (`infraestructura`). La base de datos se crea y actualiza sola al abrir la aplicación mediante los scripts de `infraestructura/base_datos/migraciones/`.

---

## Tecnologías

- **Python 3.10+**
- **PySide6** (Qt for Python): interfaz gráfica, lienzo (`QGraphicsScene`), bandeja del sistema.
- **SQLite**: base de datos local en un único archivo.
- **argon2-cffi**: cifrado de contraseñas.
- **pytest**: pruebas automáticas.
- **PyInstaller**: empaquetado como ejecutable de Windows.
- Fuente **Dongle** e iconos **Phosphor** incluidos en `recursos/`.

---

## Solución de problemas

| Problema | Solución |
|---|---|
| `python` no se reconoce como comando | Reinstale Python marcando **"Add python.exe to PATH"**, o use `py -3` en lugar de `python` en Windows. |
| `pip install` falla por falta de internet o proxy | La instalación de librerías necesita conexión; conéctese y repita el comando. |
| Windows bloquea el `.exe` | Pulse *Más información → Ejecutar de todas formas*. |
| El `.exe` no abre y no muestra nada | Genere la versión con consola: `construir_exe.bat debug`, ábrala y lea el mensaje de error. |
| Olvidé la contraseña y perdí el código de recuperación | No hay forma de recuperarla desde la aplicación (no usa servidor de correo). Cree una cuenta nueva; los datos de la cuenta anterior no se pueden abrir con ella. |
| No llegan los avisos del calendario | La aplicación debe estar abierta, y las notificaciones de Windows activadas (*Configuración → Sistema → Notificaciones*). Si el sistema no tiene bandeja, el aviso aparece como ventana emergente. |
| Las imágenes no aparecen tras restaurar un respaldo | Falta la carpeta `<nombre>_recursos` junto al `.db`; debe estar en la misma carpeta que el archivo restaurado. |
| Error `xcb` al abrir en Linux | `sudo apt install libxcb-cursor0 libxkbcommon-x11-0` |
