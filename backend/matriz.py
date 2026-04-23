import numpy as np


def obter_dimensoes_matriz(sequencia_vertical, sequencia_horizontal):
    quantidade_linhas = int(len(sequencia_vertical) + 1)
    quantidade_colunas = int(len(sequencia_horizontal) + 1)
    return quantidade_linhas, quantidade_colunas


def criar_matriz(quantidade_linhas, quantidade_colunas):
    matriz = np.zeros((quantidade_linhas, quantidade_colunas))
    return matriz


def definir_gaps_horizontal(matriz, penalidade_gap):
    ultima_linha = matriz.shape[0] - 1
    for coluna in range(matriz.shape[1]):
        matriz[ultima_linha, coluna] = coluna * penalidade_gap
    return matriz


def definir_gaps_vertical(matriz, penalidade_gap):
    ultima_linha = matriz.shape[0] - 1
    for linha in range(matriz.shape[0]):
        matriz[ultima_linha - linha, 0] = linha * penalidade_gap
    return matriz


def inicializar_matriz_com_gaps(quantidade_linhas, quantidade_colunas, penalidade_gap):
    matriz = criar_matriz(quantidade_linhas, quantidade_colunas)
    matriz = definir_gaps_horizontal(matriz, penalidade_gap)
    matriz = definir_gaps_vertical(matriz, penalidade_gap)
    return matriz


def eh_match(sequencia_vertical, sequencia_horizontal, linha, coluna):
    indice_vertical = (len(sequencia_vertical) - 1) - linha
    indice_horizontal = coluna - 1
    return sequencia_vertical[indice_vertical] == sequencia_horizontal[indice_horizontal]


def computar_scores_candidatos(
    matriz_scores,
    linha,
    coluna,
    penalidade_gap,
    penalidade_mismatch,
    pontuacao_match,
    sequencia_vertical,
    sequencia_horizontal,
):
    score_esquerda = matriz_scores[linha, coluna - 1] + penalidade_gap

    if eh_match(sequencia_vertical, sequencia_horizontal, linha, coluna):
        score_diagonal = matriz_scores[linha + 1, coluna - 1] + pontuacao_match
    else:
        score_diagonal = matriz_scores[linha + 1, coluna - 1] + penalidade_mismatch

    score_cima = matriz_scores[linha + 1, coluna] + penalidade_gap
    return score_esquerda, score_diagonal, score_cima
