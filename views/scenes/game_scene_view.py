from settings import HEIGHT, WIDTH


class GameSceneView:
    def __init__(self, screen, model):
        self.screen = screen
        self.model = model

    def draw(self):
        if self.model.stage_manager:
            self.model.stage_manager.draw_background(self.screen)

        if self.model.player:
            self.model.loot_system.draw(self.screen)
            self._draw_depth_sorted_world()
            self.model.combat_system.draw(self.screen)
            for number in self.model.damage_numbers:
                number.draw(self.screen)
            self._draw_ui()

        if self.model.stage_manager:
            self.model.stage_manager.draw_overlays(self.screen)

        if self.model.skill_tree_open:
            self.model.skill_tree_ui.draw(self.screen, self.model.player)

    def _draw_depth_sorted_world(self):
        drawables = []
        current_stage = self.model.stage_manager.current_stage

        for obstacle in current_stage.obstacles:
            drawables.append((obstacle.get_depth_y(), obstacle.draw))

        if self.model.enemy_manager:
            for enemy in self.model.enemy_manager.enemies:
                drawables.append((enemy.get_collision_rect().bottom, enemy.draw))

        drawables.append((self.model.player.get_collision_rect().bottom, self._draw_player))

        for _, draw in sorted(drawables, key=lambda item: item[0]):
            draw(self.screen)

    def _draw_player(self, surface):
        surface.blit(self.model.player.image, self.model.player.rect)

    def _draw_ui(self):
        if self.model.health_bar and self.model.player:
            self.model.health_bar.draw(
                self.screen,
                self.model.player.hp,
                self.model.player.max_hp
            )

        if self.model.xp_bar and self.model.player:
            self.model.xp_bar.draw(self.screen, self.model.player)

        self.model.stage_clear_message.draw(self.screen)

        if self.model.exit_message_timer > 0:
            self._draw_exit_message()

    def _draw_exit_message(self):
        text_surface = self.model.exit_message_font.render(
            self.model.exit_message,
            True,
            (255, 255, 255)
        )
        shadow_surface = self.model.exit_message_font.render(
            self.model.exit_message,
            True,
            (20, 20, 20)
        )
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT - 80))
        shadow_rect = shadow_surface.get_rect(center=(WIDTH // 2 + 2, HEIGHT - 78))

        self.screen.blit(shadow_surface, shadow_rect)
        self.screen.blit(text_surface, text_rect)
