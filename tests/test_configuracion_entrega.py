import json
from pathlib import Path
import subprocess


RAIZ = Path(__file__).resolve().parents[1]


def _leer_env_ejemplo() -> dict[str, str]:
    valores: dict[str, str] = {}
    for linea in (RAIZ / ".env.example").read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if linea and not linea.startswith("#"):
            clave, valor = linea.split("=", 1)
            valores[clave] = valor
    return valores


def test_dependencias_declaran_stack_del_profesor_y_pruebas() -> None:
    paquetes = {
        linea.split("==", 1)[0].lower()
        for linea in (RAIZ / "requirements.txt").read_text(encoding="utf-8").splitlines()
        if linea.strip()
    }

    assert paquetes == {
        "peewee",
        "pymysql",
        "python-decouple",
        "prettytable",
        "pytest",
    }


def test_configuracion_de_ejemplo_usa_usuario_limitado() -> None:
    valores = _leer_env_ejemplo()

    assert valores["DB_NAME"] == "tienda_online"
    assert valores["DB_USER"] == "tienda_app"
    assert valores["DB_USER"].lower() != "root"
    assert valores["DB_PASSWORD"] == "CAMBIAR_CLAVE_ANTES_DE_USAR"


def test_configuracion_vscode_es_json_valido_y_ofrece_tareas_clave() -> None:
    tareas = json.loads((RAIZ / ".vscode/tasks.json").read_text(encoding="utf-8"))
    ajustes = json.loads((RAIZ / ".vscode/settings.json").read_text(encoding="utf-8"))
    extensiones = json.loads((RAIZ / ".vscode/extensions.json").read_text(encoding="utf-8"))

    etiquetas = {tarea["label"] for tarea in tareas["tasks"]}
    assert {"Preparar proyecto", "Ejecutar pruebas", "Ejecutar tienda"} <= etiquetas
    assert ajustes["sqltools.connections"][0]["username"] == "tienda_app"
    assert "ms-python.python" in extensiones["recommendations"]
    assert "mtxr.sqltools-driver-mysql" in extensiones["recommendations"]


def test_scripts_sql_cubren_esquema_usuario_y_datos() -> None:
    carpeta = RAIZ / "datos/sql"
    ddl = (carpeta / "2026.10.05_20.00_DDL_Tienda_Online.sql").read_text(encoding="utf-8")
    usuario = (carpeta / "2026.10.20_20.10_CREATE_USER.sql").read_text(encoding="utf-8")
    datos = (carpeta / "2026.10.20_20.20_DATOS_EJEMPLO.sql").read_text(encoding="utf-8")

    for tabla in ("clientes", "productos", "pedidos", "detalles_pedido"):
        assert f"CREATE TABLE IF NOT EXISTS {tabla}" in ddl
    assert "'tienda_app'@'localhost'" in usuario
    assert "GRANT SELECT, INSERT, UPDATE, DELETE" in usuario
    assert "INSERT INTO clientes" in datos
    assert "INSERT INTO productos" in datos


def test_archivos_locales_y_secretos_estan_ignorados() -> None:
    if not (RAIZ / ".git").exists():
        assert not any(
            (RAIZ / ruta).exists()
            for ruta in (".env", ".venv", "tienda.db", "entrega.zip")
        )
        return
    resultado = subprocess.run(
        ["git", "check-ignore", ".env", ".venv/prueba", "tienda.db", "entrega.zip"],
        cwd=RAIZ,
        capture_output=True,
        text=True,
        check=False,
    )

    assert resultado.returncode == 0
    assert set(resultado.stdout.splitlines()) == {
        ".env",
        ".venv/prueba",
        "tienda.db",
        "entrega.zip",
    }


def test_documentacion_de_entrega_existe() -> None:
    assert (RAIZ / "README.md").stat().st_size > 3000
    assert (RAIZ / "docs/DIAGRAMA_UML.md").stat().st_size > 1000
