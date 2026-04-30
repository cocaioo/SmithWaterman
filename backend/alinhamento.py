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
    """Preenche a matriz de CÁLCULO do best-score (com sentinelas zeradas).

    A matriz de cálculo tem dimensões lv+2 x lh+2; os índices 1..lv / 1..lh
    correspondem aos caracteres. O preenchimento é feito bottom->up e
    right->left e aplica piso em zero.
    """
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


def _traceback_central(matriz, sequencia_vertical, sequencia_horizontal, parametros, tipo: str):
    """Traceback centralizado para 'global', 'local' e 'best_score'.

    - global: começa em (n_rows-1, n_cols-1); movimentos: diagonal(i-1,j-1), cima(i-1,j), esquerda(i,j-1); inverter ao final.
    - local: começa na célula de MAIOR VALOR da ÚLTIMA COLUNA; mesmos movimentos de global; inverter ao final.
    - best_score: começa no argmax da matriz de cálculo; movimentos: diagonal(i+1,j+1), baixo(i+1,j), direita(i,j+1); NÃO inverter.

    Em cada passo recalcula os 3 caminhos possíveis, filtra os válidos (np.isclose) e escolhe o cujo vizinho tem MAIOR valor.
    """
    n_rows, n_cols = matriz.shape

    if tipo == 'global':
        i = n_rows - 1
        j = n_cols - 1
        reverse_at_end = True
    elif tipo == 'local':
        j = n_cols - 1
        col_vals = np.array(matriz[:, j], dtype=float)
        i = int(np.argmax(col_vals))
        reverse_at_end = True
    elif tipo == 'best_score':
        best_idx = np.unravel_index(np.argmax(matriz), matriz.shape)
        i, j = int(best_idx[0]), int(best_idx[1])
        reverse_at_end = False
    else:
        raise ValueError(f"tipo inválido para traceback: {tipo}")

    alinhada_v = []
    alinhada_h = []
    score_inicio = float(matriz[i, j])

    if tipo in ('global', 'local'):
        while i > 0 or j > 0:
            curr = float(matriz[i, j])
            candidatos = []

            # diagonal (i-1, j-1)
            if i > 0 and j > 0:
                vi, vj = i - 1, j - 1
                val = float(matriz[vi, vj])
                esperado = val + (parametros.pontuacao_match if sequencia_vertical[i - 1] == sequencia_horizontal[j - 1] else parametros.penalidade_mismatch)
                if np.isclose(esperado, curr, atol=TOLERANCIA):
                    candidatos.append((val, vi, vj, 'diagonal'))

            # cima (i-1, j)
            if i > 0:
                vi, vj = i - 1, j
                val = float(matriz[vi, vj])
                esperado = val + parametros.penalidade_gap
                if np.isclose(esperado, curr, atol=TOLERANCIA):
                    candidatos.append((val, vi, vj, 'cima'))

            # esquerda (i, j-1)
            if j > 0:
                vi, vj = i, j - 1
                val = float(matriz[vi, vj])
                esperado = val + parametros.penalidade_gap
                if np.isclose(esperado, curr, atol=TOLERANCIA):
                    candidatos.append((val, vi, vj, 'esquerda'))

            if not candidatos:
                break

            # escolher apenas pelo maior valor do vizinho
            val_chosen, vi_chosen, vj_chosen, direcao = max(candidatos, key=lambda x: x[0])

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

    else:
        # best_score: movimentos para frente
        while 0 <= i < n_rows and 0 <= j < n_cols:
            curr = float(matriz[i, j])
            if curr <= TOLERANCIA:
                break

            candidatos = []

            # diagonal (i+1, j+1)
            if i + 1 < n_rows and j + 1 < n_cols:
                vi, vj = i + 1, j + 1
                val = float(matriz[vi, vj])
                calc = val + (parametros.pontuacao_match if sequencia_vertical[i - 1] == sequencia_horizontal[j - 1] else parametros.penalidade_mismatch)
                esperado = calc if calc >= 0 else 0.0
                if np.isclose(esperado, curr, atol=TOLERANCIA):
                    candidatos.append((val, vi, vj, 'diagonal'))

            # baixo (i+1, j)
            if i + 1 < n_rows:
                vi, vj = i + 1, j
                val = float(matriz[vi, vj])
                calc = val + parametros.penalidade_gap
                esperado = calc if calc >= 0 else 0.0
                if np.isclose(esperado, curr, atol=TOLERANCIA):
                    candidatos.append((val, vi, vj, 'baixo'))

            # direita (i, j+1)
            if j + 1 < n_cols:
                vi, vj = i, j + 1
                val = float(matriz[vi, vj])
                calc = val + parametros.penalidade_gap
                esperado = calc if calc >= 0 else 0.0
                if np.isclose(esperado, curr, atol=TOLERANCIA):
                    candidatos.append((val, vi, vj, 'direita'))

            if not candidatos:
                break

            val_chosen, vi_chosen, vj_chosen, direcao = max(candidatos, key=lambda x: x[0])

            if direcao == 'diagonal':
                alinhada_v.append(sequencia_vertical[i - 1])
                alinhada_h.append(sequencia_horizontal[j - 1])
                i += 1
                j += 1
            elif direcao == 'baixo':
                alinhada_v.append(sequencia_vertical[i - 1])
                alinhada_h.append('-')
                i += 1
            else:  # direita
                alinhada_v.append('-')
                alinhada_h.append(sequencia_horizontal[j - 1])
                j += 1

    if reverse_at_end:
        return ''.join(reversed(alinhada_v)), ''.join(reversed(alinhada_h)), float(score_inicio)
    return ''.join(alinhada_v), ''.join(alinhada_h), float(score_inicio)


