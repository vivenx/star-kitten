from controllers.scenes.game_scene_controller import GameSceneController
from models.scenes.game_scene_model import GameSceneModel
from views.scenes.game_scene_view import GameSceneView


class GameScene:
    def __init__(self, game):
        self.game = game
        self.model = GameSceneModel()
        self.controller = GameSceneController(game, self.model)
        self.view = GameSceneView(game.screen, self.model)

    def handle_events(self):
        self.controller.handle_events()

    def update(self):
        self.controller.update()

    def draw(self):
        self.view.draw()
