from dataclasses import dataclass
import numpy as np

TOLERANCIA = 1e-9 #devido a comparacao entre valores float 
PREFERENCIA_DIRECOES = ('diagonal', 'cima', 'esquerda')


@dataclass(frozen=True) #imutável
class ParametrosPontuacao:
    penalidade_gap: float
    penalidade_mismatch: float
    pontuacao_match: float


def criar_matriz(linhas: int, colunas: int, inicial_global: bool, penalidade_gap: float):
    m = np.zeros((linhas, colunas), dtype=float)
    if inicial_global:
        # inicializa primeira linha e primeira coluna com gaps cumulativos
        for i in range(1, linhas):
            m[i, 0] = m[i - 1, 0] + penalidade_gap
        for j in range(1, colunas):
            m[0, j] = m[0, j - 1] + penalidade_gap
    return m


def preencher_matriz(matriz, sequencia_vertical, sequencia_horizontal, parametros, local=False):
    n_rows, n_cols = matriz.shape
    for i in range(1, n_rows):
        for j in range(1, n_cols):
            cima = matriz[i - 1, j] + parametros.penalidade_gap
            esquerda = matriz[i, j - 1] + parametros.penalidade_gap
            if sequencia_vertical[i - 1] == sequencia_horizontal[j - 1]:
                diagonal = matriz[i - 1, j - 1] + parametros.pontuacao_match
            else:
                diagonal = matriz[i - 1, j - 1] + parametros.penalidade_mismatch

            if local:
                melhor = max(0.0, diagonal, cima, esquerda)
            else:
                melhor = max(diagonal, cima, esquerda)
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

    # cima
    if i > 0:
        vi, vj = i - 1, j
        val = float(matriz[vi, vj])
        expected = val + parametros.penalidade_gap
        if np.isclose(expected, curr, atol=TOLERANCIA): #mt importante para evitar erro de tolerancia
            candidatos.append(('cima', val, expected))

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
        elif direcao == 'cima':
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


def smith_waterman(matriz_score, penalidade_gap, penalidade_mismatch, pontuacao_match, sequencia_vertical, sequencia_horizontal):
    # compatibilidade API antiga: ignora `matriz_score` e retorna a matriz local
    _ = matriz_score
    return construir_matriz_local(sequencia_vertical, sequencia_horizontal, penalidade_gap, penalidade_mismatch, pontuacao_match)


def executar_suite_alinhamento(sequencia_vertical, sequencia_horizontal, penalidade_gap, penalidade_mismatch, pontuacao_match):
    parametros = ParametrosPontuacao(penalidade_gap=penalidade_gap, penalidade_mismatch=penalidade_mismatch, pontuacao_match=pontuacao_match)
    m_global = construir_matriz_global(sequencia_vertical, sequencia_horizontal, parametros.penalidade_gap, parametros.penalidade_mismatch, parametros.pontuacao_match)
    m_local = m_global

    vertical_global, horizontal_global = traceback_global(m_global, sequencia_vertical, sequencia_horizontal, parametros)
    vertical_local, horizontal_local, score_local = traceback_local(m_local, sequencia_vertical, sequencia_horizontal, parametros)

    # score global = canto inferior direito
    score_global = float(m_global[-1, -1])

    return {
        'vertical_global': vertical_global,
        'horizontal_global': horizontal_global,
        'score_global': score_global,
        'vertical_local': vertical_local,
        'horizontal_local': horizontal_local,
        'score_local': score_local,
        'matriz_score_global': m_global,
        'matriz_score_local': m_local,
    }
