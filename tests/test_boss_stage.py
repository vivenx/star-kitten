from unittest.mock import patch

import pygame

from controllers.managers.enemy_manager import EnemyManager
from controllers.systems.boss_behavior_system import BossBehaviorSystem
from models.boss import Boss
from models.player import Player
from models.stage import Stage


def make_stage(index):
    return Stage(index, "test", (0, 0, 0))


def test_third_stage_contains_only_one_boss_and_crystals():
    with patch("models.stage.random.randint", return_value=2):
        stage = make_stage(2)

    assert 1 <= len(stage.obstacles) <= 3
    assert all(obstacle.prefix == "crystal" for obstacle in stage.obstacles)

    player = Player(stage.player_spawn.x, stage.player_spawn.y)
    manager = EnemyManager(stage, player)
    assert len(manager.enemies) == 1
    assert isinstance(manager.enemies[0], Boss)
    assert manager.enemies[0].rect.center == stage.play_area.center


def test_forest_boss_alternates_orbs_and_spikes():
    stage = make_stage(2)
    player = Player(stage.player_spawn.x, stage.player_spawn.y)
    boss = Boss(stage.play_area)
    behavior = BossBehaviorSystem()

    behavior.start_attack(boss, player, stage.play_area)
    assert boss.orbs
    assert not boss.spikes

    behavior.start_attack(boss, player, stage.play_area)
    assert boss.spikes


def test_regular_stage_still_spawns_regular_enemies():
    stage = make_stage(0)
    player = Player(stage.player_spawn.x, stage.player_spawn.y)
    manager = EnemyManager(stage, player)

    assert manager.enemies
    assert all(not isinstance(enemy, Boss) for enemy in manager.enemies)
