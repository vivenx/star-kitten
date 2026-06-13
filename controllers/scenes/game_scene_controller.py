import pygame

from views.effects.visual_effects import DamageNumber
from settings import DAMAGE_NUMBER_ENEMY_HIT_COLOR, DAMAGE_NUMBER_PLAYER_HIT_COLOR


class GameSceneController:
    def __init__(self, game, model, view):
        self.game = game
        self.model = model
        self.view = view

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            if self.model.game_over:
                self._handle_game_over_event(event)
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f and self._can_enter_boss_exit():
                    self._start_stage_transition()
                    continue
                if event.key == pygame.K_z:
                    self.model.skill_tree_open = not self.model.skill_tree_open
                    continue
                if event.key == pygame.K_ESCAPE:
                    self.game.change_scene("menu")

            if self.model.skill_tree_open:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.view.skill_tree_ui.handle_click(event.pos, self.model.player)
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_player_attack(event.pos)

    def update(self, dt=None):
        if self.model.skill_tree_open or self.model.game_over:
            return

        if dt is None:
            dt = self.game.clock.get_time() / 1000.0

        if self.model.stage_manager:
            self.model.stage_manager.update(dt)

        self._update_exit_message_timer(dt)

        if self.model.player and not self.model.stage_manager.is_transitioning():
            self._update_player(dt)
            self._update_world_systems(dt)
            if self.model.game_over:
                return
            self._update_enemies(dt)
            self._check_exit_zone()

        self._sync_stage_change()

    def _handle_player_attack(self, mouse_pos):
        self.model.combat_system.handle_player_attack(
            mouse_pos,
            self.model.player,
            self.model.enemy_manager,
            self.model.loot_system,
            self._spawn_damage_numbers_from_events,
            self._update_stage_clear_state,
            self.model.stage_manager.is_transitioning(),
        )

    def _update_exit_message_timer(self, dt):
        if self.model.exit_message_timer <= 0:
            return

        self.model.exit_message_timer -= dt
        if self.model.exit_message_timer < 0:
            self.model.exit_message_timer = 0

    def _update_player(self, dt):
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1

        player = self.model.player
        player.move(dx, dy, dt)
        player.update(dt)
        player.update_cooldown(dt)

    def _update_world_systems(self, dt):
        self.model.loot_system.update(dt)
        for number in self.model.damage_numbers:
            number.update(dt)
        self.model.damage_numbers = [
            number for number in self.model.damage_numbers if number.is_alive()
        ]
        self.model.combat_system.update(
            dt,
            self.model.player,
            self.model.enemy_manager,
            self.model.loot_system,
            self._spawn_damage_numbers_from_events,
            self._update_stage_clear_state
        )
        self._handle_collisions(dt)

    def _handle_collisions(self, dt):
        self.model.player_collision_system.handle_stage_collisions(
            self.model.player,
            self.model.stage_manager.current_stage,
            dt,
            self._on_player_death
        )
        self.model.loot_system.collect_for_player(self.model.player)

    def _update_enemies(self, dt):
        if not self.model.enemy_manager:
            return

        player_died = self.model.enemy_manager.update(dt)
        if player_died or not self.model.player.is_alive():
            self._on_player_death()
            return

        self._spawn_damage_numbers_from_events()
        self._update_stage_clear_state()

    def _on_player_death(self):
        self.model.game_over = True
        self.model.skill_tree_open = False

    def _restart_current_stage(self):
        spawn_pos = self.model.stage_manager.current_stage.player_spawn
        self.model.player.restore_progress_snapshot(self.model.stage_start_progress)
        self.model.player.set_position(spawn_pos.x, spawn_pos.y)
        self.model.player.hp = self.model.player.max_hp
        self.model.reset_runtime_stage_state()
        self.view.reset_runtime_stage_state()
        self.model.reset_enemy_manager_for_current_stage()
        self.model.game_over = False

    def _handle_game_over_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._restart_current_stage()
            elif event.key == pygame.K_ESCAPE:
                self._restart_current_stage()
                self.game.change_scene("menu")
            return

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        if self.view.game_over_retry_rect.collidepoint(event.pos):
            self._restart_current_stage()
        elif self.view.game_over_menu_rect.collidepoint(event.pos):
            self._restart_current_stage()
            self.game.change_scene("menu")

    def _spawn_damage_numbers_from_events(self):
        if not self.model.enemy_manager:
            return

        for event in self.model.enemy_manager.consume_damage_number_events():
            color = (
                DAMAGE_NUMBER_PLAYER_HIT_COLOR
                if event["target"] == "player"
                else DAMAGE_NUMBER_ENEMY_HIT_COLOR
            )
            position = event["position"]
            self.model.damage_numbers.append(
                DamageNumber(position[0], position[1], event["amount"], color)
            )

    def _update_stage_clear_state(self):
        if self.model.stage_cleared or not self.model.enemy_manager:
            return

        if self.model.enemy_manager.is_stage_cleared():
            self.model.stage_cleared = True
            self.view.stage_clear_message.show()

    def _check_exit_zone(self):
        if not self.model.player or not self.model.stage_manager:
            return

        current_stage = self.model.stage_manager.current_stage
        if not current_stage.exit_zone:
            return

        player_collision_rect = self.model.player.get_collision_rect()
        is_inside = current_stage.exit_zone.rect.colliderect(player_collision_rect)
        self.model.cave_prompt_visible = False
        if not is_inside:
            return

        if self.model.enemy_manager and not self.model.enemy_manager.is_stage_cleared():
            self.model.exit_message_timer = self.model.exit_lock_message_time
            return

        if current_stage.stage_index == 2:
            self.model.cave_prompt_visible = self.model.stage_manager.has_next_stage
            return

        if self.model.stage_manager.can_enter_exit_zone():
            self._start_stage_transition()

    def _can_enter_boss_exit(self):
        if (
            not self.model.player
            or not self.model.stage_manager
            or self.model.skill_tree_open
        ):
            return False
        stage = self.model.stage_manager.current_stage
        return (
            stage.stage_index == 2
            and self.model.enemy_manager.is_stage_cleared()
            and stage.exit_zone.rect.colliderect(self.model.player.get_collision_rect())
            and self.model.stage_manager.can_enter_exit_zone()
        )

    def _start_stage_transition(self):
        if self.model.stage_manager.start_transition(self.model.player):
            self.model.cave_prompt_visible = False
            self.view.start_stage_transition()
            return True
        return False

    def _sync_stage_change(self):
        if self.model.stage_manager.current_stage_index == self.model.current_stage_index:
            return

        self.model.current_stage_index = self.model.stage_manager.current_stage_index
        self.model.reset_runtime_stage_state()
        self.view.reset_runtime_stage_state()
        self.model.reset_enemy_manager_for_current_stage()
        self.model.save_stage_start_progress()
