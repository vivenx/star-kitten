import pygame
from settings import WIDTH, HEIGHT, FPS
from scenes.menu_scene import MenuScene
from scenes.game_scene import GameScene


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Star Kitten")
        self.clock = pygame.time.Clock()
        self.running = True

        self.scenes = {
            "menu": MenuScene(self),
            "game": GameScene(self),
        }

        self.current_scene = self.scenes["menu"]

    def change_scene(self, scene_name):
        self.current_scene = self.scenes[scene_name]

    def run(self):
        while self.running:
            self.clock.tick(FPS)

            self.current_scene.handle_events()
            self.current_scene.update()
            self.current_scene.draw()

            pygame.display.flip()

        pygame.quit()
