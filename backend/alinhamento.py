"""Backend completo do algoritmo Smith-Waterman em um unico modulo."""

from typing import Literal

import numpy as np
from numpy.typing import NDArray

PONTEIRO_PARAR = 0
PONTEIRO_ESQUERDA = 1
PONTEIRO_DIAGONAL = 2
PONTEIRO_CIMA = 3
PONTEIRO_ESQUERDA_DIAGONAL = 4
PONTEIRO_ESQUERDA_CIMA = 5
PONTEIRO_DIAGONAL_CIMA = 6
PONTEIRO_TODOS = 7

TOLERANCIA = 1e-9
PREFERENCIA_DIRECOES = ('diagonal', 'cima', 'esquerda')

Direcao = Literal['esquerda', 'diagonal', 'cima']
MatrizNumerica = NDArray[np.float64]
MatrizPonteiros = NDArray[np.int_]

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


def _indice_vertical(sequencia_vertical: str, linha: int) -> int:
    return len(sequencia_vertical) - 1 - linha


def _indice_horizontal(coluna: int) -> int:
    return coluna - 1


def _obter_dimensoes_matriz(
    sequencia_vertical: str,
    sequencia_horizontal: str,
) -> tuple[int, int]:
    return len(sequencia_vertical) + 1, len(sequencia_horizontal) + 1


def _criar_matriz(quantidade_linhas: int, quantidade_colunas: int) -> MatrizNumerica:
    return np.zeros((quantidade_linhas, quantidade_colunas), dtype=float)


def _definir_gaps_horizontal(matriz: MatrizNumerica, penalidade_gap: float) -> None:
    ultima_linha = matriz.shape[0] - 1
    for coluna in range(matriz.shape[1]):
        matriz[ultima_linha, coluna] = coluna * penalidade_gap


def _definir_gaps_vertical(matriz: MatrizNumerica, penalidade_gap: float) -> None:
    ultima_linha = matriz.shape[0] - 1
    for deslocamento in range(matriz.shape[0]):
        matriz[ultima_linha - deslocamento, 0] = deslocamento * penalidade_gap


def _inicializar_matriz_com_gaps(
    quantidade_linhas: int,
    quantidade_colunas: int,
    penalidade_gap: float,
) -> MatrizNumerica:
    matriz = _criar_matriz(quantidade_linhas, quantidade_colunas)
    _definir_gaps_horizontal(matriz, penalidade_gap)
    _definir_gaps_vertical(matriz, penalidade_gap)
    return matriz


def _eh_match(
    sequencia_vertical: str,
    sequencia_horizontal: str,
    linha: int,
    coluna: int,
) -> bool:
    indice_vertical = _indice_vertical(sequencia_vertical, linha)
    indice_horizontal = _indice_horizontal(coluna)
    return sequencia_vertical[indice_vertical] == sequencia_horizontal[indice_horizontal]


def _computar_scores_candidatos(
    matriz_scores: MatrizNumerica,
    linha: int,
    coluna: int,
    penalidade_gap: float,
    penalidade_mismatch: float,
    pontuacao_match: float,
    sequencia_vertical: str,
    sequencia_horizontal: str,
) -> tuple[float, float, float]:
    score_esquerda = float(matriz_scores[linha, coluna - 1] + penalidade_gap)

    if _eh_match(sequencia_vertical, sequencia_horizontal, linha, coluna):
        score_diagonal = float(matriz_scores[linha + 1, coluna - 1] + pontuacao_match)
    else:
        score_diagonal = float(matriz_scores[linha + 1, coluna - 1] + penalidade_mismatch)

    score_cima = float(matriz_scores[linha + 1, coluna] + penalidade_gap)
    return score_esquerda, score_diagonal, score_cima


def _mesmo_score(valor_a: float, valor_b: float) -> bool:
    return bool(np.isclose(valor_a, valor_b, atol=TOLERANCIA))


def _codificar_ponteiro(vem_esquerda: bool, vem_diagonal: bool, vem_cima: bool) -> int:
    return _MAPA_MOVIMENTOS_PARA_PONTEIRO[(vem_esquerda, vem_diagonal, vem_cima)]


def _decodificar_ponteiro(valor_ponteiro: int) -> tuple[bool, bool, bool]:
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


