import pygame


class IntroSceneController:
    def __init__(self, game, model):
        self.game = game
        self.model = model

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.finish_intro()
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_RIGHT):
                    self._advance()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._advance()

    def _advance(self):
        if not self.model.advance():
            self.game.finish_intro()
