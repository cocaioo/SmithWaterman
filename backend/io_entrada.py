def abrir_arquivo(caminho_arquivo):
    with open(caminho_arquivo, encoding='utf-8') as arquivo_entrada:
        linhas = arquivo_entrada.readlines()
    return linhas


def parsear_entrada(linhas):
    sequencia_vertical = linhas[0].strip()
    sequencia_horizontal = linhas[1].strip()
    penalidade_gap = float(linhas[2])
    penalidade_mismatch = float(linhas[3])
    pontuacao_match = float(linhas[4])
    return sequencia_vertical, sequencia_horizontal, penalidade_gap, penalidade_mismatch, pontuacao_match
