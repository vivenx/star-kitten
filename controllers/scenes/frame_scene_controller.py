import pygame


class FrameSceneController:
    """Управляет общей логикой покадровой сюжетной сцены."""

    def __init__(self, game, model, finish_scene):
        """Сохраняет зависимости и действие завершения сцены."""
        self.game = game
        self.model = model
        self._finish_scene = finish_scene

    def handle_events(self):
        """Обрабатывает закрытие игры и переход к следующему кадру."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._finish_scene()
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_RIGHT):
                    self._advance()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._advance()

    def _advance(self):
        """Показывает следующий кадр или завершает сцену."""
        if not self.model.advance():
            self._finish_scene()
