from controllers.scenes.frame_scene_controller import FrameSceneController


class EndingSceneController(FrameSceneController):
    """Управляет переключением кадров и завершением финальной сцены."""
    def __init__(self, game, model):
        """Создаёт контроллер финальной сцены."""
        super().__init__(game, model, game.finish_ending)
