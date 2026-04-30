from dataclasses import dataclass
import numpy as np

TOLERANCIA = 1e-9  # devido a comparacao entre valores float


@dataclass(frozen=True)
class ParametrosPontuacao:
    penalidade_gap: float
    penalidade_mismatch: float
    pontuacao_match: float


def criar_matriz(linhas: int, colunas: int, inicial_global: bool, penalidade_gap: float):
    m = np.zeros((linhas, colunas), dtype=float)
    if inicial_global:
        for i in range(1, linhas):
            m[i, 0] = m[i - 1, 0] + penalidade_gap
        for j in range(1, colunas):
            m[0, j] = m[0, j - 1] + penalidade_gap
    return m


def preencher_matriz(matriz, sequencia_vertical, sequencia_horizontal, parametros):
    """Preenche matriz (global/local) padrão, acumulando gaps nas bordas quando já inicializada."""
    n_rows, n_cols = matriz.shape
    for i in range(1, n_rows):
        for j in range(1, n_cols):
            baixo = matriz[i - 1, j] + parametros.penalidade_gap
            esquerda = matriz[i, j - 1] + parametros.penalidade_gap

            if sequencia_vertical[i - 1] == sequencia_horizontal[j - 1]:
                diagonal = matriz[i - 1, j - 1] + parametros.pontuacao_match
            else:
                diagonal = matriz[i - 1, j - 1] + parametros.penalidade_mismatch

            matriz[i, j] = float(max(diagonal, baixo, esquerda))
    return matriz


def preencher_matriz_bestscore(matriz_base, sequencia_vertical, sequencia_horizontal, parametros):
    """Preenche a matriz de cálculo do best-score com sentinelas zeradas."""
    matriz = matriz_base.copy()
    n_rows, n_cols = matriz.shape

    for i in range(n_rows - 2, 0, -1):
        for j in range(n_cols - 2, 0, -1):
            direita = matriz[i, j + 1] + parametros.penalidade_gap
            baixo = matriz[i + 1, j] + parametros.penalidade_gap

            if sequencia_vertical[i - 1] == sequencia_horizontal[j - 1]:
                diagonal = matriz[i + 1, j + 1] + parametros.pontuacao_match
            else:
                diagonal = matriz[i + 1, j + 1] + parametros.penalidade_mismatch

            matriz[i, j] = float(max(0.0, direita, baixo, diagonal))

    return matriz


def _traceback_normal(matriz, sequencia_vertical, sequencia_horizontal, parametros, i, j):
    alinhada_v = []
    alinhada_h = []
    score_inicio = float(matriz[i, j])

    while i > 0 or j > 0:
        valor_atual = float(matriz[i, j])

        melhor_direcao = None
        maior_vizinho = None

        # diagonal: (i - 1, j - 1)
        if i > 0 and j > 0:
            vizinho = float(matriz[i - 1, j - 1])

            if sequencia_vertical[i - 1] == sequencia_horizontal[j - 1]:
                esperado = vizinho + parametros.pontuacao_match
            else:
                esperado = vizinho + parametros.penalidade_mismatch

            if np.isclose(esperado, valor_atual, atol=TOLERANCIA):
                melhor_direcao = 'diagonal'
                maior_vizinho = vizinho

        # cima: (i - 1, j)
        if i > 0:
            vizinho = float(matriz[i - 1, j])
            esperado = vizinho + parametros.penalidade_gap

            if np.isclose(esperado, valor_atual, atol=TOLERANCIA):
                if maior_vizinho is None or vizinho > maior_vizinho:
                    melhor_direcao = 'cima'
                    maior_vizinho = vizinho

        # esquerda: (i, j - 1)
        if j > 0:
            vizinho = float(matriz[i, j - 1])
            esperado = vizinho + parametros.penalidade_gap

            if np.isclose(esperado, valor_atual, atol=TOLERANCIA):
                if maior_vizinho is None or vizinho > maior_vizinho:
                    melhor_direcao = 'esquerda'
                    maior_vizinho = vizinho

        if melhor_direcao is None:
            break

        if melhor_direcao == 'diagonal':
            alinhada_v.append(sequencia_vertical[i - 1])
            alinhada_h.append(sequencia_horizontal[j - 1])
            i -= 1
            j -= 1

        elif melhor_direcao == 'cima':
            alinhada_v.append(sequencia_vertical[i - 1])
            alinhada_h.append('-')
            i -= 1

        else:  # esquerda
            alinhada_v.append('-')
            alinhada_h.append(sequencia_horizontal[j - 1])
            j -= 1

    return _finalizar_alinhamento(alinhada_v, alinhada_h, score_inicio, inverter=True)

