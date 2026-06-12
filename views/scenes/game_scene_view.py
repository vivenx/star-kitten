import pygame

from settings import HEIGHT, WIDTH
from views.entities.enemy_view import EnemyView
from views.entities.boss_view import BossView
from views.entities.loot_view import LootView
from views.entities.player_view import PlayerView
from views.entities.stage_view import StageView
from views.effects.combat_effects_view import CombatEffectsView
from views.effects.visual_effects import StageClearMessage
from views.transitions.fader import Fader
from views.transitions.stage_title import StageTitle
from views.ui.health_bar import HealthBar
from views.ui.skill_tree_ui import SkillTreeUI
from views.ui.xp_bar import XPBar


class GameSceneView:
    def __init__(self, screen, model):
        self.screen = screen
        self.model = model
        self.health_bar = HealthBar(18, 10)
        self.xp_bar = XPBar(18, 74)
        self.stage_clear_message = StageClearMessage()
        self.skill_tree_ui = SkillTreeUI()
        self.exit_message_font = pygame.font.Font(None, 48)
        self.fader = Fader()
        self.stage_title = StageTitle()
        self.enemy_view = EnemyView()
        self.boss_view = BossView()
        self.player_view = PlayerView()
        self.stage_view = StageView()
        self.loot_view = LootView()
        self.combat_effects_view = CombatEffectsView()
        game_over_image = pygame.image.load(
            "assets/images/game_over_screen.png"
        ).convert_alpha()
        game_over_height = int(HEIGHT * 0.88)
        game_over_width = int(
            game_over_image.get_width()
            * game_over_height
            / game_over_image.get_height()
        )
        self.game_over_image = pygame.transform.smoothscale(
            game_over_image, (game_over_width, game_over_height)
        )
        self.game_over_rect = self.game_over_image.get_rect(
            center=(WIDTH // 2, HEIGHT // 2)
        )
        self.game_over_retry_rect = pygame.Rect(
            self.game_over_rect.x + int(game_over_width * 0.21),
            self.game_over_rect.y + int(game_over_height * 0.59),
            int(game_over_width * 0.58),
            int(game_over_height * 0.12)
        )
        self.game_over_menu_rect = pygame.Rect(
            self.game_over_rect.x + int(game_over_width * 0.21),
            self.game_over_rect.y + int(game_over_height * 0.72),
            int(game_over_width * 0.58),
            int(game_over_height * 0.09)
        )

    def update(self, dt):
        self._show_pending_stage_titles()
        self.fader.update(dt)
        self.stage_title.update(dt)
        if self.model.enemy_manager:
            self.enemy_view.update(dt, self.model.enemy_manager.enemies)
            self.boss_view.update(dt, self.model.enemy_manager.enemies)
        self.loot_view.update(dt, self.model.loot_system)
        if self.model.player:
            self.player_view.update(dt, self.model.player)
            self.xp_bar.update(dt, self.model.player)
        self.combat_effects_view.update(dt, self.model.combat_system)
        self.stage_clear_message.update(dt)

    def start_stage_transition(self):
        self._show_pending_stage_titles()
        self.fader.start_fade_out(callback=self._on_stage_fade_out_complete)

    def reset_runtime_stage_state(self):
        self.stage_clear_message.reset()

    def draw(self):
        if self.model.stage_manager:
            self.stage_view.draw_background(
                self.screen,
                self.model.stage_manager.current_stage
            )

        if self.model.player:
            self.loot_view.draw(self.screen, self.model.loot_system)
            self._draw_depth_sorted_world()
            self.combat_effects_view.draw(self.screen, self.model.combat_system)
            for number in self.model.damage_numbers:
                number.draw(self.screen)
            self._draw_ui()

        if self.model.stage_manager:
            self.fader.draw(self.screen)
            self.stage_title.draw(self.screen)

        if self.model.skill_tree_open:
            self.skill_tree_ui.draw(self.screen, self.model.player)

        if self.model.game_over:
            self.screen.blit(self.game_over_image, self.game_over_rect)

    def _draw_depth_sorted_world(self):
        drawables = []
        current_stage = self.model.stage_manager.current_stage

        if self.model.enemy_manager:
            for enemy in self.model.enemy_manager.enemies:
                if getattr(enemy, "is_boss", False):
                    self.boss_view.draw_hazards(self.screen, enemy)

        for obstacle in current_stage.obstacles:
            drawables.append((
                obstacle.get_depth_y(),
                lambda surface, obstacle=obstacle: self.stage_view.draw_obstacle(surface, obstacle),
            ))

        if self.model.enemy_manager:
            for enemy in self.model.enemy_manager.enemies:
                draw_enemy = self.boss_view.draw if getattr(enemy, "is_boss", False) else self.enemy_view.draw
                drawables.append((
                    enemy.get_collision_rect().bottom,
                    lambda surface, enemy=enemy, draw_enemy=draw_enemy: draw_enemy(surface, enemy),
                ))

        drawables.append((self.model.player.get_collision_rect().bottom, self._draw_player))

        for _, draw in sorted(drawables, key=lambda item: item[0]):
            draw(self.screen)

    def _draw_player(self, surface):
        self.player_view.draw(surface, self.model.player)

    def _draw_ui(self):
        if self.model.player:
            self.health_bar.draw(
                self.screen,
                self.model.player.hp,
                self.model.player.max_hp
            )

        if self.model.player:
            self.xp_bar.draw(self.screen, self.model.player)

        self.stage_clear_message.draw(self.screen)

        if self.model.exit_message_timer > 0:
            self._draw_exit_message()

    def _draw_exit_message(self):
        text_surface = self.exit_message_font.render(
            self.model.exit_message,
            True,
            (255, 255, 255)
        )
        shadow_surface = self.exit_message_font.render(
            self.model.exit_message,
            True,
            (20, 20, 20)
        )
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT - 80))
        shadow_rect = shadow_surface.get_rect(center=(WIDTH // 2 + 2, HEIGHT - 78))

        self.screen.blit(shadow_surface, shadow_rect)
        self.screen.blit(text_surface, text_rect)

    def _show_pending_stage_titles(self):
        if not self.model.stage_manager:
            return

        for title, subtitle in self.model.stage_manager.consume_stage_title_events():
            self.stage_title.show(title, subtitle)

    def _on_stage_fade_out_complete(self):
        if not self.model.stage_manager.complete_fade_out():
            return

        self._show_pending_stage_titles()
        self.fader.start_fade_in(callback=self.model.stage_manager.complete_fade_in)
