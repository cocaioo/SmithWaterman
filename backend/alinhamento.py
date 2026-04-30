from dataclasses import dataclass
import numpy as np

TOLERANCIA = 1e-9 #devido a comparacao entre valores float 
PREFERENCIA_DIRECOES = ('diagonal', 'baixo', 'esquerda')


@dataclass(frozen=True) #imutável
class ParametrosPontuacao:
    penalidade_gap: float
    penalidade_mismatch: float
    pontuacao_match: float

#inicializar matriz ja com gaps
def criar_matriz(linhas: int, colunas: int, inicial_global: bool, penalidade_gap: float):
    m = np.zeros((linhas, colunas), dtype=float)
    if inicial_global:
        # inicializa primeira linha e primeira coluna com gaps cumulativos
        for i in range(1, linhas):
            m[i, 0] = m[i - 1, 0] + penalidade_gap
        for j in range(1, colunas):
            m[0, j] = m[0, j - 1] + penalidade_gap
    return m

def preencher_matriz_bestscore(matriz_base, sequencia_vertical, sequencia_horizontal, parametros):
    """Preenche a matriz best-score a partir de uma matriz base com gaps."""
    matriz_best_score = matriz_base.copy()

    n_rows, n_cols = matriz_best_score.shape

    for i in range(n_rows - 2, 0, -1):
        for j in range(1, n_cols):
            # esquerda: (i, j-1)
            val_esquerda = float(matriz_best_score[i, j - 1]) + parametros.penalidade_gap

            # baixo: (i+1, j)
            val_baixo = float(matriz_best_score[i + 1, j]) + parametros.penalidade_gap

            # diagonal baixo-esquerda: (i+1, j-1)
            match = sequencia_vertical[i - 1] == sequencia_horizontal[j - 1]
            val_diagonal = float(matriz_best_score[i + 1, j - 1]) + (
                parametros.pontuacao_match if match else parametros.penalidade_mismatch
            )

            # aplicar piso em zero
            candidato_esq = 0.0 if val_esquerda < 0 else val_esquerda
            candidato_baixo = 0.0 if val_baixo < 0 else val_baixo
            candidato_diag = 0.0 if val_diagonal < 0 else val_diagonal

            maior = max(candidato_esq, candidato_baixo, candidato_diag)

            matriz_best_score[i, j] = float(maior)

    return matriz_best_score


def _coletar_vizinhos_validos_bestscore(matriz, i, j, sequencia_vertical, sequencia_horizontal, parametros):
    """Retorna lista de candidatos válidos [(direcao, valor_vizinho, expected), ...]
    para traceback da matriz best-score.
    Direções: 'diagonal'=(i+1,j-1), 'baixo'=(i+1,j), 'esquerda'=(i,j-1)
    """
    curr = float(matriz[i, j])
    candidatos = []
    n_rows, n_cols = matriz.shape

    # esquerda
    if j > 0:
        vi, vj = i, j - 1
        val = float(matriz[vi, vj])
        expected = val + parametros.penalidade_gap
        if np.isclose(expected, curr, atol=TOLERANCIA):
            candidatos.append(('esquerda', val, expected))

    # baixo
    if i + 1 < n_rows:
        vi, vj = i + 1, j
        val = float(matriz[vi, vj])
        expected = val + parametros.penalidade_gap
        if np.isclose(expected, curr, atol=TOLERANCIA):
            candidatos.append(('baixo', val, expected))

    # diagonal baixo-esquerda
    if i + 1 < n_rows and j > 0:
        vi, vj = i + 1, j - 1
        val = float(matriz[vi, vj])
        match = sequencia_vertical[i - 1] == sequencia_horizontal[j - 1]
        expected = val + (parametros.pontuacao_match if match else parametros.penalidade_mismatch)
        if np.isclose(expected, curr, atol=TOLERANCIA):
            candidatos.append(('diagonal', val, expected))

    return candidatos


def traceback_bestscore(matriz, sequencia_vertical, sequencia_horizontal, parametros):
    """Traceback para a matriz best-score.

    Inicia na célula de maior valor e segue vizinhos (esquerda, baixo, diagonal baixo-esquerda)
    até encontrar valor 0, não haver vizinho válido, ou sair da grade.
    Retorna (alinhada_v, alinhada_h, score_best)
    """
    n_rows, n_cols = matriz.shape

    # inicia na melhor célula
    best_idx = np.unravel_index(np.argmax(matriz), matriz.shape)
    i, j = int(best_idx[0]), int(best_idx[1])

    score_best = float(matriz[i, j])

    alinhada_v = []
    alinhada_h = []

    while 0 <= i < n_rows and 0 <= j < n_cols:
        curr = float(matriz[i, j])
        if curr <= TOLERANCIA:
            break

        candidatos = _coletar_vizinhos_validos_bestscore(matriz, i, j, sequencia_vertical, sequencia_horizontal, parametros)
        if not candidatos:
            break

        direcao = _escolher_melhor_candidato(candidatos)

        if direcao == 'diagonal':
            # diagonal baixo-esquerda: consome sequencia_vertical[i] e sequencia_horizontal[j-1]
            alinhada_v.append(sequencia_vertical[i - 1])
            alinhada_h.append(sequencia_horizontal[j - 1])
            i += 1
            j -= 1
        elif direcao == 'baixo':
            # baixo: consome sequencia_vertical[i] e gap em horizontal
            alinhada_v.append(sequencia_vertical[i - 1])
            alinhada_h.append('-')
            i += 1
        else:
            # esquerda: gap em vertical e consome sequencia_horizontal[j-1]
            alinhada_v.append('-')
            alinhada_h.append(sequencia_horizontal[j - 1])
            j -= 1

    # inverter para exibir left->right
    return ''.join(reversed(alinhada_v)), ''.join(reversed(alinhada_h)), float(score_best)

