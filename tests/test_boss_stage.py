from unittest.mock import patch

import pygame

from controllers.managers.enemy_manager import EnemyManager
from controllers.systems.boss_behavior_system import BossBehaviorSystem
from controllers.systems.combat_system import CombatSystem
from controllers.systems.loot_system import LootSystem
from controllers.managers.stage_manager import StageManager
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


def test_boss_drops_exactly_ten_stars():
    stage = make_stage(2)
    player = Player(stage.player_spawn.x, stage.player_spawn.y)
    manager = EnemyManager(stage, player)
    boss = manager.enemies[0]
    loot = LootSystem()

    boss.current_hp = 1
    defeated, _ = manager.damage_enemies_with_result(
        boss.get_collision_rect(), 1
    )
    CombatSystem._spawn_drops(manager, loot, defeated)

    assert len(loot.star_orbs) == 10


def test_cave_stages_follow_the_forest_boss():
    manager = StageManager()

    assert len(manager.stages) == 6
    assert manager.stages[2].biome == "forest"
    assert manager.stages[3].biome == "cave"
    assert manager.stages[3].background_image_path.endswith("cave/stages/stage1.png")
