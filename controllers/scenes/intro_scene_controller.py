from controllers.scenes.frame_scene_controller import FrameSceneController


class IntroSceneController(FrameSceneController):
    """Управляет переключением кадров и завершением вступительной сцены."""
    def __init__(self, game, model):
        """Создаёт контроллер вступительной сцены."""
        super().__init__(game, model, game.finish_intro)
