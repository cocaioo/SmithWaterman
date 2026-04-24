"""Carga de valores padrao exibidos nos campos da interface."""

import backend

PADROES_FALLBACK = {
    'sequencia_vertical': 'AATG',
    'sequencia_horizontal': 'TTGA',
    'penalidade_gap': '-2',
    'penalidade_mismatch': '-1',
    'pontuacao_match': '1',
}


def _carregar_padroes_do_arquivo(caminho_entrada: str) -> dict[str, str]:
    linhas_entrada = backend.abrir_arquivo(caminho_entrada)
    (
        sequencia_vertical,
        sequencia_horizontal,
        penalidade_gap,
        penalidade_mismatch,
        pontuacao_match,
    ) = backend.parsear_entrada(linhas_entrada)

    return {
        'sequencia_vertical': sequencia_vertical,
        'sequencia_horizontal': sequencia_horizontal,
        'penalidade_gap': str(penalidade_gap),
        'penalidade_mismatch': str(penalidade_mismatch),
        'pontuacao_match': str(pontuacao_match),
    }


def carregar_padroes() -> dict[str, str]:
    """Tenta carregar input.txt; se falhar, retorna padroes seguros."""
    try:
        return _carregar_padroes_do_arquivo('input.txt')
    except (FileNotFoundError, IndexError, ValueError):
        return PADROES_FALLBACK.copy()
