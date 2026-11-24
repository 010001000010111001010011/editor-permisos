# Editor de permisos para agentes de IA — v1 (proyecto de aprendizaje)

Esto es la **opción 1** del plan: una página para decidir con tildes qué puede
hacer un agente de IA (Claude Code) antes de que arranque. Es un proyecto para
**aprender Python**, no la apuesta principal de plata (esa sigue siendo
Turnos al Calendario). Todo corre en tu PC, sin cuentas, sin claves y sin
subir nada a internet.

## Qué hace esta versión (pasos 0 y 1 del plan)

- **Paso 0:** `probar_agentperm.py` prueba si `agentperm` (el motor que une
  a varios agentes) corre en tu PC.
- **Paso 1:** `editor_permisos.py` + `pagina.html` son el editor visual:
  tres columnas (**Permitir / Preguntar / Negar**), presets
  (**Seguro / Equilibrado / Libre**), y guarda los cambios en un
  `settings.json` real, el archivo que lee Claude Code. Antes de guardar,
  revisa que el JSON esté bien y te avisa si una regla está repetida entre
  listas.

## Resultado del paso 0 (verificado el 24/11/2026)

- `agentperm` **sí funciona en Linux**: se instaló con `pip` (versión 0.4.0,
  más nueva que la 0.3.0 del plan), arrancó, creó su archivo de reglas,
  permitió `git status` y negó `rm -rf /`, como tiene que ser.
- En **Windows no corre de forma oficial**: su manual dice
  "Python 3.12+, macOS or Linux" y en PyPI solo lista macOS y Linux.
  En tu PC con Windows, la salida es **WSL** (un Linux que vive dentro de
  Windows) para el paso 2. La v1 no necesita agentperm: usa el
  `settings.json` nativo de Claude Code, que sí corre en Windows.

## Archivos

| Archivo | Qué hace | Qué aprendés de él |
|---|---|---|
| `editor_permisos.py` | El servidor: sirve la página y guarda `settings.json` | `http.server`, `json`, funciones, `try/except`, diccionarios y listas |
| `pagina.html` | La página con las 3 columnas y los presets | Cómo una página habla con Python (fetch, JSON) |
| `settings.json` | Ejemplo real de permisos (preset Equilibrado) | El formato que usa Claude Code |
| `probar_agentperm.py` | Prueba del paso 0 | `subprocess`, entornos virtuales, `platform`, `tempfile` |
| `ejecutar.bat` | Doble clic para arrancar el editor en Windows | — |
| `README.md` | Este archivo | — |

## Cómo correrlo en Windows

1. Instalá **Python 3.12 o más nuevo** desde python.org. Cuando lo instales,
   marcá la casilla **"Add python.exe to PATH"**.
2. Descomprimí esta carpeta donde quieras (por ejemplo en el Escritorio).
3. Hacé **doble clic en `ejecutar.bat`**.
4. Abrí el navegador en **http://localhost:8000**.
5. Para pararlo, cerrá la ventana negra o apretá **Ctrl + C**.

Si preferís la terminal: `python editor_permisos.py` en la carpeta.

## Cómo usarlo

1. Elegí un preset (**Seguro**, **Equilibrado** o **Libre**) o editá las
   reglas a mano: cada regla dice abajo, en palabras simples, qué significa.
2. Agregá reglas nuevas con el cuadrito de cada columna, o quitalas con
   el botón **Quitar**.
3. Apretá **Guardar en settings.json**.
4. Para usarlo con Claude Code, copiá el `settings.json` de esta carpeta a
   tu carpeta `.claude` (en Windows:
   `C:\Users\TU_USUARIO\.claude\settings.json`).

## La regla de oro (cómo decide Claude Code)

Las tres listas se revisan en este orden:

1. **Negar** — si la regla está acá, el agente NO puede hacerlo. Gana siempre.
2. **Preguntar** — el agente te pregunta antes de hacerlo.
3. **Permitir** — el agente lo hace sin preguntar.

Por eso lo peligroso (borrar archivos, `sudo`, subir cambios, leer tus
claves de `.env`) va en **Negar**. El editor te avisa si ponés la misma
regla en dos listas.

## Qué NO hace todavía (pasos 2, 3 y 4, a propósito)

- No conecta agentperm todavía (eso es el paso 2, cuando corra en WSL).
- No hay registro vivo de lo que el agente intentó hacer (paso 3).
- No hay versión para equipos ni nube (paso 4).
- No es un sandbox: decide permitir/preguntar/negar, no encierra lo que corre.

## El dato que lo empezó todo

El equipo de Anthropic encontró que los desarrolladores aprueban el **93%**
de los pedidos de permiso de Claude Code sin revisarlos con cuidado. Esta
herramienta existe para que esa decisión se tome antes, con calma, y no
apretando "sí" a todo en el momento.
