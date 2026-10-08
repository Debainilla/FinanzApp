"""Pruebas de la interfaz con Streamlit AppTest.

Se usa una base de datos temporal por prueba (variable ``FINANZAPP_DB``)
para no tocar la base real.
"""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parents[1]
APP = str(RAIZ / "app.py")


def _app(tmp_path, nombre: str) -> AppTest:
    os.environ["FINANZAPP_DB"] = str(tmp_path / nombre)
    return AppTest.from_file(APP, default_timeout=30)


def _por_key(at: AppTest, tipo: str, key: str):
    for widget in at.get(tipo):
        if getattr(widget, "key", None) == key:
            return widget
    raise AssertionError(f"No se encontro {tipo} con key '{key}'")


def _boton_por_label(at: AppTest, texto: str):
    for boton in at.get("button"):
        if texto in (boton.label or ""):
            return boton
    raise AssertionError(f"No se encontro el boton '{texto}'")


def _registrar(at, fecha, categoria, monto, descripcion) -> None:
    _por_key(at, "date_input", "reg_fecha").set_value(fecha)
    _por_key(at, "selectbox", "reg_categoria").set_value(categoria)
    _por_key(at, "number_input", "reg_monto").set_value(monto)
    _por_key(at, "text_input", "reg_descripcion").set_value(descripcion)
    _boton_por_label(at, "Guardar gasto").click()
    at.run()


def test_app_inicia_sin_excepciones(tmp_path) -> None:
    at = _app(tmp_path, "inicio.db").run()
    assert not at.exception
    assert at.title[0].value == "FinanzApp"


def test_registrar_gasto_aparece_en_tabla(tmp_path) -> None:
    at = _app(tmp_path, "registro.db").run()
    _registrar(at, date(2024, 1, 15), "Transporte", 25.5, "Taxi")
    assert not at.exception
    assert [s.value for s in at.success]
    assert len(at.dataframe[0].value) == 1


def test_grafica_usa_exactamente_los_datos_filtrados(tmp_path) -> None:
    at = _app(tmp_path, "filtro.db").run()
    _registrar(at, date(2024, 1, 5), "Ocio", 10.0, "cine")
    _registrar(at, date(2024, 2, 5), "Salud", 30.0, "farmacia")
    assert len(at.dataframe[0].value) == 2

    _por_key(at, "date_input", "filtro_fecha_ini").set_value(date(2024, 1, 1))
    _por_key(at, "date_input", "filtro_fecha_fin").set_value(date(2024, 1, 31))
    at.run()

    assert not at.exception
    tabla = at.dataframe[0].value
    assert len(tabla) == 1
    valores_metricas = [m.value for m in at.metric]
    assert "10.00" in valores_metricas
    assert "30.00" not in valores_metricas


def _metric(at: AppTest, label: str) -> str:
    for metrica in at.metric:
        if metrica.label == label:
            return metrica.value
    raise AssertionError(f"No se encontro la metrica '{label}'")


def test_resumen_del_periodo_filtrado(tmp_path) -> None:
    at = _app(tmp_path, "resumen.db").run()
    _registrar(at, date(2024, 1, 5), "Ocio", 10.0, "cine")
    _registrar(at, date(2024, 2, 5), "Salud", 30.0, "farmacia")

    assert _metric(at, "Fecha inicial") == "Sin limite"
    assert _metric(at, "Fecha final") == "Sin limite"
    assert _metric(at, "Gastos encontrados") == "2"
    assert _metric(at, "Total gastado") == "40.00"

    _por_key(at, "date_input", "filtro_fecha_ini").set_value(date(2024, 1, 1))
    _por_key(at, "date_input", "filtro_fecha_fin").set_value(date(2024, 1, 31))
    at.run()

    assert not at.exception
    assert _metric(at, "Fecha inicial") == "01/01/2024"
    assert _metric(at, "Fecha final") == "31/01/2024"
    assert _metric(at, "Gastos encontrados") == "1"
    assert _metric(at, "Total gastado") == "10.00"


def test_periodo_sin_resultados_muestra_aviso_sin_grafica(tmp_path) -> None:
    at = _app(tmp_path, "vacio.db").run()
    _registrar(at, date(2024, 1, 5), "Ocio", 10.0, "cine")

    _por_key(at, "date_input", "filtro_fecha_ini").set_value(date(2024, 3, 1))
    _por_key(at, "date_input", "filtro_fecha_fin").set_value(date(2024, 3, 31))
    at.run()

    assert not at.exception
    assert _metric(at, "Gastos encontrados") == "0"
    assert _metric(at, "Total gastado") == "0.00"
    assert len(at.dataframe) == 0
    mensajes = [info.value for info in at.info]
    assert any("No hay gastos registrados" in mensaje for mensaje in mensajes)
    assert any("No hay datos para graficar" in mensaje for mensaje in mensajes)


def test_eliminar_requiere_confirmacion(tmp_path) -> None:
    at = _app(tmp_path, "eliminar.db").run()
    _registrar(at, date(2024, 1, 5), "Ocio", 10.0, "cine")

    _boton_por_label(at, "Solicitar eliminacion").click()
    at.run()
    assert not at.exception
    assert [w.value for w in at.warning]

    _boton_por_label(at, "Confirmar eliminacion").click()
    at.run()
    assert not at.exception
    assert len(at.dataframe) == 0
    assert any("No hay gastos" in info.value for info in at.info)
