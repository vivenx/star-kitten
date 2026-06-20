import pygame

from config import HEIGHT, WIDTH


class MenuSceneView:
    """Отображает главное меню и диалог подтверждения новой игры."""
    def __init__(self, screen):
        self.screen = screen
        self.bg = pygame.image.load("assets/images/menu_bg.png").convert()
        self.bg = pygame.transform.scale(self.bg, (WIDTH, HEIGHT))
        confirmation = pygame.image.load("assets/images/new_game.png").convert_alpha()
        confirmation_size = (870, 600)
        self.confirmation = pygame.transform.smoothscale(confirmation, confirmation_size)
        self.confirmation_rect = self.confirmation.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 150))

        # Button coordinates are proportional to their positions in new_game.png.
        self.confirm_yes_rect = pygame.Rect(
            self.confirmation_rect.x + 202,
            self.confirmation_rect.y + 424,
            220,
            76,
        )
        self.confirm_no_rect = pygame.Rect(
            self.confirmation_rect.x + 451,
            self.confirmation_rect.y + 424,
            220,
            76,
        )

    def draw(self, confirmation_visible=False):
        self.screen.blit(self.bg, (0, 0))
        if confirmation_visible:
            self.screen.blit(self.overlay, (0, 0))
            self.screen.blit(self.confirmation, self.confirmation_rect)
