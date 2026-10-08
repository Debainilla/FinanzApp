"""Pruebas del calculo de estadisticas."""

from __future__ import annotations

from datetime import date

from src.logica.estadisticas import EstadisticasGastos
from src.modelos.gasto import Gasto


def _gastos() -> list[Gasto]:
    return [
        Gasto(date(2024, 1, 1), "Ocio", 10.0, ""),
        Gasto(date(2024, 1, 2), "Ocio", 5.0, ""),
        Gasto(date(2024, 1, 3), "Salud", 20.0, ""),
    ]


def test_cantidad_y_total() -> None:
    stats = EstadisticasGastos(_gastos())
    assert stats.cantidad() == 3
    assert stats.total() == 35.0


def test_promedio() -> None:
    stats = EstadisticasGastos(_gastos())
    assert stats.promedio() == round(35.0 / 3, 2)


def test_total_por_categoria_ordenado() -> None:
    stats = EstadisticasGastos(_gastos())
    assert stats.total_por_categoria() == {"Salud": 20.0, "Ocio": 15.0}


def test_lista_vacia() -> None:
    stats = EstadisticasGastos([])
    assert stats.cantidad() == 0
    assert stats.total() == 0.0
    assert stats.promedio() == 0.0
    assert stats.total_por_categoria() == {}


def test_no_modifica_la_lista_original() -> None:
    original = _gastos()
    EstadisticasGastos(original)
    assert len(original) == 3
