import math
import random

from config import (
    ENEMY_COLLISION_HEIGHT_RATIO,
    ENEMY_COLLISION_WIDTH_RATIO,
    ENEMY_COUNT_PER_ARENA,
    ENEMY_MAX_COUNT,
    ENEMY_MIN_DISTANCE_FROM_PLAYER_SPAWN,
    ENEMY_NEXT_WAVE_THRESHOLD,
    ENEMY_SIZE,
    ENEMY_SPAWN_PADDING,
    ENEMY_WAVE_COUNT,
    ENEMY_WAVE_SIZE,
)
from controllers.systems.boss_behavior_system import BossBehaviorSystem
from controllers.systems.cave_slime_boss_behavior_system import CaveSlimeBossBehaviorSystem
from controllers.systems.enemy_behavior_system import EnemyBehaviorSystem
from controllers.systems.slime_behavior_system import SlimeBehaviorSystem
from models.boss import Boss
from models.cave_slime_boss import CaveSlimeBoss
from models.enemy import Enemy
from models.pathfinder import Pathfinder
from models.slime import Slime


class EnemyManager:
    """Управляет созданием, поведением, волнами и уроном всех врагов этапа."""

    def __init__(self, stage, player, difficulty_multiplier=1.0, arena_index=0):
        self.max_enemies = ENEMY_MAX_COUNT
        self.behavior_systems = {
            "melee_chase": EnemyBehaviorSystem(),
            "forest_boss": BossBehaviorSystem(),
            "slime_ranged": SlimeBehaviorSystem(),
            "cave_slime_boss": CaveSlimeBossBehaviorSystem(),
        }
        self._configure_stage(stage, player, difficulty_multiplier, arena_index)

    def reset_stage(self, stage, player, difficulty_multiplier=1.0, arena_index=0):
        self._configure_stage(stage, player, difficulty_multiplier, arena_index)

    def _configure_stage(self, stage, player, difficulty_multiplier, arena_index):
        self.stage = stage
        self.player = player
        self.difficulty_multiplier = difficulty_multiplier
        self.arena_index = arena_index
        self.enemies = []
        self.pathfinder = self._create_pathfinder(stage)
        self.is_boss_stage = stage.boss_type is not None

        self.current_wave_index = -1
        self.spawned_enemies = 0
        self.next_wave_threshold = ENEMY_NEXT_WAVE_THRESHOLD
        self.wave_count = 1 if self.is_boss_stage else ENEMY_WAVE_COUNT
        self.wave_size = (
            1
            if self.is_boss_stage
            else int(ENEMY_WAVE_SIZE + arena_index * ENEMY_COUNT_PER_ARENA)
        )

        self.damage_events = []
        self.defeated_boss_positions = []
        self.defeated_cave_boss_positions = []
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
                self.damage_events.append({
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
        if ignored_enemy_ids is None:
            ignored_enemy_ids = set()
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
            position = enemy.get_collision_rect().center
            died = enemy.take_damage(damage)
            self.damage_events.append({
                "amount": damage,
                "position": position,
                "target": "enemy",
            })
            if not died:
                continue

            defeated_positions.append(position)
            if getattr(enemy, "is_boss", False):
                positions = (
                    self.defeated_cave_boss_positions
                    if isinstance(enemy, CaveSlimeBoss)
                    else self.defeated_boss_positions
                )
                positions.append(position)

        self.enemies = [enemy for enemy in self.enemies if enemy.is_alive()]
        return defeated_positions, hit_count

    def consume_defeated_boss_positions(self):
        return self._consume_events("defeated_boss_positions")

    def consume_defeated_cave_boss_positions(self):
        return self._consume_events("defeated_cave_boss_positions")

    def consume_damage_number_events(self):
        return self._consume_events("damage_events")

    def _consume_events(self, attribute):
        values = getattr(self, attribute)
        setattr(self, attribute, [])
        return values

    def is_stage_cleared(self):
        return self.current_wave_index >= self.wave_count - 1 and not self.has_alive_enemies()

    def spawn_wave(self):
        if self.current_wave_index >= self.wave_count - 1:
            return
        self.current_wave_index += 1
        wave_index = self.current_wave_index
        spawned_count = 0
        while spawned_count < self.wave_size and len(self.enemies) < self.max_enemies:
            enemy = self.spawn_enemy(wave_index)
            if enemy is None:
                break
            spawned_count += 1

    def spawn_enemy(self, wave_index):
        if self.is_boss_stage:
            boss_class = CaveSlimeBoss if self.stage.boss_type == "cave" else Boss
            enemy = boss_class(self.stage.play_area, self.difficulty_multiplier)
            enemy.wave_index = wave_index
        else:
            enemy = self._create_regular_enemy(wave_index)

        if enemy is not None:
            self.enemies.append(enemy)
            self.spawned_enemies += 1
        return enemy

    def _create_regular_enemy(self, wave_index, max_attempts=80):
        for _ in range(max_attempts):
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
                return enemy
        return None

    def _get_border_spawn_position(self):
        play_area = self.stage.play_area
        side = random.choice(("top", "right", "bottom", "left"))
        if side == "top":
            return (
                random.randint(play_area.left, play_area.right - ENEMY_SIZE[0]),
                play_area.top + ENEMY_SPAWN_PADDING,
            )
        if side == "right":
            return (
                play_area.right - ENEMY_SIZE[0] - ENEMY_SPAWN_PADDING,
                random.randint(play_area.top, play_area.bottom - ENEMY_SIZE[1]),
            )
        if side == "bottom":
            return (
                random.randint(play_area.left, play_area.right - ENEMY_SIZE[0]),
                play_area.bottom - ENEMY_SIZE[1] - ENEMY_SPAWN_PADDING,
            )
        return (
            play_area.left + ENEMY_SPAWN_PADDING,
            random.randint(play_area.top, play_area.bottom - ENEMY_SIZE[1]),
        )

    def _can_spawn(self, enemy):
        enemy_rect = enemy.get_collision_rect()
        if not self.stage.play_area.contains(enemy.rect):
            return False
        if enemy_rect.colliderect(self.player.get_collision_rect()):
            return False

        spawn_distance = enemy.position.distance_to(self.stage.player_spawn)
        if spawn_distance < ENEMY_MIN_DISTANCE_FROM_PLAYER_SPAWN:
            return False
        if any(enemy_rect.colliderect(rect) for rect in self._get_blocking_rects()):
            return False
        if any(
            enemy_rect.colliderect(other_enemy.get_collision_rect())
            for other_enemy in self.enemies
        ):
            return False
        return True

    def _should_spawn_next_wave(self):
        if self.current_wave_index >= self.wave_count - 1:
            return False
        alive = sum(
            1
            for enemy in self.enemies
            if getattr(enemy, "wave_index", -1) == self.current_wave_index
        )
        defeated = self.wave_size - alive
        required = math.ceil(self.wave_size * self.next_wave_threshold)
        return defeated >= required

    def _get_blocking_rects(self):
        return [
            obstacle.rect
            for obstacle in self.stage.obstacles
            if obstacle.is_solid or obstacle.deals_damage()
        ]

    @staticmethod
    def _create_pathfinder(stage):
        agent_size = (
            int(ENEMY_SIZE[0] * ENEMY_COLLISION_WIDTH_RATIO),
            int(ENEMY_SIZE[1] * ENEMY_COLLISION_HEIGHT_RATIO),
        )
        return Pathfinder(stage, agent_size=agent_size)
