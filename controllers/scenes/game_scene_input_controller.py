import pygame


class GameSceneInputController:
    """Обрабатывает пользовательский ввод игровой сцены."""

    def __init__(self, game, model, view, flow, attack_handler):
        self.game = game
        self.model = model
        self.view = view
        self.flow = flow
        self.attack_handler = attack_handler

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.save_manager.save(self.model)
                self.game.running = False

            if self.model.game_over:
                self.flow.handle_game_over_event(event)
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f and self.flow.collect_final_star():
                    continue
                if event.key == pygame.K_f and self.flow.can_enter_boss_exit():
                    self.flow.start_stage_transition()
                    continue
                if event.key == pygame.K_z:
                    self.model.skill_tree_open = not self.model.skill_tree_open
                    continue
                if event.key == pygame.K_r and not self.model.skill_tree_open:
                    self.model.player.use_heal_skill()
                    continue
                if event.key == pygame.K_ESCAPE:
                    self.game.save_manager.save(self.model)
                    self.game.change_scene("menu")

            if self.model.skill_tree_open:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.view.skill_tree_ui.handle_click(event.pos, self.model.player)
                continue
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.attack_handler(event.pos)
