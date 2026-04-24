"""Orquestracao principal das etapas de alinhamento."""

import numpy as np
from numpy.typing import NDArray

from .alinhamento import rastrear_caminho
from .constantes import PONTEIRO_PARAR
from .matriz import (
    MatrizNumerica,
    computar_scores_candidatos,
    criar_matriz,
    inicializar_matriz_com_gaps,
    obter_dimensoes_matriz,
)
from .ponteiros import codificar_ponteiro, mesmo_score

MatrizPonteiros = NDArray[np.int_]


def _criar_matriz_ponteiros(
    quantidade_linhas: int,
    quantidade_colunas: int,
) -> MatrizPonteiros:
    return np.zeros((quantidade_linhas, quantidade_colunas), dtype=int)


def _preencher_matrizes(
    matriz_scores: MatrizNumerica,
    matriz_ponteiros: MatrizPonteiros,
    sequencia_vertical: str,
    sequencia_horizontal: str,
    penalidade_gap: float,
    penalidade_mismatch: float,
    pontuacao_match: float,
    usar_base_local: bool,
) -> tuple[MatrizNumerica, MatrizPonteiros]:
    """Preenche scores e ponteiros para os modos global e local."""
    quantidade_linhas, quantidade_colunas = matriz_scores.shape

    for linha in range(quantidade_linhas - 2, -1, -1):
        for coluna in range(1, quantidade_colunas):
            score_esquerda, score_diagonal, score_cima = computar_scores_candidatos(
                matriz_scores,
                linha,
                coluna,
                penalidade_gap,
                penalidade_mismatch,
                pontuacao_match,
                sequencia_vertical,
                sequencia_horizontal,
            )

            if usar_base_local:
                melhor_score = max(0.0, score_esquerda, score_diagonal, score_cima)
            else:
                melhor_score = max(score_esquerda, score_diagonal, score_cima)

            matriz_scores[linha, coluna] = melhor_score

            if usar_base_local and mesmo_score(melhor_score, 0.0):
                matriz_ponteiros[linha, coluna] = PONTEIRO_PARAR
                continue

            matriz_ponteiros[linha, coluna] = codificar_ponteiro(
                mesmo_score(score_esquerda, melhor_score),
                mesmo_score(score_diagonal, melhor_score),
                mesmo_score(score_cima, melhor_score),
            )

    return matriz_scores, matriz_ponteiros


def construir_matrizes_globais(
    sequencia_vertical: str,
    sequencia_horizontal: str,
    penalidade_gap: float,
    penalidade_mismatch: float,
    pontuacao_match: float,
) -> tuple[MatrizNumerica, MatrizPonteiros]:
    """Cria e preenche matrizes no modo de alinhamento global."""
    quantidade_linhas, quantidade_colunas = obter_dimensoes_matriz(
        sequencia_vertical,
        sequencia_horizontal,
    )
    matriz_scores = inicializar_matriz_com_gaps(
        quantidade_linhas,
        quantidade_colunas,
        penalidade_gap,
    )
    matriz_ponteiros = _criar_matriz_ponteiros(quantidade_linhas, quantidade_colunas)

    return _preencher_matrizes(
        matriz_scores,
        matriz_ponteiros,
        sequencia_vertical,
        sequencia_horizontal,
        penalidade_gap,
        penalidade_mismatch,
        pontuacao_match,
        usar_base_local=False,
    )


def construir_matrizes_locais(
    sequencia_vertical: str,
    sequencia_horizontal: str,
    penalidade_gap: float,
    penalidade_mismatch: float,
    pontuacao_match: float,
) -> tuple[MatrizNumerica, MatrizPonteiros]:
    """Cria e preenche matrizes no modo de alinhamento local."""
    quantidade_linhas, quantidade_colunas = obter_dimensoes_matriz(
        sequencia_vertical,
        sequencia_horizontal,
    )
    matriz_scores = criar_matriz(quantidade_linhas, quantidade_colunas)
    matriz_ponteiros = _criar_matriz_ponteiros(quantidade_linhas, quantidade_colunas)

    return _preencher_matrizes(
        matriz_scores,
        matriz_ponteiros,
        sequencia_vertical,
        sequencia_horizontal,
        penalidade_gap,
        penalidade_mismatch,
        pontuacao_match,
        usar_base_local=True,
    )


def smith_waterman(
    matriz_score: MatrizNumerica,
    penalidade_gap: float,
    penalidade_mismatch: float,
    pontuacao_match: float,
    sequencia_vertical: str,
    sequencia_horizontal: str,
) -> tuple[MatrizNumerica, MatrizPonteiros]:
    """Mantem API antiga e devolve matrizes de score/ponteiro locais."""
    _ = matriz_score
    return construir_matrizes_locais(
        sequencia_vertical,
        sequencia_horizontal,
        penalidade_gap,
        penalidade_mismatch,
        pontuacao_match,
    )


def executar_suite_alinhamento(
    sequencia_vertical: str,
    sequencia_horizontal: str,
    penalidade_gap: float,
    penalidade_mismatch: float,
    pontuacao_match: float,
) -> dict[str, str | float | MatrizNumerica | MatrizPonteiros]:
    """Executa pipeline completo de alinhamento global e local."""
    matriz_score_global, matriz_ponteiro_global = construir_matrizes_globais(
        sequencia_vertical,
        sequencia_horizontal,
        penalidade_gap,
        penalidade_mismatch,
        pontuacao_match,
    )
    matriz_score_local, matriz_ponteiro_local = construir_matrizes_locais(
        sequencia_vertical,
        sequencia_horizontal,
        penalidade_gap,
        penalidade_mismatch,
        pontuacao_match,
    )

    resultado_alinhamento = rastrear_caminho(
        matriz_score_local,
        matriz_ponteiro_local,
        sequencia_vertical,
        sequencia_horizontal,
        matriz_score_global,
        matriz_ponteiro_global,
    )
    resultado_alinhamento.update(
        {
            'matriz_score_global': matriz_score_global,
            'matriz_ponteiro_global': matriz_ponteiro_global,
            'matriz_score_local': matriz_score_local,
            'matriz_ponteiro_local': matriz_ponteiro_local,
        },
    )
    return resultado_alinhamento
