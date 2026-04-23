import numpy as np


def matriz_para_linhas(matriz):
    linhas = []

    if np.issubdtype(matriz.dtype, np.integer):
        for linha in matriz:
            linhas.append(' '.join(f'{int(valor):4d}' for valor in linha))
    else:
        for linha in matriz:
            linhas.append(' '.join(f'{float(valor):7.1f}' for valor in linha))

    return linhas
