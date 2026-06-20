from controllers.managers.enemy_manager import EnemyManager
from controllers.managers.stage_manager import StageManager
from controllers.scenes.game_scene_controller import GameSceneController
from controllers.systems.combat_system import CombatSystem
from controllers.systems.loot_system import LootSystem
from controllers.systems.player_collision_system import PlayerCollisionSystem
from models.player import Player
from models.scenes.game_scene_model import GameSceneModel
from views.scenes.game_scene_view import GameSceneView


class GameScene:
    """Собирает компоненты основной игровой сцены."""
    def __init__(self, game):
        self.game = game
        self.model = GameSceneModel(
            stage_manager=StageManager(),
            loot_system=LootSystem(),
            combat_system=CombatSystem(),
            player_collision_system=PlayerCollisionSystem(),
            player_factory=Player,
            enemy_manager_factory=EnemyManager,
        )
        self.view = GameSceneView(game.screen, self.model)
        self.controller = GameSceneController(game, self.model, self.view)

    def handle_events(self):
        self.controller.handle_events()

    def update(self):
        dt = self.game.clock.get_time() / 1000.0
        self.controller.update(dt)
        self.view.update(dt)

    def draw(self):
        self.view.draw()
