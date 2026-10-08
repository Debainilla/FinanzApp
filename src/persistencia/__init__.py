"""Capa de persistencia: contrato y su implementacion sobre SQLite."""

from .repositorio import RepositorioGastos
from .sqlite_repositorio import SqliteRepositorioGastos

__all__ = ["RepositorioGastos", "SqliteRepositorioGastos"]
