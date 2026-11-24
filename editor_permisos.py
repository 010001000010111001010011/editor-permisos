# editor_permisos.py
# Servidor local para editar los permisos de Claude Code con una página web.
# Solo usa la biblioteca estándar de Python: no hay nada que instalar.
#
# Para correrlo:
#     python editor_permisos.py
# Después abrí en el navegador:
#     http://localhost:8000
# Para pararlo: Ctrl + C en la terminal.
#
# Qué hace: sirve la página (pagina.html) y guarda los cambios en
# settings.json, que es el archivo real que lee Claude Code.
# Todo queda en tu PC: nada se sube a internet, no hay cuentas ni claves.

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# --- Ajustes del programa (cambialos si querés) ---
PUERTO = 8000
ARCHIVO_AJUSTES = "settings.json"   # el archivo que editamos
ARCHIVO_PAGINA = "pagina.html"      # la página que ve el usuario

# Herramientas de Claude Code que conocemos.
# Si escribís una regla con otra herramienta, te avisamos (no es error,
# solo un aviso para que revises que esté bien escrita).
HERRAMIENTAS_CONOCIDAS = [
    "Read", "Edit", "Write", "Glob", "Grep", "Bash", "BashOutput",
    "KillShell", "WebFetch", "WebSearch", "TodoWrite", "Task",
    "NotebookEdit", "SlashCommand",
]

# Las tres listas de permisos, en el orden en que Claude Code las revisa.
# "deny" gana siempre: si una regla está en Negar y en Permitir, gana Negar.
LISTAS = ("allow", "ask", "deny")


def ruta_de(nombre):
    """Devuelve la ruta completa de un archivo de esta carpeta."""
    carpeta = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(carpeta, nombre)


def leer_ajustes():
    """Lee settings.json y lo devuelve como un diccionario de Python.
    Si el archivo no existe, devuelve permisos vacíos.
    Si el archivo está roto, lanza ValueError con el problema."""
    ruta = ruta_de(ARCHIVO_AJUSTES)
    if not os.path.exists(ruta):
        return {"permissions": {"allow": [], "ask": [], "deny": []}}
    with open(ruta, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)
    if not isinstance(datos, dict):
        raise ValueError("settings.json no es un objeto JSON válido.")
    return datos


def limpiar_lista(lista):
    """Quita espacios, borra reglas vacías y repetidas, sin cambiar el orden."""
    vistas = set()
    limpia = []
    for regla in lista:
        regla = regla.strip()
        if not regla or regla in vistas:
            continue
        vistas.add(regla)
        limpia.append(regla)
    return limpia


def validar_permisos(permisos):
    """Revisa las tres listas de permisos.
    Devuelve (avisos, permisos_limpios).
    Si algo está muy mal, lanza ValueError con el problema en español."""
    if not isinstance(permisos, dict):
        raise ValueError("'permissions' tiene que ser un objeto con allow, ask y deny.")

    avisos = []
    limpios = {}

    # 1) Cada lista tiene que ser una lista de textos.
    for nombre in LISTAS:
        valor = permisos.get(nombre, [])
        if not isinstance(valor, list):
            raise ValueError(f"'{nombre}' tiene que ser una lista de reglas.")
        for regla in valor:
            if not isinstance(regla, str):
                raise ValueError(f"En '{nombre}' hay una regla que no es texto: {regla!r}.")
        limpios[nombre] = limpiar_lista(valor)

    # 2) Reglas repetidas entre listas: gana Negar, después Preguntar.
    for regla in limpios["deny"]:
        if regla in limpios["allow"]:
            avisos.append(
                f"La regla '{regla}' está en Negar y en Permitir: gana Negar, "
                "el agente NO podrá hacerlo."
            )
        if regla in limpios["ask"]:
            avisos.append(
                f"La regla '{regla}' está en Negar y en Preguntar: gana Negar, "
                "el agente NO podrá hacerlo."
            )
    for regla in limpios["ask"]:
        if regla in limpios["allow"]:
            avisos.append(
                f"La regla '{regla}' está en Preguntar y en Permitir: gana Preguntar, "
                "el agente pedirá permiso antes de hacerlo."
            )

    # 3) Herramientas que no conocemos: aviso, no error.
    for nombre in LISTAS:
        for regla in limpios[nombre]:
            herramienta = regla.split("(", 1)[0]
            if herramienta not in HERRAMIENTAS_CONOCIDAS and not herramienta.startswith("mcp__"):
                avisos.append(
                    f"En '{nombre}' la regla '{regla}' usa una herramienta "
                    f"que no conozco ('{herramienta}'). Revisá que esté bien escrita."
                )

    return avisos, limpios


def guardar_ajustes(datos_nuevos):
    """Valida los datos nuevos y los guarda en settings.json.
    No borra las otras claves del archivo (por ejemplo "model"):
    solo reemplaza "permissions". Devuelve la lista de avisos."""
    permisos = datos_nuevos.get("permissions", {})
    avisos, limpios = validar_permisos(permisos)

    # Leo lo que ya hay en el archivo para no perder otras claves.
    try:
        datos_viejos = leer_ajustes()
    except ValueError:
        datos_viejos = {}
    datos_viejos["permissions"] = limpios

    ruta = ruta_de(ARCHIVO_AJUSTES)
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos_viejos, archivo, indent=2, ensure_ascii=False)
        archivo.write("\n")
    return avisos


class Manejador(BaseHTTPRequestHandler):
    """Atiende cada pedido del navegador. Solo hay 3 direcciones:
    /              -> la página
    /api/ajustes  -> leer (GET) o guardar (POST) los permisos"""

    def _responder_json(self, codigo, datos):
        cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_GET(self):
        if self.path == "/" or self.path == "/pagina.html":
            with open(ruta_de(ARCHIVO_PAGINA), "rb") as archivo:
                contenido = archivo.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(contenido)))
            self.end_headers()
            self.wfile.write(contenido)
        elif self.path == "/api/ajustes":
            try:
                datos = leer_ajustes()
            except ValueError as error:
                self._responder_json(500, {"ok": False, "error": str(error)})
                return
            self._responder_json(200, {"ok": True, "datos": datos})
        else:
            self._responder_json(404, {"ok": False, "error": "No existe esa dirección."})

    def do_POST(self):
        if self.path != "/api/ajustes":
            self._responder_json(404, {"ok": False, "error": "No existe esa dirección."})
            return
        largo = int(self.headers.get("Content-Length", 0))
        cuerpo = self.rfile.read(largo)
        try:
            datos = json.loads(cuerpo.decode("utf-8"))
        except json.JSONDecodeError:
            self._responder_json(400, {"ok": False, "error": "Lo que llegó no es JSON válido."})
            return
        if not isinstance(datos, dict):
            self._responder_json(400, {"ok": False, "error": "Los datos tienen que ser un objeto JSON."})
            return
        try:
            avisos = guardar_ajustes(datos)
        except ValueError as error:
            self._responder_json(400, {"ok": False, "error": str(error)})
            return
        self._responder_json(200, {"ok": True, "avisos": avisos})

    def log_message(self, formato, *args):
        # Mensajes cortos en la terminal, sin tanto ruido.
        print("  " + formato % args)


if __name__ == "__main__":
    servidor = ThreadingHTTPServer(("127.0.0.1", PUERTO), Manejador)
    print("Editor de permisos corriendo en http://localhost:8000")
    print("Solo se ve desde tu PC. Pará con Ctrl + C.")
    servidor.serve_forever()
