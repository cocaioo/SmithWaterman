import sys

import pygame

import backend
from .constantes_ui import (
    ALTURA_JANELA,
    COR_BORDA_INPUT,
    COR_ERRO,
    COR_FUNDO,
    COR_PAINEL,
    COR_SUCESSO,
    COR_TEXTO,
    COR_TEXTO_SECUNDARIO,
    FPS,
    LARGURA_JANELA,
)
from .formatacao import matriz_para_linhas
from .padroes import carregar_padroes
from .widgets import Botao, CampoEntrada


class SmithWatermanUI:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Smith-Waterman Interactive UI')
        self.tela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
        self.relogio = pygame.time.Clock()

        self.fonte_titulo = pygame.font.SysFont('Segoe UI', 32, bold=True)
        self.fonte_rotulo = pygame.font.SysFont('Segoe UI', 18)
        self.fonte_input = pygame.font.SysFont('Consolas', 22)
        self.fonte_botao = pygame.font.SysFont('Segoe UI', 20, bold=True)
        self.fonte_mono = pygame.font.SysFont('Consolas', 20)

        padroes = carregar_padroes()
        self.campos_entrada = [
            CampoEntrada('Sequencia vertical', padroes['sequencia_vertical'], (20, 70, 220, 42), numerico=False),
            CampoEntrada('Sequencia horizontal', padroes['sequencia_horizontal'], (260, 70, 220, 42), numerico=False),
            CampoEntrada('Penalidade gap', padroes['penalidade_gap'], (500, 70, 150, 42), numerico=True),
            CampoEntrada('Penalidade mismatch', padroes['penalidade_mismatch'], (670, 70, 170, 42), numerico=True),
            CampoEntrada('Pontuacao match', padroes['pontuacao_match'], (860, 70, 150, 42), numerico=True),
        ]

        self.botao_executar = Botao('Executar alinhamento', (1030, 70, 220, 42))

        self.texto_status = 'Pronto'
        self.cor_status = COR_TEXTO_SECUNDARIO

        self.linhas_saida = [
            "Pressione 'Executar alinhamento' para rodar Smith-Waterman.",
            'Use a roda do mouse para rolar o painel de saida.',
        ]
        self.deslocamento_scroll = 0

        self.painel_saida = pygame.Rect(20, 150, LARGURA_JANELA - 40, ALTURA_JANELA - 170)

    def executar(self):
        em_execucao = True

        while em_execucao:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    em_execucao = False
                    continue

                if self.botao_executar.tratar_evento(evento):
                    self.executar_alinhamento()

                for indice, campo_entrada in enumerate(self.campos_entrada):
                    acao = campo_entrada.tratar_evento(evento)
                    if acao == 'tab':
                        campo_entrada.ativo = False
                        self.campos_entrada[(indice + 1) % len(self.campos_entrada)].ativo = True
                    elif acao == 'enter':
                        self.executar_alinhamento()

                if evento.type == pygame.MOUSEWHEEL:
                    self.deslocamento_scroll -= evento.y
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_UP:
                        self.deslocamento_scroll -= 1
                    elif evento.key == pygame.K_DOWN:
                        self.deslocamento_scroll += 1
                    elif evento.key == pygame.K_F5:
                        self.executar_alinhamento()

            self.desenhar()
            self.relogio.tick(FPS)

        pygame.quit()
        sys.exit(0)

    def executar_alinhamento(self):
        try:
            sequencia_vertical = self.campos_entrada[0].texto.strip().upper()
            sequencia_horizontal = self.campos_entrada[1].texto.strip().upper()
            penalidade_gap = float(self.campos_entrada[2].texto.strip())
            penalidade_mismatch = float(self.campos_entrada[3].texto.strip())
            pontuacao_match = float(self.campos_entrada[4].texto.strip())

            if not sequencia_vertical or not sequencia_horizontal:
                raise ValueError('As sequencias nao podem ser vazias')

            resultado_alinhamento = backend.executar_suite_alinhamento(
                sequencia_vertical,
                sequencia_horizontal,
                penalidade_gap,
                penalidade_mismatch,
                pontuacao_match,
            )

            melhor_score = float(resultado_alinhamento['melhor_score'])

            linhas = [
                'Resultado Smith-Waterman',
                '',
                f'Sequencia vertical  : {sequencia_vertical}',
                f'Sequencia horizontal: {sequencia_horizontal}',
                f'Penalidade gap      : {penalidade_gap}',
                f'Penalidade mismatch : {penalidade_mismatch}',
                f'Pontuacao match     : {pontuacao_match}',
                '',
                'Alinhamento global',
                f"Vertical  : {resultado_alinhamento['vertical_global']}",
                f"Horizontal: {resultado_alinhamento['horizontal_global']}",
                '',
                'Alinhamento local',
                f"Vertical  : {resultado_alinhamento['vertical_local']}",
                f"Horizontal: {resultado_alinhamento['horizontal_local']}",
                '',
                'Melhor alinhamento',
                f"Vertical  : {resultado_alinhamento['melhor_vertical']}",
                f"Horizontal: {resultado_alinhamento['melhor_horizontal']}",
                f'Melhor score: {melhor_score:.2f}',
                '',
                'Matriz de score global:',
            ]

            linhas.extend(matriz_para_linhas(resultado_alinhamento['matriz_score_global']))
            linhas.append('')
            linhas.append('Matriz de ponteiros global:')
            linhas.extend(matriz_para_linhas(resultado_alinhamento['matriz_ponteiro_global']))
            linhas.append('')
            linhas.append('Matriz de score local:')
            linhas.extend(matriz_para_linhas(resultado_alinhamento['matriz_score_local']))
            linhas.append('')
            linhas.append('Matriz de ponteiros local:')
            linhas.extend(matriz_para_linhas(resultado_alinhamento['matriz_ponteiro_local']))

            self.linhas_saida = linhas
            self.deslocamento_scroll = 0
            self.texto_status = 'Alinhamento executado com sucesso'
            self.cor_status = COR_SUCESSO

        except Exception as erro:
            self.texto_status = f'Erro: {erro}'
            self.cor_status = COR_ERRO

    def desenhar(self):
        self.tela.fill(COR_FUNDO)

        superficie_cabecalho = self.fonte_titulo.render('Smith-Waterman Front-End', True, COR_TEXTO)
        self.tela.blit(superficie_cabecalho, (20, 20))

        for campo_entrada in self.campos_entrada:
            campo_entrada.desenhar(self.tela, self.fonte_rotulo, self.fonte_input)

        self.botao_executar.desenhar(self.tela, self.fonte_botao)

        superficie_status = self.fonte_rotulo.render(self.texto_status, True, self.cor_status)
        self.tela.blit(superficie_status, (20, 125))

        self.desenhar_painel_saida()

        pygame.display.flip()

    def desenhar_painel_saida(self):
        pygame.draw.rect(self.tela, COR_PAINEL, self.painel_saida, border_radius=12)
        pygame.draw.rect(self.tela, COR_BORDA_INPUT, self.painel_saida, width=2, border_radius=12)

        altura_linha = self.fonte_mono.get_linesize() + 2
        max_linhas_visiveis = max(1, (self.painel_saida.height - 20) // altura_linha)
        max_scroll = max(0, len(self.linhas_saida) - max_linhas_visiveis)

        self.deslocamento_scroll = max(0, min(self.deslocamento_scroll, max_scroll))

        inicio = self.deslocamento_scroll
        fim = inicio + max_linhas_visiveis
        linhas_visiveis = self.linhas_saida[inicio:fim]

        y_texto = self.painel_saida.y + 10
        for linha in linhas_visiveis:
            superficie_linha = self.fonte_mono.render(linha, True, COR_TEXTO)
            self.tela.blit(superficie_linha, (self.painel_saida.x + 12, y_texto))
            y_texto += altura_linha
