"""Leitura e parsing do arquivo de entrada do alinhamento."""

from collections.abc import Sequence


def abrir_arquivo(caminho_arquivo: str) -> list[str]:
    """Retorna as linhas do arquivo de entrada mantendo a ordem original."""
    with open(caminho_arquivo, encoding='utf-8') as arquivo_entrada:
        return arquivo_entrada.readlines()


def _validar_quantidade_minima_linhas(linhas: Sequence[str]) -> None:
    if len(linhas) < 5:
        raise ValueError('O arquivo de entrada deve conter ao menos 5 linhas.')


def parsear_entrada(linhas: Sequence[str]) -> tuple[str, str, float, float, float]:
    """Converte as 5 linhas esperadas em parametros para o algoritmo."""
    _validar_quantidade_minima_linhas(linhas)

    sequencia_vertical = linhas[0].strip()
    sequencia_horizontal = linhas[1].strip()

    try:
        penalidade_gap = float(linhas[2])
        penalidade_mismatch = float(linhas[3])
        pontuacao_match = float(linhas[4])
    except ValueError as erro:
        raise ValueError('As linhas 3, 4 e 5 devem conter valores numericos.') from erro

    return (
        sequencia_vertical,
        sequencia_horizontal,
        penalidade_gap,
        penalidade_mismatch,
        pontuacao_match,
    )
