"""Fixtures compartidas para las pruebas."""

from __future__ import annotations

import pytest

from src.logica.gasto_servicio import GastoServicio
from src.persistencia.sqlite_repositorio import SqliteRepositorioGastos


@pytest.fixture
def repo() -> SqliteRepositorioGastos:
    """Repositorio SQLite temporal en memoria."""
    repositorio = SqliteRepositorioGastos(":memory:")
    yield repositorio
    repositorio.cerrar()


@pytest.fixture
def servicio(repo: SqliteRepositorioGastos) -> GastoServicio:
    """Servicio de gastos respaldado por una base en memoria."""
    return GastoServicio(repo)