def _traceback_bestscore_calculo(matriz, sequencia_vertical, sequencia_horizontal, parametros):
    n_rows, n_cols = matriz.shape

    best_idx = np.unravel_index(np.argmax(matriz), matriz.shape)
    i, j = int(best_idx[0]), int(best_idx[1])

    alinhada_v = []
    alinhada_h = []
    score_inicio = float(matriz[i, j])

    while 0 <= i < n_rows and 0 <= j < n_cols:
        valor_atual = float(matriz[i, j])

        if valor_atual <= TOLERANCIA:
            break

        melhor_direcao = None
        maior_vizinho = None

        # diagonal: (i + 1, j + 1)
        if i + 1 < n_rows and j + 1 < n_cols:
            vizinho = float(matriz[i + 1, j + 1])

            if sequencia_vertical[i - 1] == sequencia_horizontal[j - 1]:
                esperado = vizinho + parametros.pontuacao_match
            else:
                esperado = vizinho + parametros.penalidade_mismatch

            esperado = max(0.0, esperado)

            if np.isclose(esperado, valor_atual, atol=TOLERANCIA):
                melhor_direcao = 'diagonal'
                maior_vizinho = vizinho

        # baixo: (i + 1, j)
        if i + 1 < n_rows:
            vizinho = float(matriz[i + 1, j])
            esperado = max(0.0, vizinho + parametros.penalidade_gap)

            if np.isclose(esperado, valor_atual, atol=TOLERANCIA):
                if maior_vizinho is None or vizinho > maior_vizinho:
                    melhor_direcao = 'baixo'
                    maior_vizinho = vizinho

        # direita: (i, j + 1)
        if j + 1 < n_cols:
            vizinho = float(matriz[i, j + 1])
            esperado = max(0.0, vizinho + parametros.penalidade_gap)

            if np.isclose(esperado, valor_atual, atol=TOLERANCIA):
                if maior_vizinho is None or vizinho > maior_vizinho:
                    melhor_direcao = 'direita'
                    maior_vizinho = vizinho

        if melhor_direcao is None:
            break

        if melhor_direcao == 'diagonal':
            alinhada_v.append(sequencia_vertical[i - 1])
            alinhada_h.append(sequencia_horizontal[j - 1])
            i += 1
            j += 1

        elif melhor_direcao == 'baixo':
            alinhada_v.append(sequencia_vertical[i - 1])
            alinhada_h.append('-')
            i += 1

        else:  # direita
            alinhada_v.append('-')
            alinhada_h.append(sequencia_horizontal[j - 1])
            j += 1

    return _finalizar_alinhamento(alinhada_v, alinhada_h, score_inicio)
def _finalizar_alinhamento(alinhada_v, alinhada_h, score, inverter: bool = False):
    if inverter:
        alinhada_v = reversed(alinhada_v)
        alinhada_h = reversed(alinhada_h)

    return ''.join(alinhada_v), ''.join(alinhada_h), float(score)


def traceback_global(matriz, sequencia_vertical, sequencia_horizontal, parametros):
    ultima_linha = matriz.shape[0] - 1
    ultima_coluna = matriz.shape[1] - 1
    return _traceback_normal(matriz, sequencia_vertical, sequencia_horizontal, parametros, ultima_linha, ultima_coluna)


def traceback_local(matriz, sequencia_vertical, sequencia_horizontal, parametros):
    ultima_coluna = matriz.shape[1] - 1
    coluna = np.array(matriz[:, ultima_coluna], dtype=float)
    linha_maior = int(np.argmax(coluna))
    return _traceback_normal(matriz, sequencia_vertical, sequencia_horizontal, parametros, linha_maior, ultima_coluna)


