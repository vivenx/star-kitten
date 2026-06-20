import pygame

from config import HEIGHT, WIDTH


class TutorialSceneView:
    """Отображает изображение с правилами управления и обучения."""
    def __init__(self, screen):
        self.screen = screen
        image = pygame.image.load("assets/images/tutor.png").convert()
        scale = min(WIDTH / image.get_width(), HEIGHT / image.get_height())
        size = (
            max(1, round(image.get_width() * scale)),
            max(1, round(image.get_height() * scale)),
        )
        self.image = pygame.transform.smoothscale(image, size)
        self.image_rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    def draw(self):
        self.screen.fill((5, 4, 10))
        self.screen.blit(self.image, self.image_rect)
