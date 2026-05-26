import unittest

import pygame

from enemies.pathfinder import Pathfinder


class DummyObstacle:
    def __init__(self, rect, is_solid=True, damage=0):
        self.rect = rect
        self.is_solid = is_solid
        self.damage = damage

    def deals_damage(self):
        return self.damage > 0


class DummyStage:
    def __init__(self, obstacles=None):
        self.play_area = pygame.Rect(0, 0, 120, 120)
        self.obstacles = obstacles or []


class PathfinderTest(unittest.TestCase):
    def test_finds_path_around_solid_obstacle(self):
        obstacle = DummyObstacle(pygame.Rect(40, 0, 40, 80))
        pathfinder = Pathfinder(DummyStage([obstacle]), cell_size=40, agent_size=(20, 20))

        path = pathfinder.find_path((20, 20), (100, 20))

        self.assertEqual(
            [(int(point.x), int(point.y)) for point in path],
            [
                (20, 20),
                (20, 60),
                (20, 100),
                (60, 100),
                (100, 100),
                (100, 60),
                (100, 20),
            ],
        )

    def test_uses_nearest_walkable_cell_for_blocked_target(self):
        obstacle = DummyObstacle(pygame.Rect(80, 0, 40, 40))
        pathfinder = Pathfinder(DummyStage([obstacle]), cell_size=40, agent_size=(20, 20))

        path = pathfinder.find_path((20, 20), (100, 20))

        self.assertTrue(path)
        self.assertNotEqual((int(path[-1].x), int(path[-1].y)), (100, 20))
        self.assertIn(
            (int(path[-1].x), int(path[-1].y)),
            {
                (60, 20),
                (100, 60),
            },
        )

    def test_returns_empty_path_when_every_cell_is_blocked(self):
        obstacle = DummyObstacle(pygame.Rect(0, 0, 120, 120))
        pathfinder = Pathfinder(DummyStage([obstacle]), cell_size=40, agent_size=(20, 20))

        self.assertEqual(pathfinder.find_path((20, 20), (100, 100)), [])


if __name__ == "__main__":
    unittest.main()
