from backend import abrir_arquivo, executar_suite_alinhamento, parsear_entrada


if __name__ == '__main__':
    linhas_entrada = abrir_arquivo('input.txt')

    sequencia_vertical, sequencia_horizontal, penalidade_gap, penalidade_mismatch, pontuacao_match = parsear_entrada(linhas_entrada)
    resultado = executar_suite_alinhamento(
        sequencia_vertical,
        sequencia_horizontal,
        penalidade_gap,
        penalidade_mismatch,
        pontuacao_match,
    )

    print(resultado['matriz_score_global'])
    print(resultado['matriz_ponteiro_global'])
    print(resultado['matriz_score_local'])
    print(resultado['matriz_ponteiro_local'])
    print({
        'vertical_global': resultado['vertical_global'],
        'horizontal_global': resultado['horizontal_global'],
        'vertical_local': resultado['vertical_local'],
        'horizontal_local': resultado['horizontal_local'],
        'melhor_vertical': resultado['melhor_vertical'],
        'melhor_horizontal': resultado['melhor_horizontal'],
        'melhor_score': resultado['melhor_score'],
    })
