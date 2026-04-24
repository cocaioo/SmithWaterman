"""Entrypoint principal para modo terminal e modo UI."""

import argparse
from pprint import pprint

from backend import abrir_arquivo, executar_suite_alinhamento, parsear_entrada
from frontend import SmithWatermanUI


def _imprimir_resultado_terminal(
    resultado: dict[str, object],
) -> None:
    print(resultado['matriz_score_global'])
    print(resultado['matriz_ponteiro_global'])
    print(resultado['matriz_score_local'])
    print(resultado['matriz_ponteiro_local'])

    resumo = {
        'vertical_global': resultado['vertical_global'],
        'horizontal_global': resultado['horizontal_global'],
        'vertical_local': resultado['vertical_local'],
        'horizontal_local': resultado['horizontal_local'],
        'melhor_vertical': resultado['melhor_vertical'],
        'melhor_horizontal': resultado['melhor_horizontal'],
        'melhor_score': resultado['melhor_score'],
    }
    pprint(resumo)


def executar_terminal(caminho_entrada: str = 'input.txt') -> None:
    linhas_entrada = abrir_arquivo(caminho_entrada)
    (
        sequencia_vertical,
        sequencia_horizontal,
        penalidade_gap,
        penalidade_mismatch,
        pontuacao_match,
    ) = parsear_entrada(linhas_entrada)

    resultado = executar_suite_alinhamento(
        sequencia_vertical,
        sequencia_horizontal,
        penalidade_gap,
        penalidade_mismatch,
        pontuacao_match,
    )
    _imprimir_resultado_terminal(resultado)


def executar_ui() -> None:
    SmithWatermanUI().executar()


def criar_parser_argumentos() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Entry point unico do projeto Smith-Waterman.',
    )
    parser.add_argument(
        '--modo',
        choices=('ui', 'terminal'),
        default='ui',
        help='Define o modo de execucao: ui (padrao) ou terminal.',
    )
    parser.add_argument(
        '--entrada',
        default='input.txt',
        help='Arquivo de entrada usado no modo terminal.',
    )
    return parser


def main() -> None:
    argumentos = criar_parser_argumentos().parse_args()

    if argumentos.modo == 'terminal':
        executar_terminal(argumentos.entrada)
        return

    executar_ui()


if __name__ == '__main__':
    main()
