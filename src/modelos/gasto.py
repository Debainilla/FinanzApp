"""Modelo de dominio: la entidad ``Gasto``.

Esta capa no conoce ni la base de datos ni Streamlit; solo contiene
los datos y las reglas minimas para que un gasto sea valido.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from typing import Final

from .errores import ErrorValidacion

#: Catalogo fijo de categorias permitidas.
CATEGORIAS: Final[list[str]] = [
    "Alimentación",
    "Transporte",
    "Vivienda",
    "Ocio",
    "Salud",
    "Educación",
    "Otros",
]


@dataclass
class Gasto:
    """Representa un gasto personal.

    Attributes:
        fecha: Fecha en que se realizo el gasto.
        categoria: Categoria del gasto; debe pertenecer a :data:`CATEGORIAS`.
        monto: Importe del gasto; debe ser un numero finito mayor que cero.
        descripcion: Texto libre opcional.
        id: Identificador asignado por la base de datos (0 si aun no se guardo).
    """

    fecha: date
    categoria: str
    monto: float
    descripcion: str = ""
    id: int = 0

    def validar(self) -> None:
        """Valida y normaliza los datos del gasto.

        Normaliza la categoria y la descripcion (sin espacios sobrantes)
        y redondea el monto a dos decimales.

        Raises:
            ErrorValidacion: Si la fecha, la categoria o el monto no son validos.
        """
        if not isinstance(self.fecha, date):
            raise ErrorValidacion("La fecha debe ser una fecha valida.")

        if not isinstance(self.categoria, str) or not self.categoria.strip():
            raise ErrorValidacion("La categoria no puede estar vacia.")

        categoria_limpia = self.categoria.strip()
        if categoria_limpia not in CATEGORIAS:
            raise ErrorValidacion(
                f"Categoria no permitida: '{categoria_limpia}'. "
                f"Opciones validas: {', '.join(CATEGORIAS)}."
            )

        try:
            monto = float(self.monto)
        except (TypeError, ValueError) as exc:
            raise ErrorValidacion("El monto debe ser un numero.") from exc

        if not math.isfinite(monto):
            raise ErrorValidacion("El monto debe ser un numero finito mayor que cero.")

        monto = round(monto, 2)
        if monto <= 0:
            raise ErrorValidacion("El monto debe ser mayor que cero.")

        self.categoria = categoria_limpia
        self.monto = monto
        self.descripcion = (self.descripcion or "").strip()
