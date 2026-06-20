import pygame

from controllers.scenes.game_scene_flow_controller import GameSceneFlowController
from controllers.scenes.game_scene_input_controller import GameSceneInputController
from controllers.systems.combat_system import CombatContext
from views.effects.visual_effects import DamageNumber
from config import DAMAGE_NUMBER_ENEMY_HIT_COLOR, DAMAGE_NUMBER_PLAYER_HIT_COLOR


class GameSceneController:
    """Координирует обновление игрока, боя, врагов и игрового мира."""
    def __init__(self, game, model, view):
        self.game = game
        self.model = model
        self.view = view
        self.autosave_elapsed = 0.0
        self.autosave_interval = 5.0
        self.flow = GameSceneFlowController(game, model, view)
        self.input = GameSceneInputController(
            game, model, view, self.flow, self._handle_player_attack
        )

    def handle_events(self):
        self.input.handle_events()

    def update(self, dt=None):
        if self.model.skill_tree_open or self.model.game_over:
            return

        if dt is None:
            dt = self.game.clock.get_time() / 1000.0

        self.autosave_elapsed += dt
        if self.autosave_elapsed >= self.autosave_interval:
            self.autosave_elapsed = 0.0
            self.game.save_manager.save(self.model)

        if self.model.stage_manager:
            self.model.stage_manager.update(dt)

        if self.model.player and not self.model.stage_manager.is_transitioning():
            self._update_player(dt)
            self._update_world_systems(dt)
            if self.model.game_over:
                return
            self._update_enemies(dt)
            self.flow.update_final_star_prompt()
            self.flow.check_exit_zone()

        self.flow.sync_stage_change()

    def _handle_player_attack(self, mouse_pos):
        self.model.combat_system.handle_player_attack(
            mouse_pos,
            self._combat_context(),
        )

    def _combat_context(self):
        return CombatContext(
            player=self.model.player,
            enemy_manager=self.model.enemy_manager,
            loot_system=self.model.loot_system,
            on_damage_events=self._spawn_damage_numbers_from_events,
            on_stage_clear=self._update_stage_clear_state,
            is_transitioning=self.model.stage_manager.is_transitioning(),
        )

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
        self.model.combat_system.update(dt, self._combat_context())
        self._handle_collisions(dt)

    def _handle_collisions(self, dt):
        self.model.player_collision_system.handle_stage_collisions(
            self.model.player,
            self.model.stage_manager.current_stage,
            dt,
            self.flow.on_player_death
        )
        self.model.loot_system.collect_for_player(self.model.player)

    def _update_enemies(self, dt):
        if not self.model.enemy_manager:
            return

        player_died = self.model.enemy_manager.update(dt)
        if player_died or not self.model.player.is_alive():
            self.flow.on_player_death()
            return

        self._spawn_damage_numbers_from_events()
        self._update_stage_clear_state()

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
