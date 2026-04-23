import numpy as np

from .constantes import (
    PONTEIRO_CIMA,
    PONTEIRO_DIAGONAL,
    PONTEIRO_DIAGONAL_CIMA,
    PONTEIRO_ESQUERDA,
    PONTEIRO_ESQUERDA_CIMA,
    PONTEIRO_ESQUERDA_DIAGONAL,
    PONTEIRO_PARAR,
    PONTEIRO_TODOS,
    TOLERANCIA,
)


def mesmo_score(valor_a, valor_b):
    return np.isclose(valor_a, valor_b, atol=TOLERANCIA)


def codificar_ponteiro(vem_esquerda, vem_diagonal, vem_cima):
    if vem_esquerda and vem_diagonal and vem_cima:
        return PONTEIRO_TODOS
    if vem_esquerda and vem_diagonal:
        return PONTEIRO_ESQUERDA_DIAGONAL
    if vem_esquerda and vem_cima:
        return PONTEIRO_ESQUERDA_CIMA
    if vem_diagonal and vem_cima:
        return PONTEIRO_DIAGONAL_CIMA
    if vem_esquerda:
        return PONTEIRO_ESQUERDA
    if vem_diagonal:
        return PONTEIRO_DIAGONAL
    if vem_cima:
        return PONTEIRO_CIMA
    return PONTEIRO_PARAR


def decodificar_ponteiro(valor_ponteiro):
    pode_ir_esquerda = valor_ponteiro in (PONTEIRO_ESQUERDA, PONTEIRO_ESQUERDA_DIAGONAL, PONTEIRO_ESQUERDA_CIMA, PONTEIRO_TODOS)
    pode_ir_diagonal = valor_ponteiro in (PONTEIRO_DIAGONAL, PONTEIRO_ESQUERDA_DIAGONAL, PONTEIRO_DIAGONAL_CIMA, PONTEIRO_TODOS)
    pode_ir_cima = valor_ponteiro in (PONTEIRO_CIMA, PONTEIRO_ESQUERDA_CIMA, PONTEIRO_DIAGONAL_CIMA, PONTEIRO_TODOS)
    return pode_ir_esquerda, pode_ir_diagonal, pode_ir_cima


def escolher_direcao_traceback(valor_ponteiro, matriz_scores, linha, coluna):
    pode_ir_esquerda, pode_ir_diagonal, pode_ir_cima = decodificar_ponteiro(valor_ponteiro)

    candidatos = []

    if pode_ir_esquerda and coluna - 1 >= 0:
        candidatos.append(('esquerda', matriz_scores[linha, coluna - 1]))

    if pode_ir_diagonal and linha + 1 < matriz_scores.shape[0] and coluna - 1 >= 0:
        candidatos.append(('diagonal', matriz_scores[linha + 1, coluna - 1]))

    if pode_ir_cima and linha + 1 < matriz_scores.shape[0]:
        candidatos.append(('cima', matriz_scores[linha + 1, coluna]))

    if not candidatos:
        return None

    maior_valor_vizinho = max(valor for _, valor in candidatos)
    melhores_direcoes = [direcao for direcao, valor in candidatos if valor == maior_valor_vizinho]

    for direcao_preferencial in ('diagonal', 'cima', 'esquerda'):
        if direcao_preferencial in melhores_direcoes:
            return direcao_preferencial

    return melhores_direcoes[0]
