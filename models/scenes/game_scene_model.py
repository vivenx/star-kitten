from controllers.managers.enemy_manager import EnemyManager
from controllers.managers.stage_manager import StageManager
from controllers.systems.combat_system import CombatSystem
from controllers.systems.loot_system import LootSystem
from controllers.systems.player_collision_system import PlayerCollisionSystem
from models.player import Player
from settings import EXIT_LOCK_MESSAGE_TIME


class GameSceneModel:
    def __init__(self):
        self.player = None
        self.stage_manager = None
        self.enemy_manager = None
        self.damage_numbers = []
        self.loot_system = LootSystem()
        self.combat_system = CombatSystem()
        self.player_collision_system = PlayerCollisionSystem()
        self.current_stage_index = 0
        self.stage_start_progress = None
        self.stage_cleared = False
        self.exit_message = "Сначала уничтожьте всех врагов"
        self.exit_message_timer = 0.0
        self.cave_prompt_visible = False
        self.final_star_prompt_visible = False
        self.final_star_prompt = "Нажмите F, чтобы забрать Финальную звезду"
        self.final_cutscene_requested = False
        self.cave_prompt = "Нажмите F, чтобы спуститься в пещеру"
        self.exit_lock_message_time = EXIT_LOCK_MESSAGE_TIME
        self.skill_tree_open = False
        self.game_over = False

        self._setup_stage_manager()
        self._create_player()
        self._create_enemy_manager()
        self.save_stage_start_progress()

    def _setup_stage_manager(self):
        self.stage_manager = StageManager()

    def _create_player(self):
        spawn_pos = self.stage_manager.current_stage.player_spawn
        self.player = Player(spawn_pos.x, spawn_pos.y)

    def _create_enemy_manager(self):
        self.enemy_manager = EnemyManager(
            self.stage_manager.current_stage,
            self.player,
            self.stage_manager.difficulty_multiplier,
            self.stage_manager.current_stage_index
        )

    def save_stage_start_progress(self):
        if self.player:
            self.stage_start_progress = self.player.get_progress_snapshot()

    def reset_runtime_stage_state(self):
        self.loot_system.clear()
        self.damage_numbers = []
        self.combat_system.clear()
        self.stage_cleared = False
        self.cave_prompt_visible = False
        self.final_star_prompt_visible = False
        self.final_cutscene_requested = False

    def reset_enemy_manager_for_current_stage(self):
        if not self.enemy_manager:
            return

        self.enemy_manager.reset_stage(
            self.stage_manager.current_stage,
            self.player,
            self.stage_manager.difficulty_multiplier,
            self.stage_manager.current_stage_index
        )
