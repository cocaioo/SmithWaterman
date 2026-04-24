"""Rotinas de traceback e montagem dos alinhamentos finais."""

from typing import Literal

import numpy as np
from numpy.typing import NDArray

from .constantes import PREFERENCIA_DIRECOES
from .ponteiros import escolher_direcao_traceback, mesmo_score

Direcao = Literal['esquerda', 'diagonal', 'cima']
MatrizNumerica = NDArray[np.float64]


def _indice_vertical(sequencia_vertical: str, linha: int) -> int:
    return len(sequencia_vertical) - 1 - linha


def _indice_horizontal(coluna: int) -> int:
    return coluna - 1


def _coletar_candidatos_fallback(
    matriz_scores: MatrizNumerica,
    linha: int,
    coluna: int,
) -> list[tuple[Direcao, float]]:
    ultima_linha = matriz_scores.shape[0] - 1
    candidatos: list[tuple[Direcao, float]] = []

    if coluna - 1 >= 0:
        candidatos.append(('esquerda', float(matriz_scores[linha, coluna - 1])))

    if linha + 1 <= ultima_linha and coluna - 1 >= 0:
        candidatos.append(('diagonal', float(matriz_scores[linha + 1, coluna - 1])))

    if linha + 1 <= ultima_linha:
        candidatos.append(('cima', float(matriz_scores[linha + 1, coluna])))

    return candidatos


def _escolher_direcao_fallback(candidatos: list[tuple[Direcao, float]]) -> Direcao | None:
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


def construir_alinhamento_da_posicao(
    matriz_scores: MatrizNumerica,
    matriz_ponteiros: NDArray[np.int_],
    sequencia_vertical: str,
    sequencia_horizontal: str,
    linha_inicio: int,
    coluna_inicio: int,
    parar_em_zero: bool,
    completar_bordas: bool,
) -> tuple[str, str]:
    """Rastreia o caminho de uma posicao inicial e monta duas sequencias alinhadas."""
    alinhada_vertical: list[str] = []
    alinhada_horizontal: list[str] = []

    linha = linha_inicio
    coluna = coluna_inicio
    ultima_linha = matriz_scores.shape[0] - 1

    while 0 <= linha <= ultima_linha and coluna >= 0:
        if parar_em_zero and matriz_scores[linha, coluna] <= 0:
            break

        if linha == ultima_linha and coluna == 0:
            break

        if coluna == 0:
            if not completar_bordas:
                break

            indice_vertical = _indice_vertical(sequencia_vertical, linha)
            alinhada_vertical.append(sequencia_vertical[indice_vertical])
            alinhada_horizontal.append('-')
            linha += 1
            continue

        if linha == ultima_linha:
            if not completar_bordas:
                break

            indice_horizontal = _indice_horizontal(coluna)
            alinhada_vertical.append('-')
            alinhada_horizontal.append(sequencia_horizontal[indice_horizontal])
            coluna -= 1
            continue

        valor_ponteiro = int(matriz_ponteiros[linha, coluna])
        direcao = escolher_direcao_traceback(valor_ponteiro, matriz_scores, linha, coluna)

        if direcao is None:
            if not completar_bordas:
                break

            direcao = _escolher_direcao_fallback(
                _coletar_candidatos_fallback(matriz_scores, linha, coluna),
            )

            if direcao is None:
                break

        indice_vertical = _indice_vertical(sequencia_vertical, linha)
        indice_horizontal = _indice_horizontal(coluna)

        if direcao == 'diagonal':
            alinhada_vertical.append(sequencia_vertical[indice_vertical])
            alinhada_horizontal.append(sequencia_horizontal[indice_horizontal])
            linha += 1
            coluna -= 1
        elif direcao == 'esquerda':
            alinhada_vertical.append('-')
            alinhada_horizontal.append(sequencia_horizontal[indice_horizontal])
            coluna -= 1
        elif direcao == 'cima':
            alinhada_vertical.append(sequencia_vertical[indice_vertical])
            alinhada_horizontal.append('-')
            linha += 1

    alinhada_vertical.reverse()
    alinhada_horizontal.reverse()
    return ''.join(alinhada_vertical), ''.join(alinhada_horizontal)


