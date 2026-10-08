"""Orquestacion de la interfaz de FinanzApp."""

from __future__ import annotations

import streamlit as st

from src.logica.gasto_servicio import GastoServicio
from src.modelos.errores import ErrorValidacion

from . import componentes


def render_app(servicio: GastoServicio) -> None:
    """Dibuja la aplicacion completa.

    Los filtros se calculan una sola vez y el resultado se comparte entre
    la tabla (R2) y la grafica (R4), garantizando que ambos usen los
    mismos datos.
    """
    componentes.mostrar_encabezado()
    componentes.mostrar_mensajes_flash()

    filtro = componentes.panel_filtros()
    try:
        datos = servicio.listar_gastos(filtro)
    except ErrorValidacion as exc:
        st.error(f"Filtro invalido: {exc}")
        datos = []

    tab_registrar, tab_consultar, tab_grafica = st.tabs(
        ["Registrar gasto", "Consultar / Editar / Eliminar", "Grafica"]
    )

    with tab_registrar:
        componentes.seccion_registrar(servicio)
    with tab_consultar:
        componentes.seccion_consultar(servicio, datos, filtro)
    with tab_grafica:
        componentes.seccion_grafica(datos)
