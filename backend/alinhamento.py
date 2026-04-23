import numpy as np

from .ponteiros import escolher_direcao_traceback, mesmo_score


def construir_alinhamento_da_posicao(
    matriz_scores,
    matriz_ponteiros,
    sequencia_vertical,
    sequencia_horizontal,
    linha_inicio,
    coluna_inicio,
    parar_em_zero,
    completar_bordas,
):
    alinhada_vertical = []
    alinhada_horizontal = []

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
            indice_vertical = (len(sequencia_vertical) - 1) - linha
            alinhada_vertical.append(sequencia_vertical[indice_vertical])
            alinhada_horizontal.append('-')
            linha += 1
            continue

        if linha == ultima_linha:
            if not completar_bordas:
                break
            indice_horizontal = coluna - 1
            alinhada_vertical.append('-')
            alinhada_horizontal.append(sequencia_horizontal[indice_horizontal])
            coluna -= 1
            continue

        valor_ponteiro = int(matriz_ponteiros[linha, coluna])
        direcao = escolher_direcao_traceback(valor_ponteiro, matriz_scores, linha, coluna)

        if direcao is None:
            if not completar_bordas:
                break

            candidatos_fallback = []

            if coluna - 1 >= 0:
                candidatos_fallback.append(('esquerda', matriz_scores[linha, coluna - 1]))

            if linha + 1 <= ultima_linha and coluna - 1 >= 0:
                candidatos_fallback.append(('diagonal', matriz_scores[linha + 1, coluna - 1]))

            if linha + 1 <= ultima_linha:
                candidatos_fallback.append(('cima', matriz_scores[linha + 1, coluna]))

            if not candidatos_fallback:
                break

            maior_valor_vizinho = max(valor for _, valor in candidatos_fallback)
            melhores_direcoes = [
                direcao_fallback
                for direcao_fallback, valor in candidatos_fallback
                if mesmo_score(valor, maior_valor_vizinho)
            ]

            direcao = melhores_direcoes[0]
            for direcao_preferencial in ('diagonal', 'cima', 'esquerda'):
                if direcao_preferencial in melhores_direcoes:
                    direcao = direcao_preferencial
                    break

        indice_vertical = (len(sequencia_vertical) - 1) - linha
        indice_horizontal = coluna - 1

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


def encontrar_melhor_posicao_local(matriz_score_local):
    melhor_posicao = np.unravel_index(np.argmax(matriz_score_local), matriz_score_local.shape)
    return int(melhor_posicao[0]), int(melhor_posicao[1])


def alinhamento_global(matriz_score_global, matriz_ponteiro_global, sequencia_vertical, sequencia_horizontal):
    linha_inicio = 0
    coluna_inicio = matriz_score_global.shape[1] - 1
    return construir_alinhamento_da_posicao(
        matriz_score_global,
        matriz_ponteiro_global,
        sequencia_vertical,
        sequencia_horizontal,
        linha_inicio,
        coluna_inicio,
        parar_em_zero=False,
        completar_bordas=True,
    )


def alinhamento_local(matriz_score_local, matriz_ponteiro_local, sequencia_vertical, sequencia_horizontal):
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


def alinhamento_melhor_score(matriz_score_local, matriz_ponteiro_local, sequencia_vertical, sequencia_horizontal):
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
    matriz_score_local,
    matriz_ponteiro_local,
    sequencia_vertical,
    sequencia_horizontal,
    matriz_score_global=None,
    matriz_ponteiro_global=None,
):
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
