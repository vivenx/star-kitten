import math

import pygame

from settings import (
    STAR_ORB_GLOW_COLOR,
    STAR_ORB_IMAGE_PATH,
    STAR_ORB_PICKUP_RADIUS,
    STAR_ORB_SIZE,
    STAR_ORB_VALUE,
)


class StarOrb:
    _image = None

    def __init__(self, x, y, value=STAR_ORB_VALUE):
        self.position = pygame.Vector2(x, y)
        self.value = value
        self.size = STAR_ORB_SIZE
        self.rect = pygame.Rect(0, 0, STAR_ORB_PICKUP_RADIUS * 2, STAR_ORB_PICKUP_RADIUS * 2)
        self.rect.center = (int(self.position.x), int(self.position.y))
        self.animation_time = 0.0

        if StarOrb._image is None:
            source = pygame.image.load(STAR_ORB_IMAGE_PATH).convert_alpha()
            StarOrb._image = pygame.transform.smoothscale(source, (self.size, self.size))

    def update(self, dt):
        self.animation_time += dt

    def can_be_picked_up_by(self, player):
        return self.rect.colliderect(player.get_collision_rect())

    def draw(self, surface):
        pulse = (math.sin(self.animation_time * 6.0) + 1.0) * 0.5
        glow_radius = int(self.size * 0.52 + pulse * 5)
        center = (int(self.position.x), int(self.position.y))

        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surface,
            (*STAR_ORB_GLOW_COLOR, 90),
            (glow_radius, glow_radius),
            glow_radius,
        )
        surface.blit(glow_surface, glow_surface.get_rect(center=center))

        image_rect = StarOrb._image.get_rect(center=center)
        surface.blit(StarOrb._image, image_rect)
