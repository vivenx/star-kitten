from controllers.scenes.game_scene_controller import GameSceneController
from models.scenes.game_scene_model import GameSceneModel
from views.scenes.game_scene_view import GameSceneView


class GameScene:
    def __init__(self, game):
        self.game = game
        self.model = GameSceneModel()
        self.view = GameSceneView(game.screen, self.model)
        self.controller = GameSceneController(game, self.model, self.view)

    def handle_events(self):
        self.controller.handle_events()

    def update(self):
        dt = self.game.clock.get_time() / 1000.0
        self.controller.update(dt)
        self.view.update(dt)

    def draw(self):
        self.view.draw()
