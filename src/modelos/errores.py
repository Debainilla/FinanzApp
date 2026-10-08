"""Excepciones de dominio de FinanzApp.

Se definen excepciones propias para no exponer detalles tecnicos
(por ejemplo, errores de SQLite) a las capas superiores.
"""


class ErrorFinanzApp(Exception):
    """Excepcion base de la aplicacion."""


class ErrorValidacion(ErrorFinanzApp):
    """Se lanza cuando los datos de entrada no cumplen las reglas de negocio."""


class ErrorNoEncontrado(ErrorFinanzApp):
    """Se lanza cuando se intenta operar sobre un gasto inexistente."""


class ErrorPersistencia(ErrorFinanzApp):
    """Se lanza cuando falla el acceso al almacenamiento (SQLite)."""
