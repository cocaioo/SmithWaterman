"""Widgets reutilizaveis da interface pygame."""

from typing import Literal

import pygame

from .constantes_ui import (
    COR_BORDA_INPUT,
    COR_BOTAO,
    COR_BOTAO_HOVER,
    COR_INPUT_ATIVO,
    COR_INPUT_FUNDO,
    COR_TEXTO,
    COR_TEXTO_BOTAO,
    COR_TEXTO_SECUNDARIO,
)

AcaoCampo = Literal['tab', 'enter']


class CampoEntrada:
    def __init__(
        self,
        rotulo: str,
        texto: str,
        retangulo: tuple[int, int, int, int],
        numerico: bool = False,
    ) -> None:
        self.rotulo = rotulo
        self.texto = texto
        self.retangulo = pygame.Rect(retangulo)
        self.numerico = numerico
        self.ativo = False

    def tratar_evento(self, evento: pygame.event.Event) -> AcaoCampo | None:
        if evento.type == pygame.MOUSEBUTTONDOWN:
            self.ativo = self.retangulo.collidepoint(evento.pos)

        if evento.type != pygame.KEYDOWN or not self.ativo:
            return None

        return self._tratar_evento_teclado(evento)

    def _tratar_evento_teclado(self, evento: pygame.event.Event) -> AcaoCampo | None:
        if evento.key == pygame.K_BACKSPACE:
            self.texto = self.texto[:-1]
            return None

        if evento.key == pygame.K_TAB:
            return 'tab'

        if evento.key == pygame.K_RETURN:
            return 'enter'

        caractere = evento.unicode
        if not caractere:
            return None

        if self.numerico:
            if self._pode_adicionar_caractere_numerico(caractere):
                self.texto += caractere
            return None

        if caractere.isalpha():
            self.texto += caractere.upper()
        return None

    def _pode_adicionar_caractere_numerico(self, caractere: str) -> bool:
        if caractere.isdigit():
            return True
        if caractere == '-' and len(self.texto) == 0:
            return True
        if caractere == '.' and '.' not in self.texto:
            return True
        return False

    def desenhar(
        self,
        superficie: pygame.Surface,
        fonte_rotulo: pygame.font.Font,
        fonte_input: pygame.font.Font,
    ) -> None:
        superficie_rotulo = fonte_rotulo.render(self.rotulo, True, COR_TEXTO_SECUNDARIO)
        superficie.blit(superficie_rotulo, (self.retangulo.x, self.retangulo.y - 24))

        cor_borda = COR_INPUT_ATIVO if self.ativo else COR_BORDA_INPUT
        pygame.draw.rect(superficie, COR_INPUT_FUNDO, self.retangulo, border_radius=8)
        pygame.draw.rect(superficie, cor_borda, self.retangulo, width=2, border_radius=8)

        superficie_texto = fonte_input.render(self.texto, True, COR_TEXTO)
        y_texto = self.retangulo.y + (self.retangulo.height - superficie_texto.get_height()) // 2
        superficie.blit(superficie_texto, (self.retangulo.x + 10, y_texto))


class Botao:
    def __init__(self, texto: str, retangulo: tuple[int, int, int, int]) -> None:
        self.texto = texto
        self.retangulo = pygame.Rect(retangulo)
        self.hover = False

    def tratar_evento(self, evento: pygame.event.Event) -> bool:
        if evento.type == pygame.MOUSEMOTION:
            self.hover = self.retangulo.collidepoint(evento.pos)

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            return bool(self.retangulo.collidepoint(evento.pos))
        return False

    def desenhar(self, superficie: pygame.Surface, fonte: pygame.font.Font) -> None:
        cor = COR_BOTAO_HOVER if self.hover else COR_BOTAO
        pygame.draw.rect(superficie, cor, self.retangulo, border_radius=10)

        superficie_texto = fonte.render(self.texto, True, COR_TEXTO_BOTAO)
        x_texto = self.retangulo.x + (self.retangulo.width - superficie_texto.get_width()) // 2
        y_texto = self.retangulo.y + (self.retangulo.height - superficie_texto.get_height()) // 2
        superficie.blit(superficie_texto, (x_texto, y_texto))
