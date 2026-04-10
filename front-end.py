import sys

import numpy as np
import pygame

import main as backend


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 820
FPS = 60

BG_COLOR = (22, 24, 29)
PANEL_COLOR = (30, 33, 40)
INPUT_BG_COLOR = (18, 20, 26)
INPUT_BORDER_COLOR = (90, 95, 110)
INPUT_ACTIVE_COLOR = (90, 160, 255)
TEXT_COLOR = (232, 236, 245)
MUTED_TEXT_COLOR = (170, 178, 196)
BUTTON_COLOR = (52, 115, 224)
BUTTON_HOVER_COLOR = (70, 134, 240)
BUTTON_TEXT_COLOR = (245, 248, 255)
ERROR_COLOR = (235, 90, 90)
SUCCESS_COLOR = (95, 201, 124)


class InputField:
    def __init__(self, label, text, rect, numeric=False):
        self.label = label
        self.text = text
        self.rect = pygame.Rect(rect)
        self.numeric = numeric
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_TAB:
                return "tab"
            elif event.key == pygame.K_RETURN:
                return "enter"
            else:
                char = event.unicode
                if not char:
                    return None

                if self.numeric:
                    if self._can_add_numeric_char(char):
                        self.text += char
                else:
                    if char.isalpha():
                        self.text += char.upper()
        return None

    def _can_add_numeric_char(self, char):
        if char.isdigit():
            return True
        if char == "-" and len(self.text) == 0:
            return True
        if char == "." and "." not in self.text:
            return True
        return False

    def draw(self, surface, label_font, input_font):
        label_surface = label_font.render(self.label, True, MUTED_TEXT_COLOR)
        surface.blit(label_surface, (self.rect.x, self.rect.y - 24))

        border_color = INPUT_ACTIVE_COLOR if self.active else INPUT_BORDER_COLOR
        pygame.draw.rect(surface, INPUT_BG_COLOR, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=8)

        text_surface = input_font.render(self.text, True, TEXT_COLOR)
        text_y = self.rect.y + (self.rect.height - text_surface.get_height()) // 2
        surface.blit(text_surface, (self.rect.x + 10, text_y))


class Button:
    def __init__(self, text, rect):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

    def draw(self, surface, font):
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        text_surface = font.render(self.text, True, BUTTON_TEXT_COLOR)
        text_x = self.rect.x + (self.rect.width - text_surface.get_width()) // 2
        text_y = self.rect.y + (self.rect.height - text_surface.get_height()) // 2
        surface.blit(text_surface, (text_x, text_y))


def matrix_to_lines(matrix):
    lines = []

    if np.issubdtype(matrix.dtype, np.integer):
        for row in matrix:
            lines.append(" ".join(f"{int(value):4d}" for value in row))
    else:
        for row in matrix:
            lines.append(" ".join(f"{float(value):7.1f}" for value in row))

    return lines


def load_defaults():
    try:
        input_lines = backend.openFilee("input.txt")
        vertical_sequence, horizontal_sequence, gap_penalty, mismatch_penalty, match_score = backend.parseInput(input_lines)
        return {
            "vertical_sequence": vertical_sequence,
            "horizontal_sequence": horizontal_sequence,
            "gap_penalty": str(gap_penalty),
            "mismatch_penalty": str(mismatch_penalty),
            "match_score": str(match_score),
        }
    except Exception:
        return {
            "vertical_sequence": "AATG",
            "horizontal_sequence": "TTGA",
            "gap_penalty": "-2",
            "mismatch_penalty": "-1",
            "match_score": "1",
        }


