import pygame

from settings import (
    ATTACK_DOUBLE_HIT_DAMAGE_MULTIPLIER,
    ATTACK_DOUBLE_HIT_DELAY,
    ATTACK_SLASH_RANGE_MULTIPLIER,
    ATTACK_SLASH_WIDTH_MULTIPLIER,
    ATTACK_WAVE_DAMAGE_MULTIPLIER,
    ATTACK_WAVE_HEIGHT,
    ATTACK_WAVE_RANGE,
    ATTACK_WAVE_SPEED,
    ATTACK_WAVE_WIDTH,
    PLAYER_ATTACK_RANGE,
    PLAYER_ATTACK_WIDTH,
    BOSS_STAR_REWARD,
)


class CombatSystem:
    def __init__(self):
        self.attack_visual_events = []
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
        self._queue_slash_visual(attack_rect, player.direction)
        self._spawn_drops(enemy_manager, loot_system, defeated_positions)
        on_damage_events()
        on_stage_clear()

        if hit_count > 0:
            self._trigger_attack_skill_effects(player, attack_rect)

    def update(self, dt, player, enemy_manager, loot_system, on_damage_events, on_stage_clear):
        if not enemy_manager:
            return

        self._update_pending_double_hits(dt, enemy_manager, loot_system, on_damage_events, on_stage_clear)
        self._update_energy_waves(dt, enemy_manager, loot_system, on_damage_events, on_stage_clear)

    def _trigger_attack_skill_effects(self, player, attack_rect):
        if player.has_skill("attack_wave"):
            wave_damage = max(1, int(player.attack_damage * ATTACK_WAVE_DAMAGE_MULTIPLIER))
            origin = attack_rect.midleft if player.direction == "left" else attack_rect.midright
            self.energy_waves.append(EnergyWave(origin, player.direction, wave_damage))

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
            self._queue_slash_visual(hit["rect"], hit["direction"], color=(255, 225, 120))
            self._spawn_drops(enemy_manager, loot_system, defeated_positions)
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
            self._spawn_drops(enemy_manager, loot_system, defeated_positions)
            on_damage_events()
            on_stage_clear()

        self.energy_waves = [wave for wave in self.energy_waves if wave.is_alive()]

    @staticmethod
    def _spawn_drops(enemy_manager, loot_system, defeated_positions):
        boss_positions = enemy_manager.consume_defeated_boss_positions()
        cave_boss_positions = enemy_manager.consume_defeated_cave_boss_positions()
        boss_positions_set = set(boss_positions + cave_boss_positions)
        regular_positions = [
            position for position in defeated_positions
            if position not in boss_positions_set
        ]
        loot_system.spawn_enemy_drops(regular_positions)
        loot_system.spawn_xp_orbs(boss_positions)
        loot_system.spawn_guaranteed_star_orbs(boss_positions, BOSS_STAR_REWARD)
        loot_system.spawn_boss_star(cave_boss_positions)

    def clear(self):
        self.attack_visual_events = []
        self.energy_waves = []
        self.pending_double_hits = []

    def consume_attack_visual_events(self):
        events = self.attack_visual_events
        self.attack_visual_events = []
        return events

    def _queue_slash_visual(self, attack_rect, direction, color=(255, 92, 50)):
        self.attack_visual_events.append({
            "type": "slash",
            "rect": attack_rect.copy(),
            "direction": direction,
            "color": color,
        })


class EnergyWave:
    def __init__(self, origin, direction, damage):
        self.position = pygame.Vector2(origin)
        self.start_x = self.position.x
        self.direction = direction
        self.damage = damage
        self.hit_enemy_ids = set()
        self.alive = True

    @property
    def rect(self):
        rect = pygame.Rect(0, 0, ATTACK_WAVE_WIDTH, ATTACK_WAVE_HEIGHT)
        rect.center = (int(self.position.x), int(self.position.y))
        return rect

    def update(self, dt):
        if not self.alive:
            return

        sign = -1 if self.direction == "left" else 1
        self.position.x += ATTACK_WAVE_SPEED * sign * dt

        if abs(self.position.x - self.start_x) >= ATTACK_WAVE_RANGE:
            self.alive = False

    def is_alive(self):
        return self.alive
