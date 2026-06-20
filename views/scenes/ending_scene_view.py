import pygame

from config import HEIGHT, STAGE_TITLE_FONT_PATH, WIDTH


class EndingSceneView:
    """Отображает изображения и текст финальной истории."""
    PANEL_HEIGHT = 300
    SIDE_MARGIN = 70

    def __init__(self, screen):
        self.screen = screen
        self.frames = [
            pygame.image.load(
                f"assets/images/story/end/frame_{number}.png"
            ).convert_alpha()
            for number in range(1, 6)
        ]
        self.text_font = pygame.font.Font(STAGE_TITLE_FONT_PATH, 25)

    def draw(self, model):
        self.screen.fill((8, 7, 12))
        self._draw_frame(self.frames[model.frame_index])
        self._draw_text(model.text)

    def _draw_frame(self, image):
        max_height = HEIGHT - self.PANEL_HEIGHT
        scale = min(WIDTH / image.get_width(), max_height / image.get_height())
        size = (
            max(1, round(image.get_width() * scale)),
            max(1, round(image.get_height() * scale)),
        )
        frame = pygame.transform.smoothscale(image, size)
        rect = frame.get_rect(center=(WIDTH // 2, max_height // 2))
        self.screen.blit(frame, rect)

    def _draw_text(self, text):
        panel_y = HEIGHT - self.PANEL_HEIGHT
        panel = pygame.Surface((WIDTH, self.PANEL_HEIGHT), pygame.SRCALPHA)
        panel.fill((7, 6, 12, 242))
        self.screen.blit(panel, (0, panel_y))
        pygame.draw.line(
            self.screen,
            (169, 139, 78),
            (self.SIDE_MARGIN, panel_y),
            (WIDTH - self.SIDE_MARGIN, panel_y),
            2,
        )

        y = panel_y + 30
        for line in text.splitlines():
            rendered = self.text_font.render(line, True, (244, 239, 222))
            self.screen.blit(rendered, (self.SIDE_MARGIN, y))
            y += 36