class SmithWatermanUI:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Smith-Waterman Interactive UI")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        self.title_font = pygame.font.SysFont("Segoe UI", 32, bold=True)
        self.label_font = pygame.font.SysFont("Segoe UI", 18)
        self.input_font = pygame.font.SysFont("Consolas", 22)
        self.button_font = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.mono_font = pygame.font.SysFont("Consolas", 20)

        defaults = load_defaults()
        self.input_fields = [
            InputField("Vertical sequence", defaults["vertical_sequence"], (20, 70, 220, 42), numeric=False),
            InputField("Horizontal sequence", defaults["horizontal_sequence"], (260, 70, 220, 42), numeric=False),
            InputField("Gap penalty", defaults["gap_penalty"], (500, 70, 150, 42), numeric=True),
            InputField("Mismatch penalty", defaults["mismatch_penalty"], (670, 70, 170, 42), numeric=True),
            InputField("Match score", defaults["match_score"], (860, 70, 150, 42), numeric=True),
        ]

        self.run_button = Button("Run alignment", (1030, 70, 220, 42))

        self.status_text = "Ready"
        self.status_color = MUTED_TEXT_COLOR

        self.output_lines = [
            "Press 'Run alignment' to execute Smith-Waterman.",
            "Use mouse wheel to scroll output panel.",
        ]
        self.scroll_offset = 0

        self.output_panel = pygame.Rect(20, 150, WINDOW_WIDTH - 40, WINDOW_HEIGHT - 170)

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    continue

                if self.run_button.handle_event(event):
                    self.execute_alignment()

                for index, input_field in enumerate(self.input_fields):
                    action = input_field.handle_event(event)
                    if action == "tab":
                        input_field.active = False
                        self.input_fields[(index + 1) % len(self.input_fields)].active = True
                    elif action == "enter":
                        self.execute_alignment()

                if event.type == pygame.MOUSEWHEEL:
                    self.scroll_offset -= event.y
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.scroll_offset -= 1
                    elif event.key == pygame.K_DOWN:
                        self.scroll_offset += 1
                    elif event.key == pygame.K_F5:
                        self.execute_alignment()

            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit(0)

    def execute_alignment(self):
        try:
            vertical_sequence = self.input_fields[0].text.strip().upper()
            horizontal_sequence = self.input_fields[1].text.strip().upper()
            gap_penalty = float(self.input_fields[2].text.strip())
            mismatch_penalty = float(self.input_fields[3].text.strip())
            match_score = float(self.input_fields[4].text.strip())

            if not vertical_sequence or not horizontal_sequence:
                raise ValueError("Sequences must not be empty")

            alignment_result = backend.runAlignmentSuite(
                vertical_sequence,
                horizontal_sequence,
                gap_penalty,
                mismatch_penalty,
                match_score,
            )

            best_score = float(alignment_result["best_score"])

            lines = [
                "Smith-Waterman output",
                "",
                f"Vertical sequence  : {vertical_sequence}",
                f"Horizontal sequence: {horizontal_sequence}",
                f"Gap penalty        : {gap_penalty}",
                f"Mismatch penalty   : {mismatch_penalty}",
                f"Match score        : {match_score}",
                "",
                "Global alignment",
                f"Vertical  : {alignment_result['global_vertical']}",
                f"Horizontal: {alignment_result['global_horizontal']}",
                "",
                "Local alignment",
                f"Vertical  : {alignment_result['local_vertical']}",
                f"Horizontal: {alignment_result['local_horizontal']}",
                "",
                "Best alignment",
                f"Vertical  : {alignment_result['best_vertical']}",
                f"Horizontal: {alignment_result['best_horizontal']}",
                f"Best score: {best_score:.2f}",
                "",
                "Global score matrix:",
            ]

            lines.extend(matrix_to_lines(alignment_result["global_score_matrix"]))
            lines.append("")
            lines.append("Global pointer matrix:")
            lines.extend(matrix_to_lines(alignment_result["global_pointer_matrix"]))
            lines.append("")
            lines.append("Local score matrix:")
            lines.extend(matrix_to_lines(alignment_result["local_score_matrix"]))
            lines.append("")
            lines.append("Local pointer matrix:")
            lines.extend(matrix_to_lines(alignment_result["local_pointer_matrix"]))

            self.output_lines = lines
            self.scroll_offset = 0
            self.status_text = "Alignment executed successfully"
            self.status_color = SUCCESS_COLOR

        except Exception as error:
            self.status_text = f"Error: {error}"
            self.status_color = ERROR_COLOR

    def draw(self):
        self.screen.fill(BG_COLOR)

        header_surface = self.title_font.render("Smith-Waterman Front-End", True, TEXT_COLOR)
        self.screen.blit(header_surface, (20, 20))

        for input_field in self.input_fields:
            input_field.draw(self.screen, self.label_font, self.input_font)

        self.run_button.draw(self.screen, self.button_font)

        status_surface = self.label_font.render(self.status_text, True, self.status_color)
        self.screen.blit(status_surface, (20, 125))

        self.draw_output_panel()

        pygame.display.flip()

    def draw_output_panel(self):
        pygame.draw.rect(self.screen, PANEL_COLOR, self.output_panel, border_radius=12)
        pygame.draw.rect(self.screen, INPUT_BORDER_COLOR, self.output_panel, width=2, border_radius=12)

        line_height = self.mono_font.get_linesize() + 2
        max_visible_lines = max(1, (self.output_panel.height - 20) // line_height)
        max_scroll = max(0, len(self.output_lines) - max_visible_lines)

        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

        start = self.scroll_offset
        end = start + max_visible_lines
        visible_lines = self.output_lines[start:end]

        y = self.output_panel.y + 10
        for line in visible_lines:
            line_surface = self.mono_font.render(line, True, TEXT_COLOR)
            self.screen.blit(line_surface, (self.output_panel.x + 12, y))
            y += line_height


if __name__ == "__main__":
    SmithWatermanUI().run()