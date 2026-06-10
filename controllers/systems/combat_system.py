import pygame

from views.effects.attack_effects import EnergyWaveEffect, SlashEffect
from settings import (
    ATTACK_DOUBLE_HIT_DAMAGE_MULTIPLIER,
    ATTACK_DOUBLE_HIT_DELAY,
    ATTACK_SLASH_RANGE_MULTIPLIER,
    ATTACK_SLASH_WIDTH_MULTIPLIER,
    ATTACK_WAVE_DAMAGE_MULTIPLIER,
    PLAYER_ATTACK_RANGE,
    PLAYER_ATTACK_WIDTH,
)


class CombatSystem:
    def __init__(self):
        self.attack_effects = []
        self.energy_waves = []
        self.pending_double_hits = []

    def handle_player_attack(
        self,
        mouse_pos,
        player,
        enemy_manager,
        loot_system,
        on_damage_events,
        on_stage_clear,
        is_transitioning,
    ):
        if not player or not enemy_manager or is_transitioning:
            return

        if not player.start_attack(mouse_pos):
            return

        attack_rect = self._get_player_attack_rect(player)
        defeated_positions, hit_count = enemy_manager.damage_enemies_with_result(
            attack_rect,
            player.attack_damage
        )
        self.attack_effects.append(SlashEffect(attack_rect, player.direction))
        loot_system.spawn_enemy_drops(defeated_positions)
        on_damage_events()
        on_stage_clear()

        if hit_count > 0:
            self._trigger_attack_skill_effects(player, attack_rect)

    def update(self, dt, player, enemy_manager, loot_system, on_damage_events, on_stage_clear):
        if not enemy_manager:
            return

        for effect in self.attack_effects:
            effect.update(dt)
        self.attack_effects = [effect for effect in self.attack_effects if effect.is_alive()]

        self._update_pending_double_hits(dt, enemy_manager, loot_system, on_damage_events, on_stage_clear)
        self._update_energy_waves(dt, enemy_manager, loot_system, on_damage_events, on_stage_clear)

    def _trigger_attack_skill_effects(self, player, attack_rect):
        if player.has_skill("attack_wave"):
            wave_damage = max(1, int(player.attack_damage * ATTACK_WAVE_DAMAGE_MULTIPLIER))
            origin = attack_rect.midleft if player.direction == "left" else attack_rect.midright
            self.energy_waves.append(EnergyWaveEffect(origin, player.direction, wave_damage))

        if player.has_skill("attack_double_hit"):
            double_hit_damage = max(1, int(player.attack_damage * ATTACK_DOUBLE_HIT_DAMAGE_MULTIPLIER))
            self.pending_double_hits.append({
                "timer": ATTACK_DOUBLE_HIT_DELAY,
                "rect": attack_rect.copy(),
                "direction": player.direction,
                "damage": double_hit_damage,
            })

    def _get_player_attack_rect(self, player):
        player_rect = player.get_collision_rect()
        attack_range = PLAYER_ATTACK_RANGE
        attack_height = PLAYER_ATTACK_WIDTH
        if player.has_skill("attack_slash"):
            attack_range = int(attack_range * ATTACK_SLASH_RANGE_MULTIPLIER)
            attack_height = int(attack_height * ATTACK_SLASH_WIDTH_MULTIPLIER)

        if player.direction == "left":
            return pygame.Rect(
                player_rect.centerx - attack_range,
                player_rect.centery - attack_height // 2,
                attack_range,
                attack_height
            )

        return pygame.Rect(
            player_rect.centerx,
            player_rect.centery - attack_height // 2,
            attack_range,
            attack_height
        )

    def _update_pending_double_hits(
        self,
        dt,
        enemy_manager,
        loot_system,
        on_damage_events,
        on_stage_clear,
    ):
        remaining_hits = []
        for hit in self.pending_double_hits:
            hit["timer"] -= dt
            if hit["timer"] > 0:
                remaining_hits.append(hit)
                continue

            defeated_positions, _ = enemy_manager.damage_enemies_with_result(hit["rect"], hit["damage"])
            self.attack_effects.append(SlashEffect(hit["rect"], hit["direction"], color=(255, 225, 120)))
            loot_system.spawn_enemy_drops(defeated_positions)
            on_damage_events()
            on_stage_clear()

        self.pending_double_hits = remaining_hits

    def _update_energy_waves(
        self,
        dt,
        enemy_manager,
        loot_system,
        on_damage_events,
        on_stage_clear,
    ):
        for wave in self.energy_waves:
            wave.update(dt)
            defeated_positions, _ = enemy_manager.damage_enemies_with_result(
                wave.rect,
                wave.damage,
                wave.hit_enemy_ids
            )
            loot_system.spawn_enemy_drops(defeated_positions)
            on_damage_events()
            on_stage_clear()

        self.energy_waves = [wave for wave in self.energy_waves if wave.is_alive()]

    def clear(self):
        self.attack_effects = []
        self.energy_waves = []
        self.pending_double_hits = []

    def draw(self, surface):
        for effect in self.attack_effects:
            effect.draw(surface)
        for wave in self.energy_waves:
            wave.draw(surface)
