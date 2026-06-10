import unittest

import pygame

from controllers.systems.player_collision_system import PlayerCollisionSystem
from models.stage import Obstacle


class DummyPlayer:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = image.get_rect(topleft=(x, y))
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.collision_height_ratio = 0.5

    def get_collision_rect(self):
        collision_height = int(self.rect.height * self.collision_height_ratio)
        return pygame.Rect(
            self.rect.left,
            self.rect.bottom - collision_height,
            self.rect.width,
            collision_height
        )


class PlayerCollisionSystemTest(unittest.TestCase):
    def test_obstacle_collision_uses_mask_transparency(self):
        obstacle_image = pygame.Surface((20, 20), pygame.SRCALPHA)
        obstacle_image.fill((0, 0, 0, 0))
        pygame.draw.rect(obstacle_image, (255, 255, 255, 255), pygame.Rect(10, 0, 10, 20))

        obstacle = Obstacle(
            0,
            0,
            ("stone", 1, (20, 20), True, 0, 0),
            image=obstacle_image
        )
        collision_system = PlayerCollisionSystem()
        test_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
        test_surface.fill((255, 255, 255, 255))
        test_mask = pygame.mask.from_surface(test_surface)

        transparent_overlap = pygame.Rect(-10, 0, 20, 20)
        opaque_overlap = pygame.Rect(0, 0, 20, 20)

        self.assertFalse(
            collision_system._collides_with_obstacles(
                transparent_overlap,
                test_mask,
                [obstacle]
            )
        )
        self.assertTrue(
            collision_system._collides_with_obstacles(
                opaque_overlap,
                test_mask,
                [obstacle]
            )
        )

    def test_player_can_move_out_of_partial_obstacle_overlap(self):
        obstacle_image = pygame.Surface((10, 10), pygame.SRCALPHA)
        obstacle_image.fill((255, 255, 255, 255))
        obstacle = Obstacle(
            10,
            10,
            ("stone", 1, (10, 10), True, 0, 0),
            image=obstacle_image
        )

        player_image = pygame.Surface((20, 20), pygame.SRCALPHA)
        player_image.fill((255, 255, 255, 255))
        player = DummyPlayer(0, 0, player_image)
        player.velocity.x = -5

        PlayerCollisionSystem()._move_player_axis(
            player,
            [obstacle],
            dt=1,
            speed_multiplier=1,
            axis="x"
        )

        self.assertEqual(player.position.x, -5)
        self.assertEqual(player.rect.x, -5)

    def test_obstacle_blocks_only_lower_collision_area(self):
        obstacle_image = pygame.Surface((20, 20), pygame.SRCALPHA)
        obstacle_image.fill((255, 255, 255, 255))
        obstacle = Obstacle(
            0,
            0,
            ("tree", 1, (20, 20), True, 0, 0),
            image=obstacle_image
        )
        collision_system = PlayerCollisionSystem()
        test_surface = pygame.Surface((20, 5), pygame.SRCALPHA)
        test_surface.fill((255, 255, 255, 255))
        test_mask = pygame.mask.from_surface(test_surface)

        upper_overlap = pygame.Rect(0, 0, 20, 5)
        lower_overlap = pygame.Rect(0, 15, 20, 5)

        self.assertFalse(
            collision_system._collides_with_obstacles(
                upper_overlap,
                test_mask,
                [obstacle]
            )
        )
        self.assertTrue(
            collision_system._collides_with_obstacles(
                lower_overlap,
                test_mask,
                [obstacle]
            )
        )

    def test_player_cannot_move_collision_rect_outside_play_area(self):
        player_image = pygame.Surface((20, 20), pygame.SRCALPHA)
        player_image.fill((255, 255, 255, 255))
        player = DummyPlayer(0, 0, player_image)
        player.velocity.x = -5

        PlayerCollisionSystem()._move_player_axis(
            player,
            [],
            dt=1,
            speed_multiplier=1,
            axis="x",
            play_area=pygame.Rect(0, 10, 40, 20)
        )

        self.assertEqual(player.position.x, 0)
        self.assertEqual(player.rect.x, 0)

    def test_player_can_move_inside_play_area(self):
        player_image = pygame.Surface((20, 20), pygame.SRCALPHA)
        player_image.fill((255, 255, 255, 255))
        player = DummyPlayer(0, 0, player_image)
        player.velocity.x = 5

        PlayerCollisionSystem()._move_player_axis(
            player,
            [],
            dt=1,
            speed_multiplier=1,
            axis="x",
            play_area=pygame.Rect(0, 10, 40, 20)
        )

        self.assertEqual(player.position.x, 5)
        self.assertEqual(player.rect.x, 5)


if __name__ == "__main__":
    unittest.main()
