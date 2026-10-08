"""Pruebas del repositorio SQLite (creacion de esquema y CRUD)."""

from __future__ import annotations

from datetime import date

from src.modelos.gasto import Gasto
from src.persistencia.sqlite_repositorio import SqliteRepositorioGastos


def test_crear_y_obtener(repo: SqliteRepositorioGastos) -> None:
    creado = repo.crear(Gasto(date(2024, 3, 1), "Vivienda", 500.0, "alquiler"))
    assert creado.id == 1
    recuperado = repo.obtener(1)
    assert recuperado is not None
    assert recuperado.descripcion == "alquiler"


def test_obtener_inexistente_devuelve_none(repo: SqliteRepositorioGastos) -> None:
    assert repo.obtener(777) is None


def test_ids_autoincrementales(repo: SqliteRepositorioGastos) -> None:
    primero = repo.crear(Gasto(date(2024, 1, 1), "Ocio", 1.0, ""))
    segundo = repo.crear(Gasto(date(2024, 1, 2), "Ocio", 2.0, ""))
    assert (primero.id, segundo.id) == (1, 2)


def test_actualizar_eliminar(repo: SqliteRepositorioGastos) -> None:
    gasto = repo.crear(Gasto(date(2024, 1, 1), "Ocio", 1.0, ""))
    gasto.monto = 5.0
    repo.actualizar(gasto)
    assert repo.obtener(gasto.id).monto == 5.0  # type: ignore[union-attr]

    repo.eliminar(gasto.id)
    assert repo.obtener(gasto.id) is None


def test_persistencia_en_archivo(tmp_path) -> None:
    ruta = str(tmp_path / "prueba.db")
    repo = SqliteRepositorioGastos(ruta)
    repo.crear(Gasto(date(2024, 1, 1), "Educación", 30.0, "curso"))
    repo.cerrar()

    repo_reabierto = SqliteRepositorioGastos(ruta)
    gastos = repo_reabierto.listar()
    repo_reabierto.cerrar()
    assert len(gastos) == 1
    assert gastos[0].categoria == "Educación"
