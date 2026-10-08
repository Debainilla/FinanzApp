"""Punto de entrada de FinanzApp.

Ejecutar con:

    streamlit run app.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st

RAIZ = Path(__file__).resolve().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src.logica.gasto_servicio import GastoServicio  # noqa: E402
from src.modelos.errores import ErrorPersistencia  # noqa: E402
from src.persistencia.sqlite_repositorio import SqliteRepositorioGastos  # noqa: E402
from src.ui.paginas import render_app  # noqa: E402


def _ruta_base_datos() -> str:
    """Devuelve la ruta de la base de datos.

    Se puede sobreescribir con la variable de entorno ``FINANZAPP_DB``
    (util para pruebas con bases temporales).
    """
    return os.environ.get("FINANZAPP_DB", str(RAIZ / "data" / "finanzapp.db"))


@st.cache_resource(show_spinner=False)
def _crear_repositorio(ruta_db: str) -> SqliteRepositorioGastos:
    """Crea (y cachea) el repositorio SQLite."""
    return SqliteRepositorioGastos(ruta_db)


def main() -> None:
    """Configura la pagina y arranca la interfaz."""
    st.set_page_config(
        page_title="FinanzApp",
        page_icon=":moneybag:",
        layout="wide",
    )

    try:
        repositorio = _crear_repositorio(_ruta_base_datos())
    except ErrorPersistencia as exc:
        st.error(f"No se pudo inicializar la base de datos: {exc}")
        st.stop()

    servicio = GastoServicio(repositorio)
    render_app(servicio)


if __name__ == "__main__":
    main()