def _escolher_direcao_traceback(
    valor_ponteiro: int,
    matriz_scores: MatrizNumerica,
    linha: int,
    coluna: int,
) -> Direcao | None:
    pode_ir_esquerda, pode_ir_diagonal, pode_ir_cima = _decodificar_ponteiro(valor_ponteiro)
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
        if _mesmo_score(valor, maior_valor_vizinho)
    ]

    for direcao_preferencial in PREFERENCIA_DIRECOES:
        if direcao_preferencial in melhores_direcoes:
            return direcao_preferencial

    return melhores_direcoes[0]


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
        if _mesmo_score(valor, maior_valor_vizinho)
    ]

    for direcao_preferencial in PREFERENCIA_DIRECOES:
        if direcao_preferencial in melhores_direcoes:
            return direcao_preferencial

    return melhores_direcoes[0]


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
    quantidade_linhas, quantidade_colunas = matriz_scores.shape

    for linha in range(quantidade_linhas - 2, -1, -1):
        for coluna in range(1, quantidade_colunas):
            score_esquerda, score_diagonal, score_cima = _computar_scores_candidatos(
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

            if usar_base_local and _mesmo_score(melhor_score, 0.0):
                matriz_ponteiros[linha, coluna] = PONTEIRO_PARAR
                continue

            matriz_ponteiros[linha, coluna] = _codificar_ponteiro(
                _mesmo_score(score_esquerda, melhor_score),
                _mesmo_score(score_diagonal, melhor_score),
                _mesmo_score(score_cima, melhor_score),
            )

    return matriz_scores, matriz_ponteiros


def construir_matrizes_globais(
    sequencia_vertical: str,
    sequencia_horizontal: str,
    penalidade_gap: float,
    penalidade_mismatch: float,
    pontuacao_match: float,
) -> tuple[MatrizNumerica, MatrizPonteiros]:
    quantidade_linhas, quantidade_colunas = _obter_dimensoes_matriz(
        sequencia_vertical,
        sequencia_horizontal,
    )
    matriz_scores = _inicializar_matriz_com_gaps(
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
    quantidade_linhas, quantidade_colunas = _obter_dimensoes_matriz(
        sequencia_vertical,
        sequencia_horizontal,
    )
    matriz_scores = _criar_matriz(quantidade_linhas, quantidade_colunas)
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


def _construir_alinhamento_da_posicao(
    matriz_scores: MatrizNumerica,
    matriz_ponteiros: MatrizPonteiros,
    sequencia_vertical: str,
    sequencia_horizontal: str,
    linha_inicio: int,
    coluna_inicio: int,
    parar_em_zero: bool,
    completar_bordas: bool,
) -> tuple[str, str]:
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
        direcao = _escolher_direcao_traceback(valor_ponteiro, matriz_scores, linha, coluna)

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


def _encontrar_melhor_posicao_local(matriz_score_local: MatrizNumerica) -> tuple[int, int]:
    linha, coluna = np.unravel_index(np.argmax(matriz_score_local), matriz_score_local.shape)
    return int(linha), int(coluna)


def _alinhamento_global(
    matriz_score_global: MatrizNumerica,
    matriz_ponteiro_global: MatrizPonteiros,
    sequencia_vertical: str,
    sequencia_horizontal: str,
) -> tuple[str, str]:
    return _construir_alinhamento_da_posicao(
        matriz_score_global,
        matriz_ponteiro_global,
        sequencia_vertical,
        sequencia_horizontal,
        linha_inicio=0,
        coluna_inicio=matriz_score_global.shape[1] - 1,
        parar_em_zero=False,
        completar_bordas=True,
    )


def _alinhamento_local(
    matriz_score_local: MatrizNumerica,
    matriz_ponteiro_local: MatrizPonteiros,
    sequencia_vertical: str,
    sequencia_horizontal: str,
) -> tuple[str, str]:
    linha_inicio, coluna_inicio = _encontrar_melhor_posicao_local(matriz_score_local)
    return _construir_alinhamento_da_posicao(
        matriz_score_local,
        matriz_ponteiro_local,
        sequencia_vertical,
        sequencia_horizontal,
        linha_inicio,
        coluna_inicio,
        parar_em_zero=False,
        completar_bordas=True,
    )


def _alinhamento_melhor_score(
    matriz_score_local: MatrizNumerica,
    matriz_ponteiro_local: MatrizPonteiros,
    sequencia_vertical: str,
    sequencia_horizontal: str,
) -> tuple[str, str, float]:
    linha_inicio, coluna_inicio = _encontrar_melhor_posicao_local(matriz_score_local)
    melhor_score = float(matriz_score_local[linha_inicio, coluna_inicio])

    alinhada_vertical, alinhada_horizontal = _construir_alinhamento_da_posicao(
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


def _rastrear_caminho(
    matriz_score_local: MatrizNumerica,
    matriz_ponteiro_local: MatrizPonteiros,
    sequencia_vertical: str,
    sequencia_horizontal: str,
    matriz_score_global: MatrizNumerica | None = None,
    matriz_ponteiro_global: MatrizPonteiros | None = None,
) -> dict[str, str | float]:
    if matriz_score_global is not None and matriz_ponteiro_global is not None:
        vertical_global, horizontal_global = _alinhamento_global(
            matriz_score_global,
            matriz_ponteiro_global,
            sequencia_vertical,
            sequencia_horizontal,
        )
    else:
        vertical_global, horizontal_global = '', ''

    vertical_local, horizontal_local = _alinhamento_local(
        matriz_score_local,
        matriz_ponteiro_local,
        sequencia_vertical,
        sequencia_horizontal,
    )
    melhor_vertical, melhor_horizontal, melhor_score = _alinhamento_melhor_score(
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


def smith_waterman(
    matriz_score: MatrizNumerica,
    penalidade_gap: float,
    penalidade_mismatch: float,
    pontuacao_match: float,
    sequencia_vertical: str,
    sequencia_horizontal: str,
) -> tuple[MatrizNumerica, MatrizPonteiros]:
    """Mantem API antiga e devolve as matrizes de score/ponteiro locais."""
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
    """Executa o fluxo completo e retorna tudo o que UI e terminal precisam."""
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

    resultado_alinhamento = _rastrear_caminho(
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
