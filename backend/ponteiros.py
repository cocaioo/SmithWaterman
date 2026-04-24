"""Codificacao e escolha de direcoes para traceback."""

from typing import Literal

import numpy as np
from numpy.typing import NDArray

from .constantes import (
    PONTEIRO_CIMA,
    PONTEIRO_DIAGONAL,
    PONTEIRO_DIAGONAL_CIMA,
    PONTEIRO_ESQUERDA,
    PONTEIRO_ESQUERDA_CIMA,
    PONTEIRO_ESQUERDA_DIAGONAL,
    PONTEIRO_PARAR,
    PONTEIRO_TODOS,
    PREFERENCIA_DIRECOES,
    TOLERANCIA,
)

Direcao = Literal['esquerda', 'diagonal', 'cima']
MatrizNumerica = NDArray[np.float64]

_MAPA_MOVIMENTOS_PARA_PONTEIRO: dict[tuple[bool, bool, bool], int] = {
    (False, False, False): PONTEIRO_PARAR,
    (True, False, False): PONTEIRO_ESQUERDA,
    (False, True, False): PONTEIRO_DIAGONAL,
    (False, False, True): PONTEIRO_CIMA,
    (True, True, False): PONTEIRO_ESQUERDA_DIAGONAL,
    (True, False, True): PONTEIRO_ESQUERDA_CIMA,
    (False, True, True): PONTEIRO_DIAGONAL_CIMA,
    (True, True, True): PONTEIRO_TODOS,
}

_MAPA_PONTEIRO_PARA_MOVIMENTOS: dict[int, tuple[bool, bool, bool]] = {
    ponteiro: movimentos
    for movimentos, ponteiro in _MAPA_MOVIMENTOS_PARA_PONTEIRO.items()
}


def mesmo_score(valor_a: float, valor_b: float) -> bool:
    """Compara floats usando tolerancia numerica global do projeto."""
    return bool(np.isclose(valor_a, valor_b, atol=TOLERANCIA))


def codificar_ponteiro(vem_esquerda: bool, vem_diagonal: bool, vem_cima: bool) -> int:
    """Converte flags de direcao em um unico codigo de ponteiro."""
    return _MAPA_MOVIMENTOS_PARA_PONTEIRO[(vem_esquerda, vem_diagonal, vem_cima)]


def decodificar_ponteiro(valor_ponteiro: int) -> tuple[bool, bool, bool]:
    """Converte o codigo de ponteiro nas direcoes permitidas."""
    return _MAPA_PONTEIRO_PARA_MOVIMENTOS.get(valor_ponteiro, (False, False, False))


def _coletar_candidatos_direcao(
    matriz_scores: MatrizNumerica,
    linha: int,
    coluna: int,
    pode_ir_esquerda: bool,
    pode_ir_diagonal: bool,
    pode_ir_cima: bool,
) -> list[tuple[Direcao, float]]:
    candidatos: list[tuple[Direcao, float]] = []

    if pode_ir_esquerda and coluna - 1 >= 0:
        candidatos.append(('esquerda', float(matriz_scores[linha, coluna - 1])))

    if pode_ir_diagonal and linha + 1 < matriz_scores.shape[0] and coluna - 1 >= 0:
        candidatos.append(('diagonal', float(matriz_scores[linha + 1, coluna - 1])))

    if pode_ir_cima and linha + 1 < matriz_scores.shape[0]:
        candidatos.append(('cima', float(matriz_scores[linha + 1, coluna])))

    return candidatos


def escolher_direcao_traceback(
    valor_ponteiro: int,
    matriz_scores: MatrizNumerica,
    linha: int,
    coluna: int,
) -> Direcao | None:
    """Escolhe a melhor direcao para traceback com desempate previsivel."""
    pode_ir_esquerda, pode_ir_diagonal, pode_ir_cima = decodificar_ponteiro(valor_ponteiro)
    candidatos = _coletar_candidatos_direcao(
        matriz_scores,
        linha,
        coluna,
        pode_ir_esquerda,
        pode_ir_diagonal,
        pode_ir_cima,
    )

    if not candidatos:
        return None

    maior_valor_vizinho = max(valor for _, valor in candidatos)
    melhores_direcoes = [
        direcao
        for direcao, valor in candidatos
        if mesmo_score(valor, maior_valor_vizinho)
    ]

    for direcao_preferencial in PREFERENCIA_DIRECOES:
        if direcao_preferencial in melhores_direcoes:
            return direcao_preferencial

    return melhores_direcoes[0]
