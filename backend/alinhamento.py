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
        m[:, 0] = np.arange(linhas) * penalidade_gap
        m[0, :] = np.arange(colunas) * penalidade_gap
    return m


def preencher_matriz(matriz, sequencia_vertical, sequencia_horizontal, parametros):
    """Preenche matriz (global/local) padrão, acumulando gaps nas bordas quando já inicializada."""
    n_rows, n_cols = matriz.shape
    for i in range(1, n_rows):
        for j in range(1, n_cols):
            # calcule valores vindos de cima, esquerda e diagonal
            vindo_de_cima = matriz[i - 1, j] + parametros.penalidade_gap
            vindo_de_esquerda = matriz[i, j - 1] + parametros.penalidade_gap

            if sequencia_vertical[i - 1] == sequencia_horizontal[j - 1]:
                vindo_de_diagonal = matriz[i - 1, j - 1] + parametros.pontuacao_match
            else:
                vindo_de_diagonal = matriz[i - 1, j - 1] + parametros.penalidade_mismatch

            matriz[i, j] = float(max(vindo_de_diagonal, vindo_de_cima, vindo_de_esquerda))

    return matriz


def preencher_matriz_bestscore(matriz_base, sequencia_vertical, sequencia_horizontal, parametros):
    matriz = matriz_base.copy()
    n_rows, n_cols = matriz.shape

    for i in range(1, n_rows):
        for j in range(1, n_cols):
            vindo_de_cima = matriz[i - 1, j] + parametros.penalidade_gap
            vindo_de_esquerda = matriz[i, j - 1] + parametros.penalidade_gap

            if sequencia_vertical[i - 1] == sequencia_horizontal[j - 1]:
                vindo_de_diagonal = matriz[i - 1, j - 1] + parametros.pontuacao_match
            else:
                vindo_de_diagonal = matriz[i - 1, j - 1] + parametros.penalidade_mismatch

            matriz[i, j] = float(max(
                0.0,
                vindo_de_diagonal,
                vindo_de_cima,
                vindo_de_esquerda
            ))

    return matriz


def traceback_from_position(matriz, sequencia_vertical, sequencia_horizontal, parametros, i, j):
    """Reconstrói alinhamento (global/local) a partir da posição (i, j).

    Retorna (alinhada_vertical, alinhada_horizontal, score_inicial).
    """
    alinhada_v = []
    alinhada_h = []
    score_inicio = float(matriz[i, j])
    #Refaz o calculo para checar de onde veio

    while i > 0 or j > 0:
        valor_atual = float(matriz[i, j]) #score da celula atual

        direcao = None #guarda onde o algoritmo decidiu voltar
        maior_vizinho = None

        # diagonal: (i - 1, j - 1)
        if i > 0 and j > 0: #Só pode ir para diagonal se não estiver na primeira linha nem na primeira coluna.
            vizinho = float(matriz[i - 1, j - 1])

            if sequencia_vertical[i - 1] == sequencia_horizontal[j - 1]:
                esperado = vizinho + parametros.pontuacao_match
            else:
                esperado = vizinho + parametros.penalidade_mismatch

            if np.isclose(esperado, valor_atual, atol=TOLERANCIA):
                direcao = 'diagonal' #se o valor atual vem da diagonal
                maior_vizinho = vizinho

        # cima: (i - 1, j)
        if i > 0:
            vizinho = float(matriz[i - 1, j])
            esperado = vizinho + parametros.penalidade_gap
            if np.isclose(esperado, valor_atual, atol=TOLERANCIA):
                if maior_vizinho is None or vizinho > maior_vizinho:
                    direcao = 'cima'
                    maior_vizinho = vizinho

        # esquerda: (i, j - 1)
        if j > 0:
            vizinho = float(matriz[i, j - 1])
            esperado = vizinho + parametros.penalidade_gap
            if np.isclose(esperado, valor_atual, atol=TOLERANCIA):
                if maior_vizinho is None or vizinho > maior_vizinho:
                    direcao = 'esquerda'
                    maior_vizinho = vizinho

        if direcao is None:
            break

        if direcao == 'diagonal':
            alinhada_v.append(sequencia_vertical[i - 1])
            alinhada_h.append(sequencia_horizontal[j - 1])
            i -= 1
            j -= 1

        elif direcao == 'cima':
            alinhada_v.append(sequencia_vertical[i - 1])
            alinhada_h.append('-')
            i -= 1

        else:  # esquerda
            alinhada_v.append('-')
            alinhada_h.append(sequencia_horizontal[j - 1])
            j -= 1

    return finalizar_alinhamento(alinhada_v, alinhada_h, score_inicio, inverter=True)

