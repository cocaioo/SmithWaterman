import backend


def carregar_padroes():
    try:
        linhas_entrada = backend.abrir_arquivo('input.txt')
        sequencia_vertical, sequencia_horizontal, penalidade_gap, penalidade_mismatch, pontuacao_match = backend.parsear_entrada(linhas_entrada)
        return {
            'sequencia_vertical': sequencia_vertical,
            'sequencia_horizontal': sequencia_horizontal,
            'penalidade_gap': str(penalidade_gap),
            'penalidade_mismatch': str(penalidade_mismatch),
            'pontuacao_match': str(pontuacao_match),
        }
    except Exception:
        return {
            'sequencia_vertical': 'AATG',
            'sequencia_horizontal': 'TTGA',
            'penalidade_gap': '-2',
            'penalidade_mismatch': '-1',
            'pontuacao_match': '1',
        }
