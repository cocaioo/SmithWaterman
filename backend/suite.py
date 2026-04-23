import numpy as np

from .constantes import PONTEIRO_PARAR
from .alinhamento import rastrear_caminho
from .matriz import (
    computar_scores_candidatos,
    criar_matriz,
    inicializar_matriz_com_gaps,
    obter_dimensoes_matriz,
)
from .ponteiros import codificar_ponteiro, mesmo_score


def construir_matrizes_globais(sequencia_vertical, sequencia_horizontal, penalidade_gap, penalidade_mismatch, pontuacao_match):
    quantidade_linhas, quantidade_colunas = obter_dimensoes_matriz(sequencia_vertical, sequencia_horizontal)
    matriz_scores = inicializar_matriz_com_gaps(quantidade_linhas, quantidade_colunas, penalidade_gap)
    matriz_ponteiros = np.zeros((quantidade_linhas, quantidade_colunas), dtype=int)

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

            melhor_score = max(score_esquerda, score_diagonal, score_cima)
            matriz_scores[linha, coluna] = melhor_score

            matriz_ponteiros[linha, coluna] = codificar_ponteiro(
                mesmo_score(score_esquerda, melhor_score),
                mesmo_score(score_diagonal, melhor_score),
                mesmo_score(score_cima, melhor_score),
            )

    return matriz_scores, matriz_ponteiros


def construir_matrizes_locais(sequencia_vertical, sequencia_horizontal, penalidade_gap, penalidade_mismatch, pontuacao_match):
    quantidade_linhas, quantidade_colunas = obter_dimensoes_matriz(sequencia_vertical, sequencia_horizontal)
    matriz_scores = criar_matriz(quantidade_linhas, quantidade_colunas)
    matriz_ponteiros = np.zeros((quantidade_linhas, quantidade_colunas), dtype=int)

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

            melhor_score = max(0, score_esquerda, score_diagonal, score_cima)
            matriz_scores[linha, coluna] = melhor_score

            if mesmo_score(melhor_score, 0.0):
                matriz_ponteiros[linha, coluna] = PONTEIRO_PARAR
                continue

            matriz_ponteiros[linha, coluna] = codificar_ponteiro(
                mesmo_score(score_esquerda, melhor_score),
                mesmo_score(score_diagonal, melhor_score),
                mesmo_score(score_cima, melhor_score),
            )

    return matriz_scores, matriz_ponteiros


def smith_waterman(matriz_score, penalidade_gap, penalidade_mismatch, pontuacao_match, sequencia_vertical, sequencia_horizontal):
    quantidade_linhas, quantidade_colunas = matriz_score.shape
    _ = quantidade_linhas, quantidade_colunas
    matriz_score_local, matriz_ponteiro_local = construir_matrizes_locais(
        sequencia_vertical,
        sequencia_horizontal,
        penalidade_gap,
        penalidade_mismatch,
        pontuacao_match,
    )
    return matriz_score_local, matriz_ponteiro_local


def executar_suite_alinhamento(sequencia_vertical, sequencia_horizontal, penalidade_gap, penalidade_mismatch, pontuacao_match):
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

    resultado_alinhamento['matriz_score_global'] = matriz_score_global
    resultado_alinhamento['matriz_ponteiro_global'] = matriz_ponteiro_global
    resultado_alinhamento['matriz_score_local'] = matriz_score_local
    resultado_alinhamento['matriz_ponteiro_local'] = matriz_ponteiro_local

    return resultado_alinhamento
