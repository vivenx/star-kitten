import pygame

from settings import HEIGHT, WIDTH


class MenuSceneView:
    def __init__(self, screen):
        self.screen = screen
        self.bg = pygame.image.load("assets/images/menu_bg.png").convert()
        self.bg = pygame.transform.scale(self.bg, (WIDTH, HEIGHT))

    def draw(self):
        self.screen.blit(self.bg, (0, 0))
