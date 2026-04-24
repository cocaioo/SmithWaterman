"""Aplicacao pygame para executar e visualizar o algoritmo Smith-Waterman."""

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
    INDICE_SEQUENCIA_VERTICAL = 0
    INDICE_SEQUENCIA_HORIZONTAL = 1
    INDICE_PENALIDADE_GAP = 2
    INDICE_PENALIDADE_MISMATCH = 3
    INDICE_PONTUACAO_MATCH = 4

    MENSAGENS_INICIAIS = [
        "Pressione 'Executar alinhamento' para rodar Smith-Waterman.",
        'Use a roda do mouse para rolar o painel de saida.',
    ]

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption('Smith-Waterman Interactive UI')

        self.tela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
        self.relogio = pygame.time.Clock()

        self._inicializar_fontes()

        self.campos_entrada = self._criar_campos_entrada()
        self.botao_executar = Botao('Executar alinhamento', (1030, 70, 220, 42))

        self.texto_status = 'Pronto'
        self.cor_status = COR_TEXTO_SECUNDARIO

        self.linhas_saida = self.MENSAGENS_INICIAIS.copy()
        self.deslocamento_scroll = 0

        self.painel_saida = pygame.Rect(20, 150, LARGURA_JANELA - 40, ALTURA_JANELA - 170)

    def _inicializar_fontes(self) -> None:
        self.fonte_titulo = pygame.font.SysFont('Segoe UI', 32, bold=True)
        self.fonte_rotulo = pygame.font.SysFont('Segoe UI', 18)
        self.fonte_input = pygame.font.SysFont('Consolas', 22)
        self.fonte_botao = pygame.font.SysFont('Segoe UI', 20, bold=True)
        self.fonte_mono = pygame.font.SysFont('Consolas', 20)

    def _criar_campos_entrada(self) -> list[CampoEntrada]:
        padroes = carregar_padroes()
        especificacoes_campos = [
            ('Sequencia vertical', 'sequencia_vertical', (20, 70, 220, 42), False),
            ('Sequencia horizontal', 'sequencia_horizontal', (260, 70, 220, 42), False),
            ('Penalidade gap', 'penalidade_gap', (500, 70, 150, 42), True),
            ('Penalidade mismatch', 'penalidade_mismatch', (670, 70, 170, 42), True),
            ('Pontuacao match', 'pontuacao_match', (860, 70, 150, 42), True),
        ]

        return [
            CampoEntrada(rotulo, padroes[chave], retangulo, numerico=numerico)
            for rotulo, chave, retangulo, numerico in especificacoes_campos
        ]

    def executar(self) -> None:
        em_execucao = True

        while em_execucao:
            em_execucao = self._processar_eventos()
            self.desenhar()
            self.relogio.tick(FPS)

        pygame.quit()
        sys.exit(0)

    def _processar_eventos(self) -> bool:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False

            if self.botao_executar.tratar_evento(evento):
                self.executar_alinhamento()

            self._processar_eventos_campos(evento)
            self._processar_scroll_e_atalhos(evento)

        return True

    def _processar_eventos_campos(self, evento: pygame.event.Event) -> None:
        for indice, campo_entrada in enumerate(self.campos_entrada):
            acao = campo_entrada.tratar_evento(evento)
            if acao == 'tab':
                self._ativar_proximo_campo(indice)
            elif acao == 'enter':
                self.executar_alinhamento()

    def _ativar_proximo_campo(self, indice_atual: int) -> None:
        self.campos_entrada[indice_atual].ativo = False
        proximo_indice = (indice_atual + 1) % len(self.campos_entrada)
        self.campos_entrada[proximo_indice].ativo = True

    def _processar_scroll_e_atalhos(self, evento: pygame.event.Event) -> None:
        if evento.type == pygame.MOUSEWHEEL:
            self.deslocamento_scroll -= evento.y
            return

        if evento.type != pygame.KEYDOWN:
            return

        if evento.key == pygame.K_UP:
            self.deslocamento_scroll -= 1
        elif evento.key == pygame.K_DOWN:
            self.deslocamento_scroll += 1
        elif evento.key == pygame.K_F5:
            self.executar_alinhamento()

    def _ler_entrada_parametros(self) -> tuple[str, str, float, float, float]:
        sequencia_vertical = self.campos_entrada[self.INDICE_SEQUENCIA_VERTICAL].texto.strip().upper()
        sequencia_horizontal = self.campos_entrada[self.INDICE_SEQUENCIA_HORIZONTAL].texto.strip().upper()
        penalidade_gap = float(self.campos_entrada[self.INDICE_PENALIDADE_GAP].texto.strip())
        penalidade_mismatch = float(self.campos_entrada[self.INDICE_PENALIDADE_MISMATCH].texto.strip())
        pontuacao_match = float(self.campos_entrada[self.INDICE_PONTUACAO_MATCH].texto.strip())

        return (
            sequencia_vertical,
            sequencia_horizontal,
            penalidade_gap,
            penalidade_mismatch,
            pontuacao_match,
        )

    @staticmethod
    def _validar_sequencias(sequencia_vertical: str, sequencia_horizontal: str) -> None:
        if not sequencia_vertical or not sequencia_horizontal:
            raise ValueError('As sequencias nao podem ser vazias')

    def executar_alinhamento(self) -> None:
        try:
            (
                sequencia_vertical,
                sequencia_horizontal,
                penalidade_gap,
                penalidade_mismatch,
                pontuacao_match,
            ) = self._ler_entrada_parametros()
            self._validar_sequencias(sequencia_vertical, sequencia_horizontal)

            resultado_alinhamento = backend.executar_suite_alinhamento(
                sequencia_vertical,
                sequencia_horizontal,
                penalidade_gap,
                penalidade_mismatch,
                pontuacao_match,
            )

            self.linhas_saida = self._montar_linhas_resultado(
                resultado_alinhamento,
                sequencia_vertical,
                sequencia_horizontal,
                penalidade_gap,
                penalidade_mismatch,
                pontuacao_match,
            )
            self.deslocamento_scroll = 0
            self._atualizar_status('Alinhamento executado com sucesso', COR_SUCESSO)
        except Exception as erro:
            self._atualizar_status(f'Erro: {erro}', COR_ERRO)

    @staticmethod
    def _atualizar_linhas_com_matriz(
        linhas: list[str],
        titulo: str,
        matriz: object,
    ) -> None:
        linhas.append(titulo)
        linhas.extend(matriz_para_linhas(matriz))
        linhas.append('')

    def _montar_linhas_resultado(
        self,
        resultado_alinhamento: dict[str, object],
        sequencia_vertical: str,
        sequencia_horizontal: str,
        penalidade_gap: float,
        penalidade_mismatch: float,
        pontuacao_match: float,
    ) -> list[str]:
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
        ]

        self._atualizar_linhas_com_matriz(
            linhas,
            'Matriz de score global:',
            resultado_alinhamento['matriz_score_global'],
        )
        self._atualizar_linhas_com_matriz(
            linhas,
            'Matriz de ponteiros global:',
            resultado_alinhamento['matriz_ponteiro_global'],
        )
        self._atualizar_linhas_com_matriz(
            linhas,
            'Matriz de score local:',
            resultado_alinhamento['matriz_score_local'],
        )

        linhas.append('Matriz de ponteiros local:')
        linhas.extend(matriz_para_linhas(resultado_alinhamento['matriz_ponteiro_local']))
        return linhas

    def _atualizar_status(self, texto: str, cor: tuple[int, int, int]) -> None:
        self.texto_status = texto
        self.cor_status = cor

    def desenhar(self) -> None:
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

    def desenhar_painel_saida(self) -> None:
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
