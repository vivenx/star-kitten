import random
import math

from models.enemy import Enemy
from models.boss import Boss
from models.slime import Slime
from models.cave_slime_boss import CaveSlimeBoss
from models.pathfinder import Pathfinder
from controllers.systems.boss_behavior_system import BossBehaviorSystem
from controllers.systems.enemy_behavior_system import EnemyBehaviorSystem
from controllers.systems.slime_behavior_system import SlimeBehaviorSystem
from controllers.systems.cave_slime_boss_behavior_system import CaveSlimeBossBehaviorSystem
from settings import (
    ENEMY_MAX_COUNT,
    ENEMY_COLLISION_HEIGHT_RATIO,
    ENEMY_COLLISION_WIDTH_RATIO,
    ENEMY_SIZE,
    ENEMY_NEXT_WAVE_THRESHOLD,
    ENEMY_SPAWN_PADDING,
    ENEMY_MIN_DISTANCE_FROM_PLAYER_SPAWN,
    ENEMY_WAVE_COUNT,
    ENEMY_WAVE_SIZE,
    ENEMY_COUNT_PER_ARENA,
)


class EnemyManager:
    def __init__(self, stage, player, difficulty_multiplier=1.0, arena_index=0):
        self.stage = stage
        self.player = player
        self.difficulty_multiplier = difficulty_multiplier
        self.arena_index = arena_index
        self.enemies = []
        self.pathfinder = self._create_pathfinder(stage)
        self.max_enemies = ENEMY_MAX_COUNT
        self.wave_size = self._get_scaled_wave_size()
        self.wave_count = ENEMY_WAVE_COUNT
        self.next_wave_threshold = ENEMY_NEXT_WAVE_THRESHOLD
        self.current_wave_index = -1
        self.spawned_enemies = 0
        self.damage_number_events = []
        self.defeated_boss_positions = []
        self.defeated_cave_boss_positions = []
        self.behavior_systems = {
            "melee_chase": EnemyBehaviorSystem(),
            "forest_boss": BossBehaviorSystem(),
            "slime_ranged": SlimeBehaviorSystem(),
            "cave_slime_boss": CaveSlimeBossBehaviorSystem(),
        }

        self.is_boss_stage = stage.boss_type is not None
        if self.is_boss_stage:
            self.wave_count = 1
            self.wave_size = 1

        self.spawn_wave()

    def reset_stage(self, stage, player, difficulty_multiplier=1.0, arena_index=0):
        self.stage = stage
        self.player = player
        self.difficulty_multiplier = difficulty_multiplier
        self.arena_index = arena_index
        self.enemies = []
        self.pathfinder = self._create_pathfinder(stage)
        self.wave_size = self._get_scaled_wave_size()
        self.current_wave_index = -1
        self.spawned_enemies = 0
        self.damage_number_events = []
        self.defeated_boss_positions = []
        self.defeated_cave_boss_positions = []

        self.is_boss_stage = stage.boss_type is not None
        self.wave_count = 1 if self.is_boss_stage else ENEMY_WAVE_COUNT
        self.wave_size = 1 if self.is_boss_stage else self._get_scaled_wave_size()

        self.spawn_wave()

    def update(self, dt):
        player_died = False
        solid_rects = self._get_blocking_rects()

        for enemy in self.enemies:
            hp_before = self.player.hp
            behavior_system = self.behavior_systems[enemy.behavior_type]
            died = behavior_system.update(
                enemy,
                dt,
                self.player,
                self.pathfinder,
                solid_rects,
                self.enemies,
                self.stage.play_area,
            )
            player_died = died or player_died
            damage_dealt = hp_before - self.player.hp
            if damage_dealt > 0:
                self.damage_number_events.append({
                    "amount": damage_dealt,
                    "position": self.player.get_collision_rect().center,
                    "target": "player",
                })

        self.enemies = [enemy for enemy in self.enemies if enemy.is_alive()]
        if self._should_spawn_next_wave():
            self.spawn_wave()

        return player_died

    def has_alive_enemies(self):
        return any(enemy.is_alive() for enemy in self.enemies)

    def damage_enemies_with_result(self, attack_rect, damage, ignored_enemy_ids=None):
        ignored_enemy_ids = ignored_enemy_ids or set()
        defeated_positions = []
        hit_count = 0

        for enemy in self.enemies:
            enemy_id = id(enemy)
            if enemy_id in ignored_enemy_ids:
                continue
            if not enemy.is_alive() or not attack_rect.colliderect(enemy.get_collision_rect()):
                continue

            hit_count += 1
            ignored_enemy_ids.add(enemy_id)
            hit_position = enemy.get_collision_rect().center
            died = enemy.take_damage(damage)
            self.damage_number_events.append({
                "amount": damage,
                "position": hit_position,
                "target": "enemy",
            })
            if died:
                defeated_positions.append(hit_position)
                if getattr(enemy, "is_boss", False):
                    if isinstance(enemy, CaveSlimeBoss):
                        self.defeated_cave_boss_positions.append(hit_position)
                    else:
                        self.defeated_boss_positions.append(hit_position)

        self.enemies = [enemy for enemy in self.enemies if enemy.is_alive()]
        return defeated_positions, hit_count

    def consume_defeated_boss_positions(self):
        positions = self.defeated_boss_positions
        self.defeated_boss_positions = []
        return positions

    def consume_defeated_cave_boss_positions(self):
        positions = self.defeated_cave_boss_positions
        self.defeated_cave_boss_positions = []
        return positions

    def consume_damage_number_events(self):
        events = self.damage_number_events
        self.damage_number_events = []
        return events

    def is_stage_cleared(self):
        return self.current_wave_index >= self.wave_count - 1 and not self.has_alive_enemies()

    def spawn_wave(self):
        if self.current_wave_index >= self.wave_count - 1:
            return

        self.current_wave_index += 1
        spawned_count = 0

        while spawned_count < self.wave_size and len(self.enemies) < self.max_enemies:
            enemy = self.spawn_enemy(self.current_wave_index)
            if enemy is None:
                break
            spawned_count += 1

    def spawn_enemy(self, wave_index):
        if self.is_boss_stage:
            boss_class = CaveSlimeBoss if self.stage.boss_type == "cave" else Boss
            boss = boss_class(self.stage.play_area, self.difficulty_multiplier)
            boss.wave_index = wave_index
            self.enemies.append(boss)
            self.spawned_enemies += 1
            return boss

        for _ in range(80):
            x, y = self._get_border_spawn_position()
            enemy_class = (
                random.choice((Enemy, Slime))
                if self.stage.biome == "cave"
                else Enemy
            )
            enemy = enemy_class(x, y, self.difficulty_multiplier)
            if self.stage.biome == "cave" and enemy_class is Enemy:
                enemy.visual_type = "cave_skeleton"

            if self._can_spawn(enemy):
                enemy.wave_index = wave_index
                self.enemies.append(enemy)
                self.spawned_enemies += 1
                return enemy

        return None

    def _get_border_spawn_position(self):
        play_area = self.stage.play_area
        side = random.choice(("top", "right", "bottom", "left"))

        if side == "top":
            x = random.randint(play_area.left, play_area.right - ENEMY_SIZE[0])
            y = play_area.top + ENEMY_SPAWN_PADDING
        elif side == "right":
            x = play_area.right - ENEMY_SIZE[0] - ENEMY_SPAWN_PADDING
            y = random.randint(play_area.top, play_area.bottom - ENEMY_SIZE[1])
        elif side == "bottom":
            x = random.randint(play_area.left, play_area.right - ENEMY_SIZE[0])
            y = play_area.bottom - ENEMY_SIZE[1] - ENEMY_SPAWN_PADDING
        else:
            x = play_area.left + ENEMY_SPAWN_PADDING
            y = random.randint(play_area.top, play_area.bottom - ENEMY_SIZE[1])

        return x, y

    def _can_spawn(self, enemy):
        enemy_rect = enemy.get_collision_rect()

        if not self.stage.play_area.contains(enemy.rect):
            return False

        if enemy_rect.colliderect(self.player.get_collision_rect()):
            return False

        spawn_pos = self.stage.player_spawn
        spawn_distance = enemy.position.distance_to(spawn_pos)
        if spawn_distance < ENEMY_MIN_DISTANCE_FROM_PLAYER_SPAWN:
            return False

        for rect in self._get_blocking_rects():
            if enemy_rect.colliderect(rect):
                return False

        for other_enemy in self.enemies:
            if enemy_rect.colliderect(other_enemy.get_collision_rect()):
                return False

        return True

    def _should_spawn_next_wave(self):
        if self.current_wave_index >= self.wave_count - 1:
            return False

        alive_from_current_wave = sum(
            1
            for enemy in self.enemies
            if getattr(enemy, "wave_index", -1) == self.current_wave_index
        )
        defeated_from_current_wave = self.wave_size - alive_from_current_wave
        required_defeated = math.ceil(self.wave_size * self.next_wave_threshold)

        return defeated_from_current_wave >= required_defeated

    def _get_blocking_rects(self):
        return [
            obstacle.rect
            for obstacle in self.stage.obstacles
            if obstacle.is_solid or obstacle.deals_damage()
        ]

    def _create_pathfinder(self, stage):
        agent_size = (
            int(ENEMY_SIZE[0] * ENEMY_COLLISION_WIDTH_RATIO),
            int(ENEMY_SIZE[1] * ENEMY_COLLISION_HEIGHT_RATIO)
        )
        return Pathfinder(stage, agent_size=agent_size)

    def _get_scaled_wave_size(self):
        return int(ENEMY_WAVE_SIZE + self.arena_index * ENEMY_COUNT_PER_ARENA)
