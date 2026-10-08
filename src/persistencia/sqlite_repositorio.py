"""Implementacion del repositorio de gastos sobre SQLite.

Es la unica clase de la aplicacion que importa ``sqlite3``. Crea la base
de datos y la tabla automaticamente si no existen.
"""

from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path
from typing import Optional

from src.modelos.errores import ErrorNoEncontrado, ErrorPersistencia
from src.modelos.filtro import FiltroFecha
from src.modelos.gasto import Gasto

from .repositorio import RepositorioGastos


class SqliteRepositorioGastos(RepositorioGastos):
    """Repositorio de gastos respaldado por una base SQLite.

    Args:
        ruta_db: Ruta del archivo de base de datos o ``":memory:"`` para
            una base temporal en memoria.
    """

    def __init__(self, ruta_db: str = "data/finanzapp.db") -> None:
        self.ruta_db = str(ruta_db)
        try:
            if self.ruta_db != ":memory:":
                Path(self.ruta_db).parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(self.ruta_db, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._crear_esquema()
        except sqlite3.Error as exc:
            raise ErrorPersistencia(
                f"No se pudo abrir la base de datos '{self.ruta_db}': {exc}"
            ) from exc

    def _crear_esquema(self) -> None:
        """Crea la tabla ``gastos`` si aun no existe."""
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS gastos (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha       TEXT NOT NULL,
                categoria   TEXT NOT NULL,
                monto       REAL NOT NULL,
                descripcion TEXT NOT NULL DEFAULT ''
            )
            """
        )
        self._conn.commit()

    @staticmethod
    def _mapear(fila: sqlite3.Row) -> Gasto:
        """Convierte una fila de SQLite en un objeto :class:`Gasto`."""
        return Gasto(
            id=int(fila["id"]),
            fecha=date.fromisoformat(fila["fecha"]),
            categoria=fila["categoria"],
            monto=float(fila["monto"]),
            descripcion=fila["descripcion"] or "",
        )

    def crear(self, gasto: Gasto) -> Gasto:
        gasto.validar()
        try:
            cursor = self._conn.execute(
                "INSERT INTO gastos (fecha, categoria, monto, descripcion) "
                "VALUES (?, ?, ?, ?)",
                (
                    gasto.fecha.isoformat(),
                    gasto.categoria,
                    gasto.monto,
                    gasto.descripcion,
                ),
            )
            self._conn.commit()
        except sqlite3.Error as exc:
            raise ErrorPersistencia(f"No se pudo guardar el gasto: {exc}") from exc
        gasto.id = int(cursor.lastrowid)
        return gasto

    def obtener(self, id_gasto: int) -> Optional[Gasto]:
        fila = self._conn.execute(
            "SELECT * FROM gastos WHERE id = ?", (id_gasto,)
        ).fetchone()
        return self._mapear(fila) if fila else None

    def listar(self, filtro: Optional[FiltroFecha] = None) -> list[Gasto]:
        consulta = "SELECT * FROM gastos"
        condiciones: list[str] = []
        parametros: list[str] = []

        if filtro:
            filtro.validar()
            if filtro.fecha_ini:
                condiciones.append("fecha >= ?")
                parametros.append(filtro.fecha_ini.isoformat())
            if filtro.fecha_fin:
                condiciones.append("fecha <= ?")
                parametros.append(filtro.fecha_fin.isoformat())

        if condiciones:
            consulta += " WHERE " + " AND ".join(condiciones)
        consulta += " ORDER BY fecha DESC, id DESC"

        filas = self._conn.execute(consulta, parametros).fetchall()
        return [self._mapear(fila) for fila in filas]

    def actualizar(self, gasto: Gasto) -> None:
        gasto.validar()
        if gasto.id <= 0:
            raise ErrorNoEncontrado("El gasto indicado no tiene un id valido.")
        try:
            cursor = self._conn.execute(
                "UPDATE gastos SET fecha = ?, categoria = ?, monto = ?, "
                "descripcion = ? WHERE id = ?",
                (
                    gasto.fecha.isoformat(),
                    gasto.categoria,
                    gasto.monto,
                    gasto.descripcion,
                    gasto.id,
                ),
            )
            self._conn.commit()
        except sqlite3.Error as exc:
            raise ErrorPersistencia(f"No se pudo actualizar el gasto: {exc}") from exc

        if cursor.rowcount == 0:
            raise ErrorNoEncontrado(f"No existe un gasto con id {gasto.id}.")

    def eliminar(self, id_gasto: int) -> None:
        try:
            cursor = self._conn.execute(
                "DELETE FROM gastos WHERE id = ?", (id_gasto,)
            )
            self._conn.commit()
        except sqlite3.Error as exc:
            raise ErrorPersistencia(f"No se pudo eliminar el gasto: {exc}") from exc

        if cursor.rowcount == 0:
            raise ErrorNoEncontrado(f"No existe un gasto con id {id_gasto}.")

    def cerrar(self) -> None:
        """Cierra la conexion a la base de datos."""
        self._conn.close()
