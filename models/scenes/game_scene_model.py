class GameSceneModel:
    """Хранит общее изменяемое состояние основной игровой сцены."""
    def __init__(
        self,
        *,
        stage_manager,
        loot_system,
        combat_system,
        player_collision_system,
        player_factory,
        enemy_manager_factory,
    ):
        """Создаёт модель с переданными извне игровыми зависимостями."""
        self.stage_manager = stage_manager
        self.loot_system = loot_system
        self.combat_system = combat_system
        self.player_collision_system = player_collision_system
        self._player_factory = player_factory
        self._enemy_manager_factory = enemy_manager_factory
        self.player = None
        self.enemy_manager = None
        self.damage_numbers = []
        self.current_stage_index = 0
        self.stage_start_progress = None
        self.endless_start_progress = None
        self.stage_cleared = False
        self.cave_prompt_visible = False
        self.final_star_prompt_visible = False
        self.final_star_prompt = "Нажмите F, чтобы забрать Финальную звезду"
        self.final_cutscene_requested = False
        self.portal_prompt = "Нажмите F, чтобы войти в портал"
        self.cave_prompt = "Нажмите F, чтобы спуститься в пещеру"
        self.skill_tree_open = False
        self.game_over = False

        self._create_player()
        self._create_enemy_manager()
        self.save_stage_start_progress()

    def start_endless_mode(self):
        """Запускает бесконечный режим и возвращает признак успешного перехода."""
        self.endless_start_progress = self.player.get_progress_snapshot()
        self.stage_manager.begin_endless_mode()
        if not self.stage_manager.load_next_stage():
            return False

        self.current_stage_index = self.stage_manager.current_stage_index
        spawn = self.stage_manager.current_stage.player_spawn
        self.player.set_position(spawn.x, spawn.y)
        self.player.hp = self.player.max_hp
        self.reset_runtime_stage_state()
        self.reset_enemy_manager_for_current_stage()
        self.stage_manager.stage_title_events = []
        self.stage_manager._queue_stage_intro()
        self.save_stage_start_progress()
        return True

    def _create_player(self):
        """Создаёт игрока в начальной точке текущего этапа."""
        spawn_pos = self.stage_manager.current_stage.player_spawn
        self.player = self._player_factory(spawn_pos.x, spawn_pos.y)

    def _create_enemy_manager(self):
        """Создаёт менеджер врагов для текущего этапа."""
        self.enemy_manager = self._enemy_manager_factory(
            self.stage_manager.current_stage,
            self.player,
            self.stage_manager.difficulty_multiplier,
            self.stage_manager.current_stage_index
        )

    def save_stage_start_progress(self):
        """Сохраняет снимок прогресса игрока на момент начала этапа."""
        if self.player:
            self.stage_start_progress = self.player.get_progress_snapshot()

    def reset_runtime_stage_state(self):
        """Сбрасывает временное состояние текущего этапа."""
        self.loot_system.clear()
        self.damage_numbers = []
        self.combat_system.clear()
        self.stage_cleared = False
        self.cave_prompt_visible = False
        self.final_star_prompt_visible = False
        self.final_cutscene_requested = False

    def reset_enemy_manager_for_current_stage(self):
        """Перенастраивает менеджер врагов для текущего этапа."""
        if not self.enemy_manager:
            return

        self.enemy_manager.reset_stage(
            self.stage_manager.current_stage,
            self.player,
            self.stage_manager.difficulty_multiplier,
            self.stage_manager.current_stage_index
        )

    def restore_save_data(self, save_data):
        """Восстанавливает состояние игры и возвращает результат операции."""
        stage_index = save_data.get("stage_index")
        player_progress = save_data.get("player")
        if not isinstance(stage_index, int):
            return False
        if save_data.get("endless_mode"):
            self.stage_manager.ensure_stage_exists(stage_index)
        if (
            not 0 <= stage_index < len(self.stage_manager.stages)
            or not isinstance(player_progress, dict)
        ):
            return False

        required_fields = {"level", "xp", "max_hp", "attack_damage"}
        if not required_fields.issubset(player_progress):
            return False
        numeric_fields = ("level", "xp", "stars", "max_hp", "attack_damage")
        if any(
            field in player_progress
            and (
                not isinstance(player_progress[field], (int, float))
                or isinstance(player_progress[field], bool)
                or player_progress[field] < 0
            )
            for field in numeric_fields
        ):
            return False
        unlocked_skills = player_progress.get("unlocked_skills", [])
        if not isinstance(unlocked_skills, (list, tuple)) or not all(
            isinstance(skill_id, str) for skill_id in unlocked_skills
        ):
            return False

        self.stage_manager.current_stage_index = stage_index
        self.current_stage_index = stage_index
        self.stage_manager.current_stage.generate_obstacles()
        spawn = self.stage_manager.current_stage.player_spawn
        self.player.set_position(spawn.x, spawn.y)
        try:
            self.player.restore_progress_snapshot(player_progress)
        except (KeyError, TypeError, ValueError):
            return False
        if self.stage_manager.endless_mode:
            endless_start_progress = save_data.get(
                "endless_start_progress", player_progress
            )
            if not isinstance(endless_start_progress, dict):
                return False
            if not required_fields.issubset(endless_start_progress):
                return False
            self.endless_start_progress = {
                **endless_start_progress,
                "unlocked_skills": tuple(
                    endless_start_progress.get("unlocked_skills", ())
                ),
            }
        self.player.hp = self.player.max_hp
        self.reset_runtime_stage_state()
        self.reset_enemy_manager_for_current_stage()
        self.stage_manager.stage_title_events = []
        self.stage_manager._queue_stage_intro()
        self.save_stage_start_progress()
        return True
