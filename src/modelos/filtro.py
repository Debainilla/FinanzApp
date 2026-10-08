"""Modelo de dominio: objeto de valor ``FiltroFecha``."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional

from .errores import ErrorValidacion


@dataclass
class FiltroFecha:
    """Rango de fechas (inclusivo) usado para filtrar gastos.

    Attributes:
        fecha_ini: Fecha inicial del rango o ``None`` para no acotar por abajo.
        fecha_fin: Fecha final del rango o ``None`` para no acotar por arriba.
    """

    fecha_ini: Optional[date] = None
    fecha_fin: Optional[date] = None

    def validar(self) -> None:
        """Comprueba que el rango de fechas sea coherente.

        Raises:
            ErrorValidacion: Si la fecha inicial es posterior a la final.
        """
        if self.fecha_ini and self.fecha_fin and self.fecha_ini > self.fecha_fin:
            raise ErrorValidacion(
                "La fecha inicial no puede ser mayor que la fecha final."
            )

    def contiene(self, fecha: date) -> bool:
        """Indica si ``fecha`` cae dentro del rango (limites inclusivos)."""
        if self.fecha_ini and fecha < self.fecha_ini:
            return False
        if self.fecha_fin and fecha > self.fecha_fin:
            return False
        return True
