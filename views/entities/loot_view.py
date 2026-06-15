import math

import pygame

from settings import (
    STAR_ORB_GLOW_COLOR,
    STAR_ORB_IMAGE_PATH,
    FINAL_STAR_IMAGE_PATH,
    XP_ORB_COLOR,
    XP_ORB_GLOW_COLOR,
)


class LootView:
    def __init__(self):
        self.star_image = None
        self.final_star_image = None
        self.orb_animation_times = {}

    def update(self, dt, loot_system):
        orbs = [*loot_system.xp_orbs, *loot_system.star_orbs]
        alive_orb_ids = {id(orb) for orb in orbs}
        self.orb_animation_times = {
            orb_id: animation_time
            for orb_id, animation_time in self.orb_animation_times.items()
            if orb_id in alive_orb_ids
        }
        for orb in orbs:
            self.orb_animation_times[id(orb)] = self.orb_animation_times.get(id(orb), 0.0) + dt

    def draw(self, surface, loot_system):
        for orb in loot_system.xp_orbs:
            self._draw_xp_orb(surface, orb)
        for orb in loot_system.star_orbs:
            self._draw_star_orb(surface, orb)

    def _draw_xp_orb(self, surface, orb):
        animation_time = self.orb_animation_times.get(id(orb), 0.0)
        pulse = (math.sin(animation_time * 5.0) + 1.0) * 0.5
        glow_radius = int(orb.radius + 4 + pulse * 3)
        center = (int(orb.position.x), int(orb.position.y))

        pygame.draw.circle(surface, XP_ORB_GLOW_COLOR, center, glow_radius)
        pygame.draw.circle(surface, XP_ORB_COLOR, center, orb.radius)
        pygame.draw.circle(surface, (230, 250, 255), center, max(2, orb.radius // 3))

    def _draw_star_orb(self, surface, orb):
        if orb.image_path == FINAL_STAR_IMAGE_PATH:
            if self.final_star_image is None:
                source = pygame.image.load(FINAL_STAR_IMAGE_PATH).convert_alpha()
                self.final_star_image = pygame.transform.smoothscale(source, (orb.size, orb.size))
            star_image = self.final_star_image
        else:
            if self.star_image is None:
                source = pygame.image.load(STAR_ORB_IMAGE_PATH).convert_alpha()
                self.star_image = pygame.transform.smoothscale(source, (orb.size, orb.size))
            star_image = self.star_image

        animation_time = self.orb_animation_times.get(id(orb), 0.0)
        pulse = (math.sin(animation_time * 6.0) + 1.0) * 0.5
        glow_radius = int(orb.size * 0.52 + pulse * 5)
        center = (int(orb.position.x), int(orb.position.y))

        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surface,
            (*STAR_ORB_GLOW_COLOR, 90),
            (glow_radius, glow_radius),
            glow_radius,
        )
        surface.blit(glow_surface, glow_surface.get_rect(center=center))

        image_rect = star_image.get_rect(center=center)
        surface.blit(star_image, image_rect)
