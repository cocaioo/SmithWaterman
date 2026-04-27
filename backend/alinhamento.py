"""Backend completo do algoritmo Smith-Waterman em um unico modulo."""

from typing import Literal

import numpy as np
from numpy.typing import NDArray

TOLERANCIA = 1e-9
PREFERENCIA_DIRECOES = ('diagonal', 'cima', 'esquerda')

Direcao = Literal['esquerda', 'diagonal', 'cima']
MatrizNumerica = NDArray[np.float64]


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


def _direcoes_validas_para_score_atual(
    matriz_scores: MatrizNumerica,
    linha: int,
    coluna: int,
    penalidade_gap: float,
    penalidade_mismatch: float,
    pontuacao_match: float,
    sequencia_vertical: str,
    sequencia_horizontal: str,
) -> list[Direcao]:
    """Retorna as direcoes que realmente geram o score da celula atual."""
    score_atual = float(matriz_scores[linha, coluna])
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

    direcoes_validas: list[Direcao] = []
    if _mesmo_score(score_esquerda, score_atual):
        direcoes_validas.append('esquerda')
    if _mesmo_score(score_diagonal, score_atual):
        direcoes_validas.append('diagonal')
    if _mesmo_score(score_cima, score_atual):
        direcoes_validas.append('cima')

    return direcoes_validas


def _coletar_candidatos_direcao(
    matriz_scores: MatrizNumerica,
    linha: int,
    coluna: int,
    direcoes_validas: list[Direcao],
) -> list[tuple[Direcao, float]]:
    """Coleta apenas os vizinhos das direcoes validas para traceback."""
    candidatos: list[tuple[Direcao, float]] = []
    conjunto_direcoes = set(direcoes_validas)

    if 'esquerda' in conjunto_direcoes and coluna - 1 >= 0:
        candidatos.append(('esquerda', float(matriz_scores[linha, coluna - 1])))

    if (
        'diagonal' in conjunto_direcoes
        and linha + 1 < matriz_scores.shape[0]
        and coluna - 1 >= 0
    ):
        candidatos.append(('diagonal', float(matriz_scores[linha + 1, coluna - 1])))

    if 'cima' in conjunto_direcoes and linha + 1 < matriz_scores.shape[0]:
        candidatos.append(('cima', float(matriz_scores[linha + 1, coluna])))

    return candidatos


def _coletar_candidatos_fallback(
    matriz_scores: MatrizNumerica,
    linha: int,
    coluna: int,
) -> list[tuple[Direcao, float]]:
    """Fallback defensivo quando nao for possivel inferir direcao por score."""
    ultima_linha = matriz_scores.shape[0] - 1
    candidatos: list[tuple[Direcao, float]] = []

    if coluna - 1 >= 0:
        candidatos.append(('esquerda', float(matriz_scores[linha, coluna - 1])))

    if linha + 1 <= ultima_linha and coluna - 1 >= 0:
        candidatos.append(('diagonal', float(matriz_scores[linha + 1, coluna - 1])))

    if linha + 1 <= ultima_linha:
        candidatos.append(('cima', float(matriz_scores[linha + 1, coluna])))

    return candidatos


def _escolher_direcao_com_desempate(candidatos: list[tuple[Direcao, float]]) -> Direcao | None:
    """Mantem o desempate atual: maior vizinho e depois preferencia fixa."""
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


def _escolher_direcao_traceback(
    matriz_scores: MatrizNumerica,
    linha: int,
    coluna: int,
    penalidade_gap: float,
    penalidade_mismatch: float,
    pontuacao_match: float,
    sequencia_vertical: str,
    sequencia_horizontal: str,
) -> Direcao | None:
    direcoes_validas = _direcoes_validas_para_score_atual(
        matriz_scores,
        linha,
        coluna,
        penalidade_gap,
        penalidade_mismatch,
        pontuacao_match,
        sequencia_vertical,
        sequencia_horizontal,
    )
    candidatos = _coletar_candidatos_direcao(
        matriz_scores,
        linha,
        coluna,
        direcoes_validas,
    )
    return _escolher_direcao_com_desempate(candidatos)


def _preencher_matriz_scores(
    matriz_scores: MatrizNumerica,
    sequencia_vertical: str,
    sequencia_horizontal: str,
    penalidade_gap: float,
    penalidade_mismatch: float,
    pontuacao_match: float,
    usar_base_local: bool,
) -> MatrizNumerica:
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

    return matriz_scores


def construir_matriz_global(
    sequencia_vertical: str,
    sequencia_horizontal: str,
    penalidade_gap: float,
    penalidade_mismatch: float,
    pontuacao_match: float,
) -> MatrizNumerica:
    quantidade_linhas, quantidade_colunas = _obter_dimensoes_matriz(
        sequencia_vertical,
        sequencia_horizontal,
    )
    matriz_scores = _inicializar_matriz_com_gaps(
        quantidade_linhas,
        quantidade_colunas,
        penalidade_gap,
    )
    return _preencher_matriz_scores(
        matriz_scores,
        sequencia_vertical,
        sequencia_horizontal,
        penalidade_gap,
        penalidade_mismatch,
        pontuacao_match,
        usar_base_local=False,
    )


def construir_matriz_local(
    sequencia_vertical: str,
    sequencia_horizontal: str,
    penalidade_gap: float,
    penalidade_mismatch: float,
    pontuacao_match: float,
) -> MatrizNumerica:
    quantidade_linhas, quantidade_colunas = _obter_dimensoes_matriz(
        sequencia_vertical,
        sequencia_horizontal,
    )
    matriz_scores = _criar_matriz(quantidade_linhas, quantidade_colunas)
    return _preencher_matriz_scores(
        matriz_scores,
        sequencia_vertical,
        sequencia_horizontal,
        penalidade_gap,
        penalidade_mismatch,
        pontuacao_match,
        usar_base_local=True,
    )


