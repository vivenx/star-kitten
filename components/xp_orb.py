import math

import pygame

from settings import (
    XP_ORB_COLOR,
    XP_ORB_GLOW_COLOR,
    XP_ORB_PICKUP_RADIUS,
    XP_ORB_RADIUS,
    XP_ORB_VALUE,
)


class XPOrb:
    def __init__(self, x, y, value=XP_ORB_VALUE):
        self.position = pygame.Vector2(x, y)
        self.value = value
        self.radius = XP_ORB_RADIUS
        self.rect = pygame.Rect(0, 0, XP_ORB_PICKUP_RADIUS * 2, XP_ORB_PICKUP_RADIUS * 2)
        self.rect.center = (int(self.position.x), int(self.position.y))
        self.animation_time = 0.0

    def update(self, dt):
        self.animation_time += dt

    def can_be_picked_up_by(self, player):
        return self.rect.colliderect(player.get_collision_rect())

    def draw(self, surface):
        pulse = (math.sin(self.animation_time * 5.0) + 1.0) * 0.5
        glow_radius = int(self.radius + 4 + pulse * 3)
        center = (int(self.position.x), int(self.position.y))

        pygame.draw.circle(surface, XP_ORB_GLOW_COLOR, center, glow_radius)
        pygame.draw.circle(surface, XP_ORB_COLOR, center, self.radius)
        pygame.draw.circle(surface, (230, 250, 255), center, max(2, self.radius // 3))
