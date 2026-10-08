"""Servicio de aplicacion para la gestion de gastos.

Orquesta las validaciones del modelo y delega el almacenamiento en un
``RepositorioGastos`` inyectado. No conoce SQLite ni Streamlit.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from src.modelos.filtro import FiltroFecha
from src.modelos.gasto import Gasto
from src.persistencia.repositorio import RepositorioGastos


class GastoServicio:
    """Casos de uso de alto nivel sobre gastos.

    Args:
        repositorio: Implementacion concreta de :class:`RepositorioGastos`.
    """

    def __init__(self, repositorio: RepositorioGastos) -> None:
        self._repositorio = repositorio

    def crear_gasto(
        self,
        fecha: date,
        categoria: str,
        monto: float,
        descripcion: str = "",
    ) -> Gasto:
        """Valida y registra un gasto nuevo.

        Returns:
            El gasto creado, con su ``id`` asignado.

        Raises:
            ErrorValidacion: Si los datos no son validos.
        """
        gasto = Gasto(
            fecha=fecha,
            categoria=categoria,
            monto=monto,
            descripcion=descripcion,
        )
        gasto.validar()
        return self._repositorio.crear(gasto)

    def obtener_gasto(self, id_gasto: int) -> Optional[Gasto]:
        """Devuelve un gasto por su id o ``None`` si no existe."""
        return self._repositorio.obtener(id_gasto)

    def listar_gastos(self, filtro: Optional[FiltroFecha] = None) -> list[Gasto]:
        """Lista los gastos aplicando, si se indica, un filtro por fecha.

        Raises:
            ErrorValidacion: Si el rango de fechas es incoherente.
        """
        if filtro is not None:
            filtro.validar()
        return self._repositorio.listar(filtro)

    def actualizar_gasto(
        self,
        id_gasto: int,
        fecha: date,
        categoria: str,
        monto: float,
        descripcion: str = "",
    ) -> None:
        """Actualiza un gasto existente.

        Raises:
            ErrorValidacion: Si los datos no son validos.
            ErrorNoEncontrado: Si el gasto no existe.
        """
        gasto = Gasto(
            id=id_gasto,
            fecha=fecha,
            categoria=categoria,
            monto=monto,
            descripcion=descripcion,
        )
        gasto.validar()
        self._repositorio.actualizar(gasto)

    def eliminar_gasto(self, id_gasto: int) -> None:
        """Elimina un gasto existente.

        Raises:
            ErrorNoEncontrado: Si el gasto no existe.
        """
        self._repositorio.eliminar(id_gasto)