def preencher_matriz(matriz, sequencia_vertical, sequencia_horizontal, parametros, local=False):
    n_rows, n_cols = matriz.shape

    for i in range(1, n_rows):
        for j in range(1, n_cols):
            baixo = matriz[i - 1, j] + parametros.penalidade_gap
            esquerda = matriz[i, j - 1] + parametros.penalidade_gap

            if sequencia_vertical[i - 1] == sequencia_horizontal[j - 1]:
                diagonal = matriz[i - 1, j - 1] + parametros.pontuacao_match
            else:
                diagonal = matriz[i - 1, j - 1] + parametros.penalidade_mismatch

            melhor = max(diagonal, baixo, esquerda)
            matriz[i, j] = float(melhor)

    return matriz

#saber quais vizinhos podem ter gerado aquele valor 
def _coletar_vizinhos_validos(matriz, i, j, sequencia_vertical, sequencia_horizontal, parametros):
    """Retorna lista de candidatos válidos [(direcao, valor_vizinho, expected), ...]."""
    curr = float(matriz[i, j])
    candidatos = []

    # diagonal
    if i > 0 and j > 0:
        vi, vj = i - 1, j - 1
        val = float(matriz[vi, vj])
        expected = val + (parametros.pontuacao_match if sequencia_vertical[i - 1] == sequencia_horizontal[j - 1] else parametros.penalidade_mismatch)
        if np.isclose(expected, curr, atol=TOLERANCIA): #mt importante para evitar erro de tolerancia
            candidatos.append(('diagonal', val, expected))

    # baixo
    if i > 0:
        vi, vj = i - 1, j
        val = float(matriz[vi, vj])
        expected = val + parametros.penalidade_gap
        if np.isclose(expected, curr, atol=TOLERANCIA): #mt importante para evitar erro de tolerancia
            candidatos.append(('baixo', val, expected))

    # esquerda
    if j > 0:
        vi, vj = i, j - 1
        val = float(matriz[vi, vj])
        expected = val + parametros.penalidade_gap
        if np.isclose(expected, curr, atol=TOLERANCIA): #mt importante para evitar erro de tolerancia
            candidatos.append(('esquerda', val, expected))

    return candidatos


def _escolher_melhor_candidato(candidatos):
    # candidatos: list of (direcao, valor_vizinho, expected)
    # escolher maior valor_vizinho; em empate, aplicar PREFERENCIA_DIRECOES
    valores = [val for _, val, _ in candidatos]
    max_val = max(valores)
    # considerar empates numericos
    melhores = [direcao for direcao, val, _ in candidatos if np.isclose(val, max_val, atol=TOLERANCIA)]
    for pref in PREFERENCIA_DIRECOES:
        if pref in melhores:
            return pref
    return melhores[0]


def _escolher_direcao_ou_erro(matriz, i, j, sequencia_vertical, sequencia_horizontal, parametros):
    candidatos = _coletar_vizinhos_validos(
        matriz, i, j, sequencia_vertical, sequencia_horizontal, parametros
    )

    if not candidatos:
        raise RuntimeError(f'Nenhum vizinho gera o valor atual em ({i}, {j})')

    return _escolher_melhor_candidato(candidatos)


def _montar_alinhamento(matriz, sequencia_vertical, sequencia_horizontal, parametros, i, j):
    alinhada_v = []
    alinhada_h = []

    while i > 0 or j > 0:
        if i == 0:
            alinhada_v.append('-')
            alinhada_h.append(sequencia_horizontal[j - 1])
            j -= 1
            continue

        if j == 0:
            alinhada_v.append(sequencia_vertical[i - 1])
            alinhada_h.append('-')
            i -= 1
            continue

        direcao = _escolher_direcao_ou_erro(
            matriz, i, j, sequencia_vertical, sequencia_horizontal, parametros
        )

        if direcao == 'diagonal':
            alinhada_v.append(sequencia_vertical[i - 1])
            alinhada_h.append(sequencia_horizontal[j - 1])
            i -= 1
            j -= 1
        elif direcao == 'baixo':
            alinhada_v.append(sequencia_vertical[i - 1])
            alinhada_h.append('-')
            i -= 1
        else:
            alinhada_v.append('-')
            alinhada_h.append(sequencia_horizontal[j - 1])
            j -= 1

    return ''.join(reversed(alinhada_v)), ''.join(reversed(alinhada_h))


