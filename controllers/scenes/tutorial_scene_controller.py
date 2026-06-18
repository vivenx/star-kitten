import pygame


class TutorialSceneController:
    def __init__(self, game):
        self.game = game

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
            elif event.type == pygame.KEYDOWN and event.key in (
                pygame.K_ESCAPE,
                pygame.K_SPACE,
                pygame.K_RETURN,
                pygame.K_RIGHT,
            ):
                self.game.finish_tutorial()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.game.finish_tutorial()