def traceback_bestscore(matriz, sequencia_vertical, sequencia_horizontal, parametros):
    return _traceback_bestscore_calculo(matriz, sequencia_vertical, sequencia_horizontal, parametros)


def preparar_matriz_bestscore_para_exibicao(matriz_bestscore_calculo, penalidade_gap):
    """Gera a matriz best-score visual com gaps nas bordas."""
    n_rows_calc, n_cols_calc = matriz_bestscore_calculo.shape
    lv = n_rows_calc - 2
    lh = n_cols_calc - 2

    visual = criar_matriz(lv + 1, lh + 1, inicial_global=True, penalidade_gap=penalidade_gap)

    for i in range(1, lv + 1):
        for j in range(1, lh + 1):
            visual[i, j] = float(matriz_bestscore_calculo[i, j])

    return visual


def construir_matriz_bestscore(sequencia_vertical, sequencia_horizontal, penalidade_gap, penalidade_mismatch, pontuacao_match):
    parametros = ParametrosPontuacao(
        penalidade_gap=penalidade_gap,
        penalidade_mismatch=penalidade_mismatch,
        pontuacao_match=pontuacao_match,
    )

    linhas = len(sequencia_vertical) + 2
    colunas = len(sequencia_horizontal) + 2

    matriz_base = np.zeros((linhas, colunas), dtype=float)

    return preencher_matriz_bestscore(matriz_base, sequencia_vertical, sequencia_horizontal, parametros)


def construir_matriz_global(sequencia_vertical, sequencia_horizontal, penalidade_gap, penalidade_mismatch, pontuacao_match):
    parametros = ParametrosPontuacao(penalidade_gap=penalidade_gap, penalidade_mismatch=penalidade_mismatch, pontuacao_match=pontuacao_match)
    linhas = len(sequencia_vertical) + 1
    colunas = len(sequencia_horizontal) + 1
    m = criar_matriz(linhas, colunas, inicial_global=True, penalidade_gap=parametros.penalidade_gap)
    return preencher_matriz(m, sequencia_vertical, sequencia_horizontal, parametros)



def executar_suite_alinhamento(sequencia_vertical, sequencia_horizontal, penalidade_gap, penalidade_mismatch, pontuacao_match):
    parametros = ParametrosPontuacao(
        penalidade_gap=penalidade_gap,
        penalidade_mismatch=penalidade_mismatch,
        pontuacao_match=pontuacao_match,
    )

    m_global = construir_matriz_global(
        sequencia_vertical,
        sequencia_horizontal,
        parametros.penalidade_gap,
        parametros.penalidade_mismatch,
        parametros.pontuacao_match,
    )

    # local reuse global as required
    m_local = m_global

    matriz_best_calculo = construir_matriz_bestscore(
        sequencia_vertical,
        sequencia_horizontal,
        parametros.penalidade_gap,
        parametros.penalidade_mismatch,
        parametros.pontuacao_match,
    )

    vertical_global, horizontal_global, score_global = traceback_global(
        m_global, sequencia_vertical, sequencia_horizontal, parametros
    )

    vertical_local, horizontal_local, score_local = traceback_local(
        m_local, sequencia_vertical, sequencia_horizontal, parametros
    )

    vertical_best, horizontal_best, score_best = traceback_bestscore(
        matriz_best_calculo, sequencia_vertical, sequencia_horizontal, parametros
    )

    matriz_best_visual = preparar_matriz_bestscore_para_exibicao(matriz_best_calculo, parametros.penalidade_gap)

    return {
        'vertical_global': vertical_global,
        'horizontal_global': horizontal_global,
        'score_global': score_global,
        'vertical_local': vertical_local,
        'horizontal_local': horizontal_local,
        'score_local': score_local,
        'vertical_bestscore': vertical_best,
        'horizontal_bestscore': horizontal_best,
        'score_bestscore': score_best,
        'matriz_score_global': m_global,
        'matriz_score_local': m_local,
        'matriz_bestscore': matriz_best_visual,
    }
