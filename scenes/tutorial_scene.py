from controllers.scenes.tutorial_scene_controller import TutorialSceneController
from views.scenes.tutorial_scene_view import TutorialSceneView


class TutorialScene:
    """Управляет отображением и завершением обучающей сцены."""
    def __init__(self, game):
        self.view = TutorialSceneView(game.screen)
        self.controller = TutorialSceneController(game)

    def handle_events(self):
        self.controller.handle_events()

    def update(self):
        pass

    def draw(self):
        self.view.draw()
