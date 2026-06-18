from controllers.scenes.intro_scene_controller import IntroSceneController
from models.scenes.intro_scene_model import IntroSceneModel
from views.scenes.intro_scene_view import IntroSceneView


class IntroScene:
    def __init__(self, game):
        self.model = IntroSceneModel()
        self.view = IntroSceneView(game.screen)
        self.controller = IntroSceneController(game, self.model)

    def handle_events(self):
        self.controller.handle_events()

    def update(self):
        pass

    def draw(self):
        self.view.draw(self.model)
