"""Contrato (interfaz) de acceso a los gastos.

La logica de negocio depende de esta abstraccion y no de SQLite,
lo que permite cambiar el almacenamiento sin tocar el resto del sistema.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from src.modelos.filtro import FiltroFecha
from src.modelos.gasto import Gasto


class RepositorioGastos(ABC):
    """Define las operaciones CRUD sobre gastos."""

    @abstractmethod
    def crear(self, gasto: Gasto) -> Gasto:
        """Persiste un gasto nuevo y devuelve el gasto con su ``id`` asignado."""

    @abstractmethod
    def obtener(self, id_gasto: int) -> Optional[Gasto]:
        """Devuelve el gasto con ``id_gasto`` o ``None`` si no existe."""

    @abstractmethod
    def listar(self, filtro: Optional[FiltroFecha] = None) -> list[Gasto]:
        """Devuelve los gastos, opcionalmente acotados por ``filtro``."""

    @abstractmethod
    def actualizar(self, gasto: Gasto) -> None:
        """Actualiza un gasto existente identificado por ``gasto.id``."""

    @abstractmethod
    def eliminar(self, id_gasto: int) -> None:
        """Elimina el gasto con ``id_gasto``."""
