# probar_agentperm.py
# Paso 0 del plan: ¿corre agentperm en esta PC?
#
# Lo que hace, paso a paso:
#   1. Mira qué versión de Python tenés (agentperm pide 3.12 o más).
#   2. Mira en qué sistema estás (Windows, Linux o Mac).
#   3. Instala agentperm en un entorno aparte (no toca tu Python normal).
#   4. Prueba que el programa arranque y que decida bien dos casos:
#      "git status" (tiene que permitir) y "rm -rf /" (tiene que negar).
#   5. Te dice clarito si funciona o si hace falta WSL.
#
# Para correrlo:
#     python probar_agentperm.py
# Necesita internet la primera vez (para descargar agentperm).
# Tarda un par de minutos. No borra ni cambia nada de tu PC.

import os
import platform
import shutil
import subprocess
import sys
import tempfile


def titulo(texto):
    print()
    print("=" * 60)
    print(texto)
    print("=" * 60)


def correr(comando, **opciones):
    """Corre un comando y devuelve (salió_bien, texto_de_salida)."""
    try:
        resultado = subprocess.run(
            comando, capture_output=True, text=True, timeout=240, **opciones
        )
        salida = (resultado.stdout or "") + (resultado.stderr or "")
        return resultado.returncode == 0, salida.strip()
    except FileNotFoundError:
        return False, "No se encontró el programa: " + comando[0]
    except subprocess.TimeoutExpired:
        return False, "Se acabó el tiempo esperando al comando."


def main():
    titulo("PASO 0: ¿corre agentperm en esta PC?")

    # 1) Versión de Python
    version = sys.version_info
    print(f"Python: {version.major}.{version.minor}.{version.micro}")
    if version < (3, 12):
        print("PROBLEMA: agentperm pide Python 3.12 o más.")
        print("Descargá Python 3.12 o más nuevo desde python.org y probá de nuevo.")
        return

    # 2) Sistema operativo
    sistema = platform.system()
    print(f"Sistema: {sistema}")
    if sistema == "Windows":
        print("AVISO: el manual de agentperm dice que solo corre en macOS o Linux.")
        print("En Windows puede que no funcione. Si falla, la salida es usar WSL.")
        print("(WSL es un Linux que vive dentro de Windows.)")
    elif sistema in ("Linux", "Darwin"):
        print("Bien: agentperm dice que corre en este sistema.")

    # 3) Entorno aparte para no tocar tu Python normal
    titulo("Creando un entorno aparte para la prueba...")
    carpeta = tempfile.mkdtemp(prefix="prueba-agentperm-")
    venv = os.path.join(carpeta, "venv")
    ok, salida = correr([sys.executable, "-m", "venv", venv])
    if not ok:
        print("No se pudo crear el entorno virtual:")
        print(salida)
        return
    if sistema == "Windows":
        python_venv = os.path.join(venv, "Scripts", "python.exe")
    else:
        python_venv = os.path.join(venv, "bin", "python")
    print("Entorno creado en:", carpeta)

    # 4) Instalar agentperm
    titulo("Instalando agentperm (esto tarda un poco)...")
    ok, salida = correr([python_venv, "-m", "pip", "install", "--quiet", "agentperm"])
    if not ok:
        print("No se pudo instalar agentperm:")
        print(salida)
        print()
        print("RESULTADO: agentperm NO se pudo instalar en esta PC.")
        if sistema == "Windows":
            print("En Windows, la salida es WSL: instalá Ubuntu desde la tienda")
            print("de Microsoft y corré esto mismo adentro de WSL.")
        return
    print("Instalado.")

    # 5) ¿Arranca el programa?
    titulo("Probando que arranque...")
    agente = python_venv.replace("python", "agentperm")
    if sistema == "Windows":
        agente = os.path.join(venv, "Scripts", "agentperm.exe")
    else:
        agente = os.path.join(venv, "bin", "agentperm")
    ok, salida = correr([agente, "--version"])
    print("Versión:", salida if ok else "no se pudo leer la versión")
    if not ok:
        print("El programa se instaló pero no arranca:")
        print(salida)
        print()
        print("RESULTADO: agentperm NO corre en esta PC.")
        return

    # 6) ¿Decide bien? Creamos una casa temporal para no tocar la tuya.
    titulo("Probando dos decisiones...")
    casa = os.path.join(carpeta, "casa")
    os.makedirs(casa, exist_ok=True)
    entorno = dict(os.environ)
    entorno["HOME"] = casa
    if sistema == "Windows":
        entorno["USERPROFILE"] = casa
    ok, salida = correr([agente, "init"], env=entorno)
    print("init:", "ok" if ok else "falló")
    ok, salida = correr([agente, "validate"], env=entorno)
    print("validate:", salida.splitlines()[0] if salida else "sin salida")
    ok1, s1 = correr([agente, "why", "git status"], env=entorno)
    print("why 'git status' ->", s1.splitlines()[0] if s1 else "?")
    ok2, s2 = correr([agente, "why", "rm -rf /"], env=entorno)
    print("why 'rm -rf /' ->", s2.splitlines()[0] if s2 else "?")

    titulo("RESULTADO")
    if ok1 and ok2 and "allow" in s1.lower() and "deny" in s2.lower():
        print("agentperm FUNCIONA en esta PC.")
        print("Permitió 'git status' y negó 'rm -rf /', como tiene que ser.")
    else:
        print("agentperm se instaló y arrancó, pero las decisiones no salieron")
        print("como se esperaba. Revisá la salida de arriba.")
        if sistema == "Windows":
            print("Si estás en Windows, probá adentro de WSL.")

    print()
    print("La prueba quedó en:", carpeta)
    print("Podés borrar esa carpeta cuando quieras, no hace falta.")
    print("Tu Python normal no se tocó.")


if __name__ == "__main__":
    main()