def finalizar_alinhamento(alinhada_v, alinhada_h, score, inverter: bool = False):
    if inverter:
        v = ''.join(reversed(alinhada_v))
        h = ''.join(reversed(alinhada_h))
    else:
        v = ''.join(alinhada_v)
        h = ''.join(alinhada_h)

    return v, h, float(score)

def traceback_global(matriz, sequencia_vertical, sequencia_horizontal, parametros):
    ultima_linha = matriz.shape[0] - 1
    ultima_coluna = matriz.shape[1] - 1
    return traceback_from_position(matriz, sequencia_vertical, sequencia_horizontal, parametros, ultima_linha, ultima_coluna)

def traceback_local(matriz, sequencia_vertical, sequencia_horizontal, parametros):
    ultima_coluna = matriz.shape[1] - 1
    coluna = np.array(matriz[:, ultima_coluna], dtype=float)
    linha_maior = int(np.argmax(coluna))
    return traceback_from_position(matriz, sequencia_vertical, sequencia_horizontal, parametros, linha_maior, ultima_coluna)

def traceback_bestscore(matriz, sequencia_vertical, sequencia_horizontal, parametros):
    """Reconstrói o alinhamento local a partir do maior score da matriz.

    Usa traceback clássico: começa no maior score e anda para trás até score zero.
    """
    best_idx = np.unravel_index(np.argmax(matriz), matriz.shape)
    i, j = int(best_idx[0]), int(best_idx[1])

    alinhada_v = []
    alinhada_h = []
    score_inicio = float(matriz[i, j])

    while i > 0 and j > 0:
        valor_atual = float(matriz[i, j])

        if valor_atual <= TOLERANCIA:
            break

        direcao = None
        maior_vizinho = None

        # diagonal: (i - 1, j - 1)
        vizinho = float(matriz[i - 1, j - 1])

        if sequencia_vertical[i - 1] == sequencia_horizontal[j - 1]:
            esperado = vizinho + parametros.pontuacao_match
        else:
            esperado = vizinho + parametros.penalidade_mismatch

        if np.isclose(esperado, valor_atual, atol=TOLERANCIA):
            direcao = "diagonal"
            maior_vizinho = vizinho

        # cima: (i - 1, j)
        vizinho = float(matriz[i - 1, j])
        esperado = vizinho + parametros.penalidade_gap

        if np.isclose(esperado, valor_atual, atol=TOLERANCIA):
            if maior_vizinho is None or vizinho > maior_vizinho:
                direcao = "cima"
                maior_vizinho = vizinho

        # esquerda: (i, j - 1)
        vizinho = float(matriz[i, j - 1])
        esperado = vizinho + parametros.penalidade_gap

        if np.isclose(esperado, valor_atual, atol=TOLERANCIA):
            if maior_vizinho is None or vizinho > maior_vizinho:
                direcao = "esquerda"
                maior_vizinho = vizinho

        if direcao is None:
            break

        if direcao == "diagonal":
            alinhada_v.append(sequencia_vertical[i - 1])
            alinhada_h.append(sequencia_horizontal[j - 1])
            i -= 1
            j -= 1

        elif direcao == "cima":
            alinhada_v.append(sequencia_vertical[i - 1])
            alinhada_h.append("-")
            i -= 1

        else:  # esquerda
            alinhada_v.append("-")
            alinhada_h.append(sequencia_horizontal[j - 1])
            j -= 1

    return finalizar_alinhamento(alinhada_v, alinhada_h, score_inicio, inverter=True)

def preparar_matriz_bestscore_para_exibicao(matriz_bestscore_calculo, penalidade_gap):
    return matriz_bestscore_calculo

def construir_matriz_bestscore(sequencia_vertical, sequencia_horizontal, penalidade_gap, penalidade_mismatch, pontuacao_match):
    parametros = ParametrosPontuacao(
        penalidade_gap=penalidade_gap,
        penalidade_mismatch=penalidade_mismatch,
        pontuacao_match=pontuacao_match,
    )

    linhas = len(sequencia_vertical) + 1
    colunas = len(sequencia_horizontal) + 1
    matriz_base = np.zeros((linhas, colunas), dtype=float)

    return preencher_matriz_bestscore(
        matriz_base,
        sequencia_vertical,
        sequencia_horizontal,
        parametros
    )

def construir_matriz_global(sequencia_vertical, sequencia_horizontal, penalidade_gap, penalidade_mismatch, pontuacao_match):
    parametros = ParametrosPontuacao(
        penalidade_gap=penalidade_gap,
        penalidade_mismatch=penalidade_mismatch,
        pontuacao_match=pontuacao_match,
    )
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

    m_local = m_global #A matriz é igual, só muda o traceback

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