def traceback_global(matriz, sequencia_vertical, sequencia_horizontal, parametros):
    v, h, _ = _traceback_central(matriz, sequencia_vertical, sequencia_horizontal, parametros, 'global')
    return v, h


def traceback_local(matriz, sequencia_vertical, sequencia_horizontal, parametros):
    v, h, score = _traceback_central(matriz, sequencia_vertical, sequencia_horizontal, parametros, 'local')
    return v, h, float(score)


def traceback_bestscore(matriz, sequencia_vertical, sequencia_horizontal, parametros):
    v, h, score = _traceback_central(matriz, sequencia_vertical, sequencia_horizontal, parametros, 'best_score')
    return v, h, float(score)


def preparar_matriz_bestscore_para_exibicao(matriz_bestscore_calculo, penalidade_gap):
    """Prepara matriz visual do best-score copiando o miolo da matriz de cálculo.

    - matriz_bestscore_calculo: dimensões lv+2 x lh+2
    - retorna visual: dimensões lv+1 x lh+1, com gaps cumulativos nas bordas
    """
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


def smith_waterman(matriz_score, penalidade_gap, penalidade_mismatch, pontuacao_match, sequencia_vertical, sequencia_horizontal):
    """Compatibilidade: retorna a matriz local (inicializada sem gaps cumulativos nas bordas).

    O parâmetro `matriz_score` é ignorado; função mantida para compatibilidade com API antiga.
    """
    _ = matriz_score
    parametros = ParametrosPontuacao(penalidade_gap=penalidade_gap, penalidade_mismatch=penalidade_mismatch, pontuacao_match=pontuacao_match)
    linhas = len(sequencia_vertical) + 1
    colunas = len(sequencia_horizontal) + 1
    m = criar_matriz(linhas, colunas, inicial_global=False, penalidade_gap=parametros.penalidade_gap)
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

    vertical_global, horizontal_global = traceback_global(
        m_global, sequencia_vertical, sequencia_horizontal, parametros
    )

    vertical_local, horizontal_local, score_local = traceback_local(
        m_local, sequencia_vertical, sequencia_horizontal, parametros
    )

    vertical_best, horizontal_best, score_best = traceback_bestscore(
        matriz_best_calculo, sequencia_vertical, sequencia_horizontal, parametros
    )

    matriz_best_visual = preparar_matriz_bestscore_para_exibicao(matriz_best_calculo, parametros.penalidade_gap)

    score_global = float(m_global[-1, -1])

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
