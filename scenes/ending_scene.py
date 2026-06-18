from controllers.scenes.ending_scene_controller import EndingSceneController
from models.scenes.ending_scene_model import EndingSceneModel
from views.scenes.ending_scene_view import EndingSceneView


class EndingScene:
    def __init__(self, game):
        self.model = EndingSceneModel()
        self.view = EndingSceneView(game.screen)
        self.controller = EndingSceneController(game, self.model)

    def handle_events(self):
        self.controller.handle_events()

    def update(self):
        pass

    def draw(self):
        self.view.draw(self.model)
