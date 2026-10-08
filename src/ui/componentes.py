"""Componentes de interfaz (Streamlit) de FinanzApp.

Todas las funciones de este modulo se ocupan solo de presentar datos y
capturar entradas. La logica de negocio vive en ``src.logica`` y el
acceso a datos en ``src.persistencia``; aqui nunca se importa ``sqlite3``.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from src.logica.estadisticas import EstadisticasGastos
from src.logica.gasto_servicio import GastoServicio
from src.modelos.errores import ErrorFinanzApp
from src.modelos.filtro import FiltroFecha
from src.modelos.gasto import CATEGORIAS, Gasto


def _guardar_mensaje(tipo: str, mensaje: str) -> None:
    """Guarda un mensaje para mostrarlo tras el siguiente ``st.rerun()``."""
    st.session_state["_mensaje_flash"] = (tipo, mensaje)


def mostrar_mensajes_flash() -> None:
    """Muestra y limpia el mensaje pendiente de acciones anteriores."""
    pendiente = st.session_state.pop("_mensaje_flash", None)
    if pendiente:
        tipo, mensaje = pendiente
        getattr(st, tipo)(mensaje)


def mostrar_encabezado() -> None:
    """Muestra el titulo y la descripcion de la aplicacion."""
    st.title("FinanzApp")
    st.caption(
        "Control de gastos personales. Registra, consulta, edita y visualiza "
        "tus gastos; la grafica siempre refleja los datos filtrados."
    )


def panel_filtros() -> FiltroFecha:
    """Dibuja los filtros de fecha en la barra lateral.

    Returns:
        Un :class:`FiltroFecha` construido con las fechas elegidas.
    """
    st.sidebar.header("Filtros por fecha")
    fecha_ini: date | None = st.sidebar.date_input(
        "Fecha inicial", value=None, key="filtro_fecha_ini"
    )
    fecha_fin: date | None = st.sidebar.date_input(
        "Fecha final", value=None, key="filtro_fecha_fin"
    )
    st.sidebar.caption("Deja vacias las fechas para ver todos los gastos.")
    return FiltroFecha(fecha_ini=fecha_ini, fecha_fin=fecha_fin)


def _gasto_a_fila(gasto: Gasto) -> dict[str, object]:
    """Convierte un gasto en un diccionario listo para la tabla."""
    return {
        "ID": gasto.id,
        "Fecha": gasto.fecha,
        "Categoria": gasto.categoria,
        "Monto": gasto.monto,
        "Descripcion": gasto.descripcion,
    }


def _etiqueta_gasto(gasto: Gasto) -> str:
    """Etiqueta legible para los selectores de edicion/eliminacion."""
    return f"#{gasto.id} | {gasto.fecha} | {gasto.categoria} | {gasto.monto:.2f}"


def seccion_registrar(servicio: GastoServicio) -> None:
    """Formulario para registrar un gasto nuevo (R1)."""
    st.subheader("Registrar gasto")
    with st.form("form_registro", clear_on_submit=True):
        col_fecha, col_categoria = st.columns(2)
        fecha = col_fecha.date_input(
            "Fecha", value=date.today(), key="reg_fecha"
        )
        categoria = col_categoria.selectbox(
            "Categoria", options=CATEGORIAS, key="reg_categoria"
        )
        monto = st.number_input(
            "Monto",
            min_value=0.01,
            value=1.00,
            step=0.01,
            format="%.2f",
            key="reg_monto",
        )
        descripcion = st.text_input(
            "Descripcion (opcional)", value="", key="reg_descripcion"
        )
        enviar = st.form_submit_button("Guardar gasto")

    if enviar:
        try:
            gasto = servicio.crear_gasto(
                fecha=fecha,
                categoria=categoria,
                monto=monto,
                descripcion=descripcion,
            )
        except ErrorFinanzApp as exc:
            st.error(f"No se pudo registrar el gasto: {exc}")
        else:
            _guardar_mensaje("success", f"Gasto #{gasto.id} registrado correctamente.")
            st.rerun()


def _tabla_gastos(datos: list[Gasto]) -> None:
    """Renderiza la tabla de gastos."""
    tabla = pd.DataFrame([_gasto_a_fila(gasto) for gasto in datos])
    st.dataframe(tabla, width="stretch", hide_index=True)


def seccion_consultar(
    servicio: GastoServicio, datos: list[Gasto], filtro: FiltroFecha
) -> None:
    """Tabla de gastos filtrados con resumen claro del periodo consultado."""
    st.subheader("Gastos registrados")

    estadisticas = EstadisticasGastos(datos)
    col_ini, col_fin, col_cantidad, col_total = st.columns(4)
    col_ini.metric(
        "Fecha inicial",
        filtro.fecha_ini.strftime("%d/%m/%Y") if filtro.fecha_ini else "Sin limite",
    )
    col_fin.metric(
        "Fecha final",
        filtro.fecha_fin.strftime("%d/%m/%Y") if filtro.fecha_fin else "Sin limite",
    )
    col_cantidad.metric("Gastos encontrados", estadisticas.cantidad())
    col_total.metric("Total gastado", f"{estadisticas.total():.2f}")

    if not datos:
        st.info(
            "No hay gastos registrados para el periodo seleccionado. "
            "Ajusta las fechas de la barra lateral o registra un gasto nuevo."
        )
        return

    _tabla_gastos(datos)

    opciones = {gasto.id: _etiqueta_gasto(gasto) for gasto in datos}
    ids = list(opciones.keys())

    st.divider()
    _formulario_edicion(servicio, ids, opciones)

    st.divider()
    _zona_eliminacion(servicio, ids, opciones)


def _formulario_edicion(
    servicio: GastoServicio, ids: list[int], opciones: dict[int, str]
) -> None:
    """Formulario que carga y actualiza un gasto existente (R3)."""
    st.markdown("#### Editar gasto")
    id_editar = st.selectbox(
        "Selecciona el gasto a editar",
        options=ids,
        format_func=lambda i: opciones[i],
        key="sel_editar",
    )
    gasto = servicio.obtener_gasto(id_editar)
    if gasto is None:
        st.warning("El gasto seleccionado ya no existe. Actualiza la lista.")
        return

    indice_categoria = (
        CATEGORIAS.index(gasto.categoria) if gasto.categoria in CATEGORIAS else 0
    )
    with st.form("form_edicion"):
        fecha = st.date_input("Fecha", value=gasto.fecha, key="edit_fecha")
        categoria = st.selectbox(
            "Categoria",
            options=CATEGORIAS,
            index=indice_categoria,
            key="edit_categoria",
        )
        monto = st.number_input(
            "Monto",
            min_value=0.01,
            value=float(gasto.monto),
            step=0.01,
            format="%.2f",
            key="edit_monto",
        )
        descripcion = st.text_input(
            "Descripcion", value=gasto.descripcion, key="edit_descripcion"
        )
        guardar = st.form_submit_button("Guardar cambios")

    if guardar:
        try:
            servicio.actualizar_gasto(
                id_gasto=id_editar,
                fecha=fecha,
                categoria=categoria,
                monto=monto,
                descripcion=descripcion,
            )
        except ErrorFinanzApp as exc:
            st.error(f"No se pudo actualizar el gasto: {exc}")
        else:
            _guardar_mensaje("success", f"Gasto #{id_editar} actualizado correctamente.")
            st.rerun()


def _zona_eliminacion(
    servicio: GastoServicio, ids: list[int], opciones: dict[int, str]
) -> None:
    """Seleccion y eliminacion de un gasto con confirmacion previa (R3)."""
    st.markdown("#### Eliminar gasto")
    id_eliminar = st.selectbox(
        "Selecciona el gasto a eliminar",
        options=ids,
        format_func=lambda i: opciones[i],
        key="sel_eliminar",
    )
    if st.button("Solicitar eliminacion", key="btn_solicitar_eliminar"):
        st.session_state["id_a_eliminar"] = id_eliminar

    id_pendiente = st.session_state.get("id_a_eliminar")
    if id_pendiente is None:
        return

    gasto = servicio.obtener_gasto(id_pendiente)
    if gasto is None:
        st.warning("El gasto seleccionado ya no existe.")
        st.session_state.pop("id_a_eliminar", None)
        return

    st.warning(
        f"Estas a punto de eliminar el gasto #{gasto.id} "
        f"({gasto.categoria}, {gasto.monto:.2f}). Esta accion no se puede deshacer."
    )
    col_confirmar, col_cancelar = st.columns(2)
    if col_confirmar.button("Confirmar eliminacion", key="btn_confirmar_eliminar"):
        try:
            servicio.eliminar_gasto(id_pendiente)
        except ErrorFinanzApp as exc:
            st.error(f"No se pudo eliminar el gasto: {exc}")
        else:
            st.session_state.pop("id_a_eliminar", None)
            _guardar_mensaje("success", f"Gasto #{id_pendiente} eliminado correctamente.")
            st.rerun()
    if col_cancelar.button("Cancelar", key="btn_cancelar_eliminar"):
        st.session_state.pop("id_a_eliminar", None)
        st.rerun()


def seccion_grafica(datos: list[Gasto]) -> None:
    """Grafica de gasto por categoria sobre los datos filtrados (R4)."""
    st.subheader("Resumen por categoria")
    estadisticas = EstadisticasGastos(datos)

    if estadisticas.cantidad() == 0:
        st.info(
            "No hay datos para graficar: el periodo seleccionado no tiene gastos "
            "registrados. Prueba a ampliar o quitar los filtros de fecha."
        )
        return

    col_total, col_cantidad, col_promedio = st.columns(3)
    col_total.metric("Gasto total", f"{estadisticas.total():.2f}")
    col_cantidad.metric("Numero de gastos", estadisticas.cantidad())
    col_promedio.metric("Gasto promedio", f"{estadisticas.promedio():.2f}")

    totales = estadisticas.total_por_categoria()
    grafica = pd.DataFrame(
        {
            "Categoria": list(totales.keys()),
            "Total": list(totales.values()),
        }
    )
    st.bar_chart(grafica, x="Categoria", y="Total")
    st.caption(
        "La grafica se calcula sobre exactamente los mismos gastos filtrados "
        "que se muestran en la tabla."
    )
