"""Pruebas de la logica de negocio (GastoServicio)."""

from __future__ import annotations

from datetime import date

import pytest

from src.logica.gasto_servicio import GastoServicio
from src.modelos.errores import ErrorNoEncontrado, ErrorValidacion
from src.modelos.filtro import FiltroFecha


def _crear(servicio: GastoServicio, dia: int, monto: float = 10.0) -> int:
    gasto = servicio.crear_gasto(
        fecha=date(2024, 1, dia),
        categoria="Ocio",
        monto=monto,
        descripcion=f"gasto {dia}",
    )
    return gasto.id


def test_crear_gasto_asigna_id(servicio: GastoServicio) -> None:
    gasto = servicio.crear_gasto(date(2024, 1, 1), "Transporte", 12.5, "bus")
    assert gasto.id > 0
    assert gasto.categoria == "Transporte"
    assert gasto.monto == 12.5


def test_crear_gasto_invalido_no_persiste(servicio: GastoServicio) -> None:
    with pytest.raises(ErrorValidacion):
        servicio.crear_gasto(date(2024, 1, 1), "Transporte", 0)
    assert servicio.listar_gastos() == []


def test_listar_sin_filtro_devuelve_todos(servicio: GastoServicio) -> None:
    _crear(servicio, 1)
    _crear(servicio, 15)
    _crear(servicio, 20)
    assert len(servicio.listar_gastos()) == 3


def test_filtrado_por_fecha_inclusivo(servicio: GastoServicio) -> None:
    _crear(servicio, 1)
    _crear(servicio, 15)
    _crear(servicio, 31)
    filtro = FiltroFecha(date(2024, 1, 1), date(2024, 1, 15))
    resultado = servicio.listar_gastos(filtro)
    assert [g.fecha.day for g in resultado] == [15, 1]


def test_filtro_con_fechas_invertidas_falla(servicio: GastoServicio) -> None:
    _crear(servicio, 10)
    filtro = FiltroFecha(date(2024, 2, 1), date(2024, 1, 1))
    with pytest.raises(ErrorValidacion):
        servicio.listar_gastos(filtro)


def test_obtener_gasto_inexistente_devuelve_none(servicio: GastoServicio) -> None:
    assert servicio.obtener_gasto(999) is None


def test_editar_gasto(servicio: GastoServicio) -> None:
    id_gasto = _crear(servicio, 1, 10.0)
    servicio.actualizar_gasto(id_gasto, date(2024, 1, 2), "Salud", 99.99, "farmacia")
    gasto = servicio.obtener_gasto(id_gasto)
    assert gasto is not None
    assert gasto.categoria == "Salud"
    assert gasto.monto == 99.99
    assert gasto.descripcion == "farmacia"
    assert gasto.fecha == date(2024, 1, 2)


def test_editar_gasto_inexistente_falla(servicio: GastoServicio) -> None:
    with pytest.raises(ErrorNoEncontrado):
        servicio.actualizar_gasto(123, date(2024, 1, 1), "Ocio", 5, "")


def test_eliminar_gasto(servicio: GastoServicio) -> None:
    id_gasto = _crear(servicio, 1)
    servicio.eliminar_gasto(id_gasto)
    assert servicio.obtener_gasto(id_gasto) is None
    assert servicio.listar_gastos() == []


def test_eliminar_gasto_inexistente_falla(servicio: GastoServicio) -> None:
    with pytest.raises(ErrorNoEncontrado):
        servicio.eliminar_gasto(321)