def traceback_global(matriz, sequencia_vertical, sequencia_horizontal, parametros):
    i = matriz.shape[0] - 1
    j = matriz.shape[1] - 1

    return _montar_alinhamento(
        matriz, sequencia_vertical, sequencia_horizontal, parametros, i, j
    )


def traceback_local(matriz, sequencia_vertical, sequencia_horizontal, parametros):
    ultima_linha = matriz.shape[0] - 1
    ultima_coluna = matriz.shape[1] - 1

    candidatos = []

    for j in range(matriz.shape[1]):
        candidatos.append((float(matriz[ultima_linha, j]), ultima_linha, j))

    for i in range(matriz.shape[0]):
        candidatos.append((float(matriz[i, ultima_coluna]), i, ultima_coluna))

    melhor_score, i, j = max(candidatos, key=lambda x: x[0])

    alinhada_v, alinhada_h = _montar_alinhamento(
        matriz, sequencia_vertical, sequencia_horizontal, parametros, i, j
    )

    return alinhada_v, alinhada_h, float(melhor_score)


def construir_matriz_global(sequencia_vertical, sequencia_horizontal, penalidade_gap, penalidade_mismatch, pontuacao_match):
    parametros = ParametrosPontuacao(penalidade_gap=penalidade_gap, penalidade_mismatch=penalidade_mismatch, pontuacao_match=pontuacao_match)
    linhas = len(sequencia_vertical) + 1
    colunas = len(sequencia_horizontal) + 1
    m = criar_matriz(linhas, colunas, inicial_global=True, penalidade_gap=parametros.penalidade_gap)
    return preencher_matriz(m, sequencia_vertical, sequencia_horizontal, parametros, local=False)


def construir_matriz_local(sequencia_vertical, sequencia_horizontal, penalidade_gap, penalidade_mismatch, pontuacao_match):
    parametros = ParametrosPontuacao(penalidade_gap=penalidade_gap, penalidade_mismatch=penalidade_mismatch, pontuacao_match=pontuacao_match)
    linhas = len(sequencia_vertical) + 1
    colunas = len(sequencia_horizontal) + 1
    m = criar_matriz(linhas, colunas, inicial_global=False, penalidade_gap=parametros.penalidade_gap)
    return preencher_matriz(m, sequencia_vertical, sequencia_horizontal, parametros, local=True)

def construir_matriz_bestscore(sequencia_vertical, sequencia_horizontal, penalidade_gap, penalidade_mismatch, pontuacao_match):
    parametros = ParametrosPontuacao(
        penalidade_gap=penalidade_gap,
        penalidade_mismatch=penalidade_mismatch,
        pontuacao_match=pontuacao_match
    )

    linhas = len(sequencia_vertical) + 1
    colunas = len(sequencia_horizontal) + 1

    matriz_base = criar_matriz(
        linhas,
        colunas,
        inicial_global=True,
        penalidade_gap=parametros.penalidade_gap
    )

    return preencher_matriz_bestscore(
        matriz_base,
        sequencia_vertical,
        sequencia_horizontal,
        parametros
    )

def smith_waterman(matriz_score, penalidade_gap, penalidade_mismatch, pontuacao_match, sequencia_vertical, sequencia_horizontal):
    # compatibilidade API antiga: ignora `matriz_score` e retorna a matriz local
    _ = matriz_score
    return construir_matriz_local(sequencia_vertical, sequencia_horizontal, penalidade_gap, penalidade_mismatch, pontuacao_match)


def executar_suite_alinhamento(sequencia_vertical, sequencia_horizontal, penalidade_gap, penalidade_mismatch, pontuacao_match):
    parametros = ParametrosPontuacao(
        penalidade_gap=penalidade_gap,
        penalidade_mismatch=penalidade_mismatch,
        pontuacao_match=pontuacao_match
    )

    m_global = construir_matriz_global(
        sequencia_vertical,
        sequencia_horizontal,
        parametros.penalidade_gap,
        parametros.penalidade_mismatch,
        parametros.pontuacao_match
    )

    m_local = m_global

    matriz_best = construir_matriz_bestscore(
        sequencia_vertical,
        sequencia_horizontal,
        parametros.penalidade_gap,
        parametros.penalidade_mismatch,
        parametros.pontuacao_match,
    )

    vertical_global, horizontal_global = traceback_global(
        m_global,
        sequencia_vertical,
        sequencia_horizontal,
        parametros
    )

    vertical_local, horizontal_local, score_local = traceback_local(
        m_local,
        sequencia_vertical,
        sequencia_horizontal,
        parametros
    )

    vertical_best, horizontal_best, score_best = traceback_bestscore(
        matriz_best,
        sequencia_vertical,
        sequencia_horizontal,
        parametros
    )

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
        'matriz_bestscore': matriz_best,
    }
