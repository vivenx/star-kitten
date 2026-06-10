import pygame

from settings import (
    STAR_ORB_PICKUP_RADIUS,
    STAR_ORB_SIZE,
    STAR_ORB_VALUE,
)


class StarOrb:
    def __init__(self, x, y, value=STAR_ORB_VALUE):
        self.position = pygame.Vector2(x, y)
        self.value = value
        self.size = STAR_ORB_SIZE
        self.rect = pygame.Rect(0, 0, STAR_ORB_PICKUP_RADIUS * 2, STAR_ORB_PICKUP_RADIUS * 2)
        self.rect.center = (int(self.position.x), int(self.position.y))

    def update(self, dt):
        pass

    def can_be_picked_up_by(self, player):
        return self.rect.colliderect(player.get_collision_rect())
