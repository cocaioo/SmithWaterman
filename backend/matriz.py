"""Funcoes utilitarias para construcao das matrizes de score."""

import numpy as np
from numpy.typing import NDArray

MatrizNumerica = NDArray[np.float64]


def obter_dimensoes_matriz(
    sequencia_vertical: str,
    sequencia_horizontal: str,
) -> tuple[int, int]:
    """Retorna a dimensao da matriz considerando borda extra de gaps."""
    return len(sequencia_vertical) + 1, len(sequencia_horizontal) + 1


def criar_matriz(quantidade_linhas: int, quantidade_colunas: int) -> MatrizNumerica:
    """Cria matriz de float inicializada com zero."""
    return np.zeros((quantidade_linhas, quantidade_colunas), dtype=float)


def definir_gaps_horizontal(matriz: MatrizNumerica, penalidade_gap: float) -> MatrizNumerica:
    """Preenche a ultima linha com gaps acumulados na horizontal."""
    ultima_linha = matriz.shape[0] - 1
    for coluna in range(matriz.shape[1]):
        matriz[ultima_linha, coluna] = coluna * penalidade_gap
    return matriz


def definir_gaps_vertical(matriz: MatrizNumerica, penalidade_gap: float) -> MatrizNumerica:
    """Preenche a primeira coluna com gaps acumulados na vertical."""
    ultima_linha = matriz.shape[0] - 1
    for deslocamento in range(matriz.shape[0]):
        matriz[ultima_linha - deslocamento, 0] = deslocamento * penalidade_gap
    return matriz


def inicializar_matriz_com_gaps(
    quantidade_linhas: int,
    quantidade_colunas: int,
    penalidade_gap: float,
) -> MatrizNumerica:
    """Cria matriz e aplica inicializacao de gaps de alinhamento global."""
    matriz = criar_matriz(quantidade_linhas, quantidade_colunas)
    definir_gaps_horizontal(matriz, penalidade_gap)
    definir_gaps_vertical(matriz, penalidade_gap)
    return matriz


def _indice_vertical(sequencia_vertical: str, linha: int) -> int:
    return len(sequencia_vertical) - 1 - linha


def _indice_horizontal(coluna: int) -> int:
    return coluna - 1


def eh_match(
    sequencia_vertical: str,
    sequencia_horizontal: str,
    linha: int,
    coluna: int,
) -> bool:
    """Verifica se os caracteres comparados na celula atual sao iguais."""
    indice_vertical = _indice_vertical(sequencia_vertical, linha)
    indice_horizontal = _indice_horizontal(coluna)
    return sequencia_vertical[indice_vertical] == sequencia_horizontal[indice_horizontal]


def computar_scores_candidatos(
    matriz_scores: MatrizNumerica,
    linha: int,
    coluna: int,
    penalidade_gap: float,
    penalidade_mismatch: float,
    pontuacao_match: float,
    sequencia_vertical: str,
    sequencia_horizontal: str,
) -> tuple[float, float, float]:
    """Calcula os scores candidatos de esquerda, diagonal e cima."""
    score_esquerda = float(matriz_scores[linha, coluna - 1] + penalidade_gap)

    if eh_match(sequencia_vertical, sequencia_horizontal, linha, coluna):
        score_diagonal = float(matriz_scores[linha + 1, coluna - 1] + pontuacao_match)
    else:
        score_diagonal = float(matriz_scores[linha + 1, coluna - 1] + penalidade_mismatch)

    score_cima = float(matriz_scores[linha + 1, coluna] + penalidade_gap)
    return score_esquerda, score_diagonal, score_cima
