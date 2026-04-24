"""Formatacao textual de matrizes para exibicao na UI."""

import numpy as np
from numpy.typing import NDArray


def _formatar_linha_inteira(linha: NDArray[np.generic]) -> str:
    return ' '.join(f'{int(valor):4d}' for valor in linha)


def _formatar_linha_decimal(linha: NDArray[np.generic]) -> str:
    return ' '.join(f'{float(valor):7.1f}' for valor in linha)


def matriz_para_linhas(matriz: NDArray[np.generic]) -> list[str]:
    """Converte matriz numpy em lista de linhas prontas para renderizacao."""
    linhas_formatadas: list[str] = []

    if np.issubdtype(matriz.dtype, np.integer):
        for linha in matriz:
            linhas_formatadas.append(_formatar_linha_inteira(linha))
        return linhas_formatadas

    for linha in matriz:
        linhas_formatadas.append(_formatar_linha_decimal(linha))
    return linhas_formatadas
