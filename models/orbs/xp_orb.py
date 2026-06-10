import pygame

from settings import (
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

    def update(self, dt):
        pass

    def can_be_picked_up_by(self, player):
        return self.rect.colliderect(player.get_collision_rect())
