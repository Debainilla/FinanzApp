"""Calculo de estadisticas sobre un conjunto de gastos.

La clase es pura: recibe la lista de gastos (normalmente ya filtrada) y
calcula metricas. No accede a la base de datos ni a Streamlit.
"""

from __future__ import annotations

from src.modelos.gasto import Gasto


class EstadisticasGastos:
    """Metricas agregadas de una coleccion de gastos.

    Args:
        gastos: Gastos sobre los que calcular las estadisticas. Se copia
            la lista recibida para no modificarla.
    """

    def __init__(self, gastos: list[Gasto]) -> None:
        self._gastos: list[Gasto] = list(gastos)

    def cantidad(self) -> int:
        """Numero de gastos considerados."""
        return len(self._gastos)

    def total(self) -> float:
        """Suma de todos los montos."""
        return round(sum(gasto.monto for gasto in self._gastos), 2)

    def promedio(self) -> float:
        """Monto promedio por gasto (0.0 si no hay gastos)."""
        if not self._gastos:
            return 0.0
        return round(self.total() / self.cantidad(), 2)

    def total_por_categoria(self) -> dict[str, float]:
        """Diccionario ``categoria -> suma de montos``.

        El resultado se ordena de mayor a menor importe, que es el orden
        mas util para la grafica de barras.
        """
        acumulado: dict[str, float] = {}
        for gasto in self._gastos:
            acumulado[gasto.categoria] = round(
                acumulado.get(gasto.categoria, 0.0) + gasto.monto, 2
            )
        return dict(
            sorted(acumulado.items(), key=lambda item: item[1], reverse=True)
        )