def _construir_alinhamento_da_posicao(
    matriz_scores: MatrizNumerica,
    sequencia_vertical: str,
    sequencia_horizontal: str,
    penalidade_gap: float,
    penalidade_mismatch: float,
    pontuacao_match: float,
    linha_inicio: int,
    coluna_inicio: int,
    parar_em_zero: bool,
    completar_bordas: bool,
) -> tuple[str, str]:
    """Constroi alinhamento caminhando da celula inicial ate a condicao de parada."""
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

        direcao = _escolher_direcao_traceback(
            matriz_scores,
            linha,
            coluna,
            penalidade_gap,
            penalidade_mismatch,
            pontuacao_match,
            sequencia_vertical,
            sequencia_horizontal,
        )

        if direcao is None:
            if not completar_bordas:
                break

            direcao = _escolher_direcao_com_desempate(
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
    sequencia_vertical: str,
    sequencia_horizontal: str,
    penalidade_gap: float,
    penalidade_mismatch: float,
    pontuacao_match: float,
) -> tuple[str, str]:
    return _construir_alinhamento_da_posicao(
        matriz_score_global,
        sequencia_vertical,
        sequencia_horizontal,
        penalidade_gap,
        penalidade_mismatch,
        pontuacao_match,
        linha_inicio=0,
        coluna_inicio=matriz_score_global.shape[1] - 1,
        parar_em_zero=False,
        completar_bordas=True,
    )


def _alinhamento_local(
    matriz_score_local: MatrizNumerica,
    sequencia_vertical: str,
    sequencia_horizontal: str,
    penalidade_gap: float,
    penalidade_mismatch: float,
    pontuacao_match: float,
) -> tuple[str, str]:
    linha_inicio, coluna_inicio = _encontrar_melhor_posicao_local(matriz_score_local)
    return _construir_alinhamento_da_posicao(
        matriz_score_local,
        sequencia_vertical,
        sequencia_horizontal,
        penalidade_gap,
        penalidade_mismatch,
        pontuacao_match,
        linha_inicio,
        coluna_inicio,
        parar_em_zero=True,
        completar_bordas=False,
    )


def _alinhamento_melhor_score(
    matriz_score_local: MatrizNumerica,
    sequencia_vertical: str,
    sequencia_horizontal: str,
    penalidade_gap: float,
    penalidade_mismatch: float,
    pontuacao_match: float,
) -> tuple[str, str, float]:
    linha_inicio, coluna_inicio = _encontrar_melhor_posicao_local(matriz_score_local)
    melhor_score = float(matriz_score_local[linha_inicio, coluna_inicio])

    alinhada_vertical, alinhada_horizontal = _construir_alinhamento_da_posicao(
        matriz_score_local,
        sequencia_vertical,
        sequencia_horizontal,
        penalidade_gap,
        penalidade_mismatch,
        pontuacao_match,
        linha_inicio,
        coluna_inicio,
        parar_em_zero=True,
        completar_bordas=False,
    )
    return alinhada_vertical, alinhada_horizontal, melhor_score


def _rastrear_caminho(
    matriz_score_local: MatrizNumerica,
    sequencia_vertical: str,
    sequencia_horizontal: str,
    penalidade_gap: float,
    penalidade_mismatch: float,
    pontuacao_match: float,
    matriz_score_global: MatrizNumerica | None = None,
) -> dict[str, str | float]:
    if matriz_score_global is not None:
        vertical_global, horizontal_global = _alinhamento_global(
            matriz_score_global,
            sequencia_vertical,
            sequencia_horizontal,
            penalidade_gap,
            penalidade_mismatch,
            pontuacao_match,
        )
    else:
        vertical_global, horizontal_global = '', ''

    vertical_local, horizontal_local = _alinhamento_local(
        matriz_score_local,
        sequencia_vertical,
        sequencia_horizontal,
        penalidade_gap,
        penalidade_mismatch,
        pontuacao_match,
    )
    melhor_vertical, melhor_horizontal, melhor_score = _alinhamento_melhor_score(
        matriz_score_local,
        sequencia_vertical,
        sequencia_horizontal,
        penalidade_gap,
        penalidade_mismatch,
        pontuacao_match,
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
) -> MatrizNumerica:
    """Mantem API antiga e devolve a matriz de score local."""
    _ = matriz_score
    return construir_matriz_local(
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
) -> dict[str, str | float | MatrizNumerica]:
    """Executa o fluxo completo e retorna tudo o que UI e terminal precisam."""
    matriz_score_global = construir_matriz_global(
        sequencia_vertical,
        sequencia_horizontal,
        penalidade_gap,
        penalidade_mismatch,
        pontuacao_match,
    )
    matriz_score_local = construir_matriz_local(
        sequencia_vertical,
        sequencia_horizontal,
        penalidade_gap,
        penalidade_mismatch,
        pontuacao_match,
    )

    resultado_alinhamento = _rastrear_caminho(
        matriz_score_local,
        sequencia_vertical,
        sequencia_horizontal,
        penalidade_gap,
        penalidade_mismatch,
        pontuacao_match,
        matriz_score_global,
    )
    resultado_alinhamento.update(
        {
            'matriz_score_global': matriz_score_global,
            'matriz_score_local': matriz_score_local,
        },
    )
    return resultado_alinhamento
