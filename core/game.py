import pygame
from settings import WIDTH, HEIGHT, FPS
from controllers.managers.save_manager import SaveManager
from scenes.menu_scene import MenuScene
from scenes.game_scene import GameScene
from scenes.intro_scene import IntroScene
from scenes.tutorial_scene import TutorialScene
from scenes.ending_scene import EndingScene


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Star Kitten")
        self.clock = pygame.time.Clock()
        self.running = True
        self.save_manager = SaveManager()

        self.scenes = {
            "menu": MenuScene(self),
            "game": GameScene(self),
        }

        self.current_scene = self.scenes["menu"]

    def change_scene(self, scene_name):
        self.current_scene = self.scenes[scene_name]

    def start_new_game(self):
        self.save_manager.delete()
        self.scenes["game"] = GameScene(self)
        self.save_manager.save(self.scenes["game"].model)
        self.scenes["intro"] = IntroScene(self)
        self.change_scene("intro")

    def finish_intro(self):
        self.scenes["tutorial"] = TutorialScene(self)
        self.change_scene("tutorial")

    def finish_tutorial(self):
        self.change_scene("game")

    def start_final_cutscene(self):
        self.scenes["final_cutscene"] = EndingScene(self)
        self.change_scene("final_cutscene")

    def finish_ending(self):
        game_scene = self.scenes["game"]
        if game_scene.model.start_endless_mode():
            self.save_manager.save(game_scene.model)
            self.change_scene("game")
        else:
            self.change_scene("menu")

    def continue_game(self):
        save_data = self.save_manager.load()
        if save_data is None:
            return False

        game_scene = GameScene(self)
        if not game_scene.model.restore_save_data(save_data):
            return False
        self.scenes["game"] = game_scene
        self.change_scene("game")
        return True

    def run(self):
        while self.running:
            self.clock.tick(FPS)

            self.current_scene.handle_events()
            self.current_scene.update()
            self.current_scene.draw()

            pygame.display.flip()

        pygame.quit()
