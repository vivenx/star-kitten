import os
import random
import re

import pygame

from settings import ENEMY_SIZE


class EnemyView:
    HEALTH_BAR_BACKGROUND = (60, 20, 20)
    HEALTH_BAR_FILL = (180, 40, 40)
    HEALTH_BAR_HEIGHT = 5
    HEALTH_BAR_OFFSET_Y = 8
    WALK_FRAME_TIME = 8 / 60
    DAMAGE_FRAME_TIME = 5 / 60
    ATTACK_FRAME_TIME = 5 / 60
    ACTION_DURATION = 0.25

    def __init__(self):
        self.sprites = self._load_sprites()
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
        surface.blit(image, enemy.rect)
        self._draw_health_bar(surface, enemy)

    def _load_sprites(self):
        base_path = "assets/images/forest/enemies/skeleton"
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
        frames = self.sprites[state["action"]][enemy.direction]
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
        frames = self.sprites["walk"][enemy.direction]
        if state["walk_timer"] >= self.WALK_FRAME_TIME:
            state["walk_timer"] = 0.0
            state["walk_frame"] = (state["walk_frame"] + 1) % len(frames)

    def _get_current_image(self, enemy):
        state = self._get_state(enemy)
        if state["action"]:
            frames = self.sprites[state["action"]][enemy.direction]
            return frames[state["action_frame"]]

        frames = self.sprites["walk"][enemy.direction]
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
