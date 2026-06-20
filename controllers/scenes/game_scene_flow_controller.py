import pygame


class GameSceneFlowController:
    """Управляет смертью игрока, финалом и переходами между этапами."""

    def __init__(self, game, model, view):
        self.game = game
        self.model = model
        self.view = view

    def update_final_star_prompt(self):
        self.model.final_star_prompt_visible = (
            self.model.player is not None
            and self.model.loot_system.has_interactive_star_near(self.model.player)
        )

    def collect_final_star(self):
        if self.model.skill_tree_open or not self.model.player:
            return False
        orb = self.model.loot_system.collect_interactive_star(self.model.player)
        if orb:
            self.model.final_star_prompt_visible = False
            if orb.triggers_cutscene:
                self.model.final_cutscene_requested = True
                self.game.start_final_cutscene()
        return orb is not None

    def on_player_death(self):
        self.model.game_over = True
        self.model.skill_tree_open = False

    def restart_current_stage(self):
        if self.model.stage_manager.endless_mode:
            self.model.stage_manager.reset_endless_run()
            self.model.current_stage_index = self.model.stage_manager.current_stage_index

        spawn_pos = self.model.stage_manager.current_stage.player_spawn
        progress_snapshot = (
            self.model.endless_start_progress
            if self.model.stage_manager.endless_mode
            else self.model.stage_start_progress
        )
        self.model.player.restore_progress_snapshot(progress_snapshot)
        self.model.player.set_position(spawn_pos.x, spawn_pos.y)
        self.model.player.hp = self.model.player.max_hp
        self.model.reset_runtime_stage_state()
        self.view.reset_runtime_stage_state()
        self.model.reset_enemy_manager_for_current_stage()
        self.model.save_stage_start_progress()
        self.game.save_manager.save(self.model)
        self.model.game_over = False

    def handle_game_over_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.restart_current_stage()
            elif event.key == pygame.K_ESCAPE:
                self.restart_current_stage()
                self.game.change_scene("menu")
            return

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        if self.view.game_over_retry_rect.collidepoint(event.pos):
            self.restart_current_stage()
        elif self.view.game_over_menu_rect.collidepoint(event.pos):
            self.restart_current_stage()
            self.game.change_scene("menu")

    def check_exit_zone(self):
        if not self.model.player or not self.model.stage_manager:
            return
        current_stage = self.model.stage_manager.current_stage
        if not current_stage.exit_zone:
            return

        player_rect = self.model.player.get_collision_rect()
        self.model.cave_prompt_visible = False
        if not current_stage.exit_zone.rect.colliderect(player_rect):
            return
        if self.model.enemy_manager and not self.model.enemy_manager.is_stage_cleared():
            return
        if current_stage.boss_type == "forest":
            self.model.cave_prompt_visible = self.model.stage_manager.has_next_stage
            return
        if current_stage.boss_type == "cave" and current_stage.endless:
            self.model.cave_prompt_visible = True
            return
        if self.model.stage_manager.can_enter_exit_zone():
            self.start_stage_transition()

    def can_enter_boss_exit(self):
        if not self.model.player or not self.model.stage_manager or self.model.skill_tree_open:
            return False
        stage = self.model.stage_manager.current_stage
        return (
            stage.boss_type is not None
            and (stage.boss_type == "forest" or stage.endless)
            and self.model.enemy_manager.is_stage_cleared()
            and stage.exit_zone.rect.colliderect(self.model.player.get_collision_rect())
            and self.model.stage_manager.can_enter_exit_zone()
        )

    def start_stage_transition(self):
        if self.model.stage_manager.start_transition(self.model.player):
            self.model.cave_prompt_visible = False
            self.view.start_stage_transition()
            return True
        return False

    def sync_stage_change(self):
        if self.model.stage_manager.current_stage_index == self.model.current_stage_index:
            return
        self.model.current_stage_index = self.model.stage_manager.current_stage_index
        self.model.reset_runtime_stage_state()
        self.view.reset_runtime_stage_state()
        self.model.reset_enemy_manager_for_current_stage()
        self.model.save_stage_start_progress()
        self.game.save_manager.save(self.model)
