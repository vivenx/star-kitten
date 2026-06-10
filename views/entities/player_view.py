import os
import re

import pygame


class PlayerView:
    WALK_FRAME_TIME = 5 / 60
    ATTACK_FRAME_TIME = 4 / 60
    DAMAGE_FRAME_TIME = 5 / 60

    def __init__(self):
        self.default_image = pygame.image.load(
            "assets/images/sprites_player/default.png"
        ).convert_alpha()
        sprite_size = self.default_image.get_size()
        base_path = "assets/images/sprites_player"
        self.sprites = {
            "walk": {
                "right": self._load_animation(os.path.join(base_path, "right", "walk"), sprite_size),
                "left": self._load_animation(os.path.join(base_path, "left", "walk"), sprite_size),
            },
            "attack": {
                "right": self._load_animation(os.path.join(base_path, "right", "attack"), sprite_size),
                "left": self._load_animation(os.path.join(base_path, "left", "attack"), sprite_size),
            },
            "damage": {
                "right": self._load_animation(os.path.join(base_path, "right", "damage"), sprite_size),
                "left": self._load_animation(os.path.join(base_path, "left", "damage"), sprite_size),
            },
        }
        self.sprites["damage"]["right"] = self.sprites["damage"]["right"] or [self.default_image]
        self.sprites["damage"]["left"] = self.sprites["damage"]["left"] or [self.default_image]
        self.state = {
            "walk_frame": 0,
            "walk_timer": 0.0,
            "action": None,
            "action_frame": 0,
            "action_timer": 0.0,
            "last_visual_action_id": -1,
        }

    def update(self, dt, player):
        self._start_new_visual_action_if_needed(player)
        if self.state["action"]:
            self._update_action(dt, player)
            return
        self._update_walk(dt, player)

    def draw(self, surface, player):
        surface.blit(self._get_current_image(player), player.rect)

    def _load_animation(self, folder_path, size):
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
                size,
            )
            for file_name in files
        ]

    def _get_frame_number(self, file_name):
        match = re.search(r"\((\d+)\)|(\d+)", file_name)
        if not match:
            return None
        return int(match.group(1) or match.group(2))

    def _start_new_visual_action_if_needed(self, player):
        if self.state["last_visual_action_id"] == player.visual_action_id:
            return
        self.state["last_visual_action_id"] = player.visual_action_id
        self.state["action"] = player.visual_action
        self.state["action_frame"] = 0
        self.state["action_timer"] = 0.0

    def _update_action(self, dt, player):
        action = self.state["action"]
        frame_time = self.DAMAGE_FRAME_TIME if action == "damage" else self.ATTACK_FRAME_TIME
        frames = self.sprites[action][player.direction]
        self.state["action_timer"] += dt
        if self.state["action_timer"] >= frame_time:
            self.state["action_timer"] = 0.0
            self.state["action_frame"] += 1
            if self.state["action_frame"] >= len(frames):
                self.state["action"] = None
                self.state["action_frame"] = 0

    def _update_walk(self, dt, player):
        if not player.is_moving:
            self.state["walk_frame"] = 0
            self.state["walk_timer"] = 0.0
            return

        frames = self.sprites["walk"][player.direction]
        self.state["walk_timer"] += dt
        if self.state["walk_timer"] >= self.WALK_FRAME_TIME:
            self.state["walk_timer"] = 0.0
            self.state["walk_frame"] = (self.state["walk_frame"] + 1) % len(frames)

    def _get_current_image(self, player):
        if self.state["action"]:
            frames = self.sprites[self.state["action"]][player.direction]
            return frames[self.state["action_frame"]]
        if player.is_moving:
            frames = self.sprites["walk"][player.direction]
            return frames[self.state["walk_frame"]]
        return self.default_image
