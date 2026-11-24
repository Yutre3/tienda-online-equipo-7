import importlib
import os
from pathlib import Path
import subprocess
import sys


RAIZ = Path(__file__).resolve().parents[1]


def test_main_delega_en_app_sin_duplicar_inicializacion() -> None:
    assert (RAIZ / "main.py").is_file()

    modulo_main = importlib.import_module("main")
    modulo_app = importlib.import_module("app")

    assert modulo_main.main is modulo_app.main


def test_main_y_app_arrancan_el_mismo_flujo_sin_traza(tmp_path) -> None:
    for archivo in ("main.py", "app.py"):
        entorno = os.environ.copy()
        entorno["DB_ENGINE"] = "sqlite"
        entorno["SQLITE_PATH"] = str(tmp_path / f"{archivo}.db")

        resultado = subprocess.run(
            [sys.executable, archivo],
            cwd=RAIZ,
            env=entorno,
            input="",
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )

        assert resultado.returncode == 0, resultado.stderr
        assert "Conexión exitosa" in resultado.stdout
        assert "Ejecución cancelada de forma segura" in resultado.stdout
        assert "Traceback" not in resultado.stderr
