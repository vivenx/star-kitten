import pygame
from settings import WIDTH, HEIGHT


class MenuScene:
    def __init__(self, game):
        self.game = game

        self.bg = pygame.image.load("assets/images/menu_bg.png").convert()
        self.bg = pygame.transform.scale(self.bg, (WIDTH, HEIGHT))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False


    def update(self):
        pass

    def draw(self):
        self.game.screen.blit(self.bg, (0, 0))