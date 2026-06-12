import os

import pygame

from settings import (
    BOSS_APPEARANCE_FRAME_TIME,
    BOSS_ATTACK_ANIMATION_DURATION,
    BOSS_SIZE,
)


class BossView:
    APPEARANCE_FRAME_TIME = BOSS_APPEARANCE_FRAME_TIME

    def __init__(self):
        idle_images = self._load_images("assets/images/forest/boss/start")
        attack_images = self._load_images(
            "assets/images/forest/boss/attack",
            "attack_boss",
        )
        self.idle_frames, self.attack_frames = self._scale_boss_frames(
            idle_images,
            attack_images,
        )
        self.spike_frames = {
            variant: self._load_spikes(variant)
            for variant in (1, 2)
        }
        self.boss_states = {}

    def update(self, dt, bosses):
        alive_ids = {id(boss) for boss in bosses if getattr(boss, "is_boss", False)}
        self.boss_states = {
            boss_id: state
            for boss_id, state in self.boss_states.items()
            if boss_id in alive_ids
        }
        for boss in bosses:
            if not getattr(boss, "is_boss", False):
                continue
            state = self._get_state(boss)
            state["appearance_elapsed"] += dt

    def draw(self, surface, boss):
        state = self._get_state(boss)
        if boss.attack_visual_timer > 0:
            elapsed = BOSS_ATTACK_ANIMATION_DURATION - boss.attack_visual_timer
            frame_index = min(
                len(self.attack_frames) - 1,
                int(elapsed / BOSS_ATTACK_ANIMATION_DURATION * len(self.attack_frames)),
            )
            frame = self.attack_frames[frame_index]
        else:
            frame_index = min(
                len(self.idle_frames) - 1,
                int(state["appearance_elapsed"] / self.APPEARANCE_FRAME_TIME),
            )
            frame = self.idle_frames[frame_index]

        frame_rect = frame.get_rect(midbottom=boss.rect.midbottom)
        surface.blit(frame, frame_rect)
        self._draw_health_bar(surface, boss)

    def draw_hazards(self, surface, boss):
        for spike in boss.spikes:
            image = self.spike_frames[spike.variant][spike.frame_index]
            image_rect = image.get_rect(midbottom=spike.rect.midbottom)
            surface.blit(image, image_rect)
        for orb in boss.orbs:
            center = orb.rect.center
            pygame.draw.circle(surface, (95, 35, 145), center, orb.rect.width // 2 + 6)
            pygame.draw.circle(surface, (184, 72, 255), center, orb.rect.width // 2)
            pygame.draw.circle(surface, (235, 185, 255), center, max(3, orb.rect.width // 6))

    def _get_state(self, boss):
        return self.boss_states.setdefault(id(boss), {"appearance_elapsed": 0.0})

    def _load_images(self, folder, prefix=None):
        names = sorted(
            name for name in os.listdir(folder)
            if name.endswith(".png") and (prefix is None or name.startswith(prefix))
        )
        return [
            pygame.image.load(os.path.join(folder, name)).convert_alpha()
            for name in names
        ]

    @staticmethod
    def _scale_boss_frames(idle_images, attack_images):
        all_images = idle_images + attack_images
        max_width = max(image.get_width() for image in all_images)
        max_height = max(image.get_height() for image in all_images)
        scale = min(BOSS_SIZE[0] / max_width, BOSS_SIZE[1] / max_height)

        def scale_frames(images):
            return [
                pygame.transform.smoothscale(
                    image,
                    (
                        round(image.get_width() * scale),
                        round(image.get_height() * scale),
                    ),
                )
                for image in images
            ]

        return scale_frames(idle_images), scale_frames(attack_images)

    def _load_spikes(self, variant):
        images = [
            pygame.image.load(
                f"assets/images/forest/boss/attack/thorn_{variant}_stage_{stage}.png"
            ).convert_alpha()
            for stage in range(1, 4)
        ]
        max_width = max(image.get_width() for image in images)
        max_height = max(image.get_height() for image in images)
        scale = min(70 / max_width, 100 / max_height)
        return [
            pygame.transform.smoothscale(
                image,
                (
                    round(image.get_width() * scale),
                    round(image.get_height() * scale),
                ),
            )
            for image in images
        ]

    @staticmethod
    def _draw_health_bar(surface, boss):
        width, height = 500, 18
        rect = pygame.Rect(0, 0, width, height)
        rect.midtop = (surface.get_width() // 2, 25)
        pygame.draw.rect(surface, (35, 12, 45), rect, border_radius=5)
        fill = rect.copy()
        fill.width = int(width * boss.current_hp / boss.max_hp)
        pygame.draw.rect(surface, (145, 38, 180), fill, border_radius=5)
        pygame.draw.rect(surface, (225, 190, 240), rect, 2, border_radius=5)
