"""API publica do backend do projeto Smith-Waterman."""

from .io_entrada import abrir_arquivo, parsear_entrada
from .suite import executar_suite_alinhamento, smith_waterman

__all__ = [
    'abrir_arquivo',
    'parsear_entrada',
    'smith_waterman',
    'executar_suite_alinhamento',
]
