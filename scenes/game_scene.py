import pygame
from core.player import Player
from components.health_bar import HealthBar


class GameScene:
    def __init__(self, game):
        self.game = game
        self.player = None
        self.health_bar = None

        self._create_player()
        self._create_health_bar()

    def _create_player(self):
        screen_width, screen_height = self.game.screen.get_size()
        self.player = Player(screen_width // 2 - 50, screen_height // 2 - 50)

    def _create_health_bar(self):
        self.health_bar = HealthBar(10, 10)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.change_scene("menu")

    def update(self):
        if self.player:
            keys = pygame.key.get_pressed()
            dx = 0
            dy = 0

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = 1

            self.player.move(dx, dy)
            self.player.update()

    def draw(self):
        self.game.screen.fill((20, 20, 30))

        if self.player:
            self.game.screen.blit(self.player.image, self.player.rect)
            self._draw_ui()

    def _draw_ui(self):
        """Отрисовка интерфейса с HP"""
        # Отрисовка полоски здоровья через HealthBar
        if self.health_bar:
            self.health_bar.draw(self.game.screen, self.player.hp, self.player.max_hp)