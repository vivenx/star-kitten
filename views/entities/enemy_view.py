import os
import random
import re

import pygame

from config import ENEMY_SIZE


class EnemyView:
    """Отображает обычных врагов, их анимации, снаряды и здоровье."""
    HEALTH_BAR_BACKGROUND = (60, 20, 20)
    HEALTH_BAR_FILL = (180, 40, 40)
    HEALTH_BAR_HEIGHT = 5
    HEALTH_BAR_OFFSET_Y = 8
    WALK_FRAME_TIME = 8 / 60
    DAMAGE_FRAME_TIME = 5 / 60
    ATTACK_FRAME_TIME = 5 / 60
    ACTION_DURATION = 0.25

    def __init__(self):
        self.sprites = {
            "skeleton": self._load_sprites("assets/images/forest/enemies/skeleton"),
            "cave_skeleton": self._load_sprites("assets/images/cave/enemies/skeleton"),
            "slime": self._load_sprites("assets/images/cave/enemies/slime"),
            "cave_slime_boss": self._load_flat_sprites(
                "assets/images/cave/boss/stages_boss",
                [
                    "boss_slime.png",
                    "boss_slime(1).png",
                    "boss_slime(2).png",
                    "boss_slime(3).png",
                    "boss_slime(4).png",
                ],
            ),
            **{
                f"mini_slime_{variant}": self._load_flat_sprites(
                    f"assets/images/cave/boss/minislimes/{variant}",
                    [
                        f"minislime{variant}.png",
                        f"minislime{variant}(1).png",
                        f"minislime{variant}(2).png",
                    ],
                )
                for variant in range(1, 4)
            },
        }
        self.animation_states = {}

    def update(self, dt, enemies):
        alive_enemy_ids = {id(enemy) for enemy in enemies}
        self.animation_states = {
            enemy_id: state
            for enemy_id, state in self.animation_states.items()
            if enemy_id in alive_enemy_ids
        }

        for enemy in enemies:
            self._update_enemy_animation(dt, enemy)

    def draw(self, surface, enemy):
        image = self._get_current_image(enemy)
        if image.get_size() != enemy.rect.size:
            image = pygame.transform.smoothscale(image, enemy.rect.size)
        surface.blit(image, enemy.rect)
        self._draw_health_bar(surface, enemy)

    def draw_projectiles(self, surface, enemy):
        for projectile in getattr(enemy, "projectiles", []):
            glow = pygame.Surface((46, 46), pygame.SRCALPHA)
            pygame.draw.circle(glow, (145, 55, 230, 65), (23, 23), 22)
            pygame.draw.circle(glow, (185, 75, 255, 210), (23, 23), 13)
            pygame.draw.circle(glow, (235, 180, 255, 255), (19, 19), 5)
            surface.blit(glow, glow.get_rect(center=projectile.rect.center))

    def _load_sprites(self, base_path):
        walk_right = self._load_animation(os.path.join(base_path, "right", "walk"))
        walk_left = self._load_animation(os.path.join(base_path, "left", "walk"))
        damage_right = self._load_animation(os.path.join(base_path, "right", "damage"))
        damage_left = self._load_animation(os.path.join(base_path, "left", "damage"))
        attack_right = self._load_animation(os.path.join(base_path, "right", "attack"))
        attack_left = self._load_animation(os.path.join(base_path, "left", "attack"))

        return {
            "walk": {
                "right": walk_right,
                "left": walk_left,
            },
            "damage": {
                "right": damage_right or walk_right[:1],
                "left": damage_left or walk_left[:1],
            },
            "attack": {
                "right": attack_right or walk_right[:1],
                "left": attack_left or walk_left[:1],
            },
        }

    def _load_animation(self, folder_path):
        files = [
            file_name
            for file_name in os.listdir(folder_path)
            if file_name.lower().endswith(".png")
        ]
        files.sort(key=lambda file_name: (
            self._get_frame_number(file_name)
            if self._get_frame_number(file_name) is not None
            else 0,
            file_name
        ))

        return [
            pygame.transform.scale(
                pygame.image.load(os.path.join(folder_path, file_name)).convert_alpha(),
                ENEMY_SIZE
            )
            for file_name in files
        ]

    @staticmethod
    def _load_flat_sprites(folder_path, names):
        frames = [
            pygame.image.load(os.path.join(folder_path, name)).convert_alpha()
            for name in names
        ]
        directional = {"right": frames, "left": frames}
        return {
            "walk": directional,
            "damage": directional,
            "attack": directional,
        }

    def _get_frame_number(self, file_name):
        match = re.search(r"\((\d+)\)|(\d+)", file_name)
        if not match:
            return None
        return int(match.group(1) or match.group(2))

    def _update_enemy_animation(self, dt, enemy):
        state = self._get_state(enemy)
        self._start_new_visual_action_if_needed(state, enemy)

        if state["action"]:
            self._update_action_animation(dt, state, enemy)
            return

        self._update_walk_animation(dt, state, enemy)

    def _get_state(self, enemy):
        enemy_id = id(enemy)
        if enemy_id not in self.animation_states:
            self.animation_states[enemy_id] = {
                "walk_frame": 0,
                "walk_timer": random.uniform(0, self.WALK_FRAME_TIME),
                "action": None,
                "action_frame": 0,
                "action_timer": 0.0,
                "action_elapsed": 0.0,
                "last_visual_action_id": -1,
            }
        return self.animation_states[enemy_id]

    def _start_new_visual_action_if_needed(self, state, enemy):
        if state["last_visual_action_id"] == enemy.visual_action_id:
            return

        state["last_visual_action_id"] = enemy.visual_action_id
        state["action"] = enemy.visual_action
        state["action_frame"] = 0
        state["action_timer"] = 0.0
        state["action_elapsed"] = 0.0

    def _update_action_animation(self, dt, state, enemy):
        state["action_elapsed"] += dt
        state["action_timer"] += dt

        frame_time = (
            self.DAMAGE_FRAME_TIME
            if state["action"] == "damage"
            else self.ATTACK_FRAME_TIME
        )
        sprites = self.sprites[getattr(enemy, "visual_type", "skeleton")]
        frames = sprites[state["action"]][enemy.direction]
        if state["action_timer"] >= frame_time:
            state["action_timer"] = 0.0
            state["action_frame"] = (state["action_frame"] + 1) % len(frames)

        if state["action_elapsed"] >= self.ACTION_DURATION:
            state["action"] = None
            state["action_frame"] = 0
            state["action_timer"] = 0.0
            state["action_elapsed"] = 0.0

    def _update_walk_animation(self, dt, state, enemy):
        if not enemy.is_moving:
            state["walk_frame"] = 0
            state["walk_timer"] = 0.0
            return

        state["walk_timer"] += dt
        sprites = self.sprites[getattr(enemy, "visual_type", "skeleton")]
        frames = sprites["walk"][enemy.direction]
        if state["walk_timer"] >= self.WALK_FRAME_TIME:
            state["walk_timer"] = 0.0
            state["walk_frame"] = (state["walk_frame"] + 1) % len(frames)

    def _get_current_image(self, enemy):
        state = self._get_state(enemy)
        sprites = self.sprites[getattr(enemy, "visual_type", "skeleton")]
        if getattr(enemy, "visual_type", None) == "cave_slime_boss":
            frames = sprites["walk"]["right"]
            return frames[min(enemy.summon_count, len(frames) - 1)]
        if state["action"]:
            frames = sprites[state["action"]][enemy.direction]
            return frames[state["action_frame"]]

        frames = sprites["walk"][enemy.direction]
        return frames[state["walk_frame"]]

    def _draw_health_bar(self, surface, enemy):
        if enemy.current_hp >= enemy.max_hp:
            return

        bar_width = enemy.rect.width
        x = enemy.rect.left
        y = enemy.rect.top - self.HEALTH_BAR_OFFSET_Y
        hp_percent = enemy.current_hp / enemy.max_hp

        pygame.draw.rect(
            surface,
            self.HEALTH_BAR_BACKGROUND,
            (x, y, bar_width, self.HEALTH_BAR_HEIGHT),
        )
        pygame.draw.rect(
            surface,
            self.HEALTH_BAR_FILL,
            (x, y, int(bar_width * hp_percent), self.HEALTH_BAR_HEIGHT),
        )
