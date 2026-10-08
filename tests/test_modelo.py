"""Pruebas de validacion del modelo (Gasto y FiltroFecha)."""

from __future__ import annotations

from datetime import date

import pytest

from src.modelos.errores import ErrorValidacion
from src.modelos.filtro import FiltroFecha
from src.modelos.gasto import CATEGORIAS, Gasto


def test_gasto_valido_normaliza_campos() -> None:
    gasto = Gasto(
        fecha=date(2024, 5, 1),
        categoria="  Ocio  ",
        monto=10.129,
        descripcion="  cine  ",
    )
    gasto.validar()
    assert gasto.categoria == "Ocio"
    assert gasto.monto == 10.13
    assert gasto.descripcion == "cine"


def test_monto_debe_ser_mayor_que_cero() -> None:
    with pytest.raises(ErrorValidacion):
        Gasto(date(2024, 1, 1), "Ocio", 0).validar()
    with pytest.raises(ErrorValidacion):
        Gasto(date(2024, 1, 1), "Ocio", -5).validar()


def test_monto_no_numerico_es_invalido() -> None:
    with pytest.raises(ErrorValidacion):
        Gasto(date(2024, 1, 1), "Ocio", "abc").validar()  # type: ignore[arg-type]


def test_monto_muy_pequeno_se_redondea_a_cero_y_es_invalido() -> None:
    with pytest.raises(ErrorValidacion):
        Gasto(date(2024, 1, 1), "Ocio", 0.001).validar()


def test_categoria_vacia_es_invalida() -> None:
    with pytest.raises(ErrorValidacion):
        Gasto(date(2024, 1, 1), "   ", 10).validar()


def test_categoria_fuera_del_catalogo_es_invalida() -> None:
    with pytest.raises(ErrorValidacion):
        Gasto(date(2024, 1, 1), "NoExiste", 10).validar()


def test_descripcion_opcional_se_normaliza_a_vacio() -> None:
    gasto = Gasto(date(2024, 1, 1), "Salud", 10, None)  # type: ignore[arg-type]
    gasto.validar()
    assert gasto.descripcion == ""


def test_catalogo_tiene_categorias() -> None:
    assert "Otros" in CATEGORIAS


def test_filtro_fechas_invertidas_es_invalido() -> None:
    filtro = FiltroFecha(fecha_ini=date(2024, 2, 1), fecha_fin=date(2024, 1, 1))
    with pytest.raises(ErrorValidacion):
        filtro.validar()


def test_filtro_contiene_limites_inclusivos() -> None:
    filtro = FiltroFecha(fecha_ini=date(2024, 1, 10), fecha_fin=date(2024, 1, 20))
    assert filtro.contiene(date(2024, 1, 10))
    assert filtro.contiene(date(2024, 1, 20))
    assert not filtro.contiene(date(2024, 1, 9))
    assert not filtro.contiene(date(2024, 1, 21))


def test_filtro_vacio_contiene_cualquier_fecha() -> None:
    assert FiltroFecha().contiene(date(2000, 1, 1))
