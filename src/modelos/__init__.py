"""Capa de modelo: entidades, objetos de valor y excepciones de dominio."""

from .errores import (
    ErrorFinanzApp,
    ErrorNoEncontrado,
    ErrorPersistencia,
    ErrorValidacion,
)
from .filtro import FiltroFecha
from .gasto import CATEGORIAS, Gasto

__all__ = [
    "CATEGORIAS",
    "Gasto",
    "FiltroFecha",
    "ErrorFinanzApp",
    "ErrorValidacion",
    "ErrorNoEncontrado",
    "ErrorPersistencia",
]