def encontrar_melhor_posicao_local(matriz_score_local: MatrizNumerica) -> tuple[int, int]:
    """Retorna a coordenada da celula com maior score local."""
    linha, coluna = np.unravel_index(np.argmax(matriz_score_local), matriz_score_local.shape)
    return int(linha), int(coluna)


def alinhamento_global(
    matriz_score_global: MatrizNumerica,
    matriz_ponteiro_global: NDArray[np.int_],
    sequencia_vertical: str,
    sequencia_horizontal: str,
) -> tuple[str, str]:
    """Monta o alinhamento global completo."""
    return construir_alinhamento_da_posicao(
        matriz_score_global,
        matriz_ponteiro_global,
        sequencia_vertical,
        sequencia_horizontal,
        linha_inicio=0,
        coluna_inicio=matriz_score_global.shape[1] - 1,
        parar_em_zero=False,
        completar_bordas=True,
    )


def alinhamento_local(
    matriz_score_local: MatrizNumerica,
    matriz_ponteiro_local: NDArray[np.int_],
    sequencia_vertical: str,
    sequencia_horizontal: str,
) -> tuple[str, str]:
    """Monta alinhamento local a partir da melhor celula da matriz local."""
    linha_inicio, coluna_inicio = encontrar_melhor_posicao_local(matriz_score_local)
    return construir_alinhamento_da_posicao(
        matriz_score_local,
        matriz_ponteiro_local,
        sequencia_vertical,
        sequencia_horizontal,
        linha_inicio,
        coluna_inicio,
        parar_em_zero=False,
        completar_bordas=True,
    )


def alinhamento_melhor_score(
    matriz_score_local: MatrizNumerica,
    matriz_ponteiro_local: NDArray[np.int_],
    sequencia_vertical: str,
    sequencia_horizontal: str,
) -> tuple[str, str, float]:
    """Retorna o alinhamento local e o melhor score associado."""
    linha_inicio, coluna_inicio = encontrar_melhor_posicao_local(matriz_score_local)
    melhor_score = float(matriz_score_local[linha_inicio, coluna_inicio])

    alinhada_vertical, alinhada_horizontal = construir_alinhamento_da_posicao(
        matriz_score_local,
        matriz_ponteiro_local,
        sequencia_vertical,
        sequencia_horizontal,
        linha_inicio,
        coluna_inicio,
        parar_em_zero=False,
        completar_bordas=True,
    )
    return alinhada_vertical, alinhada_horizontal, melhor_score


def rastrear_caminho(
    matriz_score_local: MatrizNumerica,
    matriz_ponteiro_local: NDArray[np.int_],
    sequencia_vertical: str,
    sequencia_horizontal: str,
    matriz_score_global: MatrizNumerica | None = None,
    matriz_ponteiro_global: NDArray[np.int_] | None = None,
) -> dict[str, str | float]:
    """Consolida alinhamentos global/local e o melhor score em um unico dicionario."""
    if matriz_score_global is not None and matriz_ponteiro_global is not None:
        vertical_global, horizontal_global = alinhamento_global(
            matriz_score_global,
            matriz_ponteiro_global,
            sequencia_vertical,
            sequencia_horizontal,
        )
    else:
        vertical_global, horizontal_global = '', ''

    vertical_local, horizontal_local = alinhamento_local(
        matriz_score_local,
        matriz_ponteiro_local,
        sequencia_vertical,
        sequencia_horizontal,
    )
    melhor_vertical, melhor_horizontal, melhor_score = alinhamento_melhor_score(
        matriz_score_local,
        matriz_ponteiro_local,
        sequencia_vertical,
        sequencia_horizontal,
    )

    return {
        'vertical_global': vertical_global,
        'horizontal_global': horizontal_global,
        'vertical_local': vertical_local,
        'horizontal_local': horizontal_local,
        'melhor_vertical': melhor_vertical,
        'melhor_horizontal': melhor_horizontal,
        'melhor_score': melhor_score,
    }
