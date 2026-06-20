from controllers.scenes.menu_scene_controller import MenuSceneController
from models.scenes.menu_scene_model import MenuSceneModel
from views.scenes.menu_scene_view import MenuSceneView


class MenuScene:
    """Объединяет модель, представление и контроллер главного меню."""
    def __init__(self, game):
        self.model = MenuSceneModel()
        self.view = MenuSceneView(game.screen)
        self.controller = MenuSceneController(game, self.model, self.view)

    def handle_events(self):
        self.controller.handle_events()

    def update(self):
        self.controller.update()

    def draw(self):
        self.view.draw(self.model.new_game_confirmation_visible)
