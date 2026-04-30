"""API publica do backend do projeto Smith-Waterman."""

from .io_entrada import abrir_arquivo, parsear_entrada
from .alinhamento import executar_suite_alinhamento

__all__ = [
    'abrir_arquivo',
    'parsear_entrada',
    'executar_suite_alinhamento',
]
