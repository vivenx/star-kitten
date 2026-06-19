import random

from models.stage import Stage
from settings import (
    ARENA_COUNT,
    COLOR_FOREST_NORMAL, COLOR_FOREST_INFECTED, COLOR_FOREST_BOSS,
    COLOR_CAVE,
    DIFFICULTY_PER_ARENA,
)


class StageManager:

    ENDLESS_REGULAR_STAGE_COUNT = 5

    def __init__(self):
        self.stages = []
        self.current_stage_index = 0
        self.transition_phase = "idle"
        self._player_ref = None
        self.stage_title_events = []
        self.stage_configs = []
        self.endless_mode = False
        self.endless_cycle = 0
        self._setup_stages()
        self._queue_stage_intro()

    def _setup_stages(self):
        self.stage_configs = [
            ("Дремучий лес", COLOR_FOREST_NORMAL, "assets/images/forest/stages/stage_1.png", "forest"),
            ("Зараженный лес", COLOR_FOREST_INFECTED, "assets/images/forest/stages/stage_2.png", "forest"),
            ("Сердце леса", COLOR_FOREST_BOSS, "assets/images/forest/stages/stage_3.png", "forest"),
            ("Вход в пещеру", COLOR_CAVE, "assets/images/cave/stages/stage1.png", "cave"),
            ("Глубины пещеры", COLOR_CAVE, "assets/images/cave/stages/stage2.png", "cave"),
            ("Кристальный грот", COLOR_CAVE, "assets/images/cave/stages/stage3.png", "cave"),
        ]

        for stage_index in range(ARENA_COUNT):
            boss_type = "forest" if stage_index == 2 else "cave" if stage_index == 5 else None
            self.stages.append(self._create_stage(stage_index, boss_type=boss_type))

    def _create_stage(self, stage_index, config_index=None, boss_type=None, endless=False):
        if config_index is None:
            config_index = stage_index % len(self.stage_configs)
        name, background_color, background_image_path, biome = self.stage_configs[
            config_index
        ]
        arena_number = stage_index + 1
        stage_name = name if stage_index < len(self.stage_configs) else f"{name} {arena_number}"

        return Stage(
            stage_index=stage_index,
            name=stage_name,
            background_color=background_color,
            background_image_path=background_image_path,
            biome=biome,
            boss_type=boss_type,
            endless=endless,
        )

    def begin_endless_mode(self):
        self.endless_mode = True
        if len(self.stages) <= ARENA_COUNT:
            self._append_endless_cycle()

    def ensure_stage_exists(self, stage_index):
        self.endless_mode = True
        while len(self.stages) <= stage_index:
            self._append_endless_cycle()

    def reset_endless_run(self):
        if not self.endless_mode:
            return False

        self.ensure_stage_exists(ARENA_COUNT)
        self.current_stage_index = ARENA_COUNT
        self.transition_phase = "idle"
        self._player_ref = None
        self.current_stage.generate_obstacles()
        self.stage_title_events = []
        self._queue_stage_intro()
        return True

    def _append_endless_cycle(self):
        self.endless_cycle += 1
        self._append_endless_biome_block("forest")
        self._append_endless_biome_block("cave")

    def _append_endless_biome_block(self, biome):
        regular_configs = (0, 1) if biome == "forest" else (3, 4)
        boss_config = 2 if biome == "forest" else 5

        for _ in range(self.ENDLESS_REGULAR_STAGE_COUNT):
            stage_index = len(self.stages)
            self.stages.append(self._create_stage(
                stage_index,
                config_index=random.choice(regular_configs),
                endless=True,
            ))

        stage_index = len(self.stages)
        self.stages.append(self._create_stage(
            stage_index,
            config_index=boss_config,
            boss_type=biome,
            endless=True,
        ))

    @property
    def current_stage(self):
        return self.stages[self.current_stage_index]

    @property
    def difficulty_multiplier(self):
        return 1.0 + self.current_stage_index * DIFFICULTY_PER_ARENA

    @property
    def has_next_stage(self):
        return self.current_stage_index < len(self.stages) - 1

    def load_next_stage(self, player_position=None):
        if self.endless_mode and not self.has_next_stage:
            self._append_endless_cycle()
        if not self.has_next_stage:
            return False

        self.current_stage_index += 1


        self.current_stage.generate_obstacles()

        return True

    def start_transition(self, player_ref=None):
        if self.endless_mode and not self.has_next_stage:
            self._append_endless_cycle()
        if not self.has_next_stage or self.is_transitioning():
            return False

        self._player_ref = player_ref
        self.transition_phase = "fading_out"
        self._queue_stage_outro()
        return True

    def complete_fade_out(self):
        if self.transition_phase != "fading_out":
            return False

        self.load_next_stage()

        spawn_pos = self.current_stage.player_spawn
        if self._player_ref:
            self._player_ref.set_position(spawn_pos.x, spawn_pos.y)
        self.transition_phase = "fading_in"
        self._queue_stage_intro()
        return True

    def complete_fade_in(self):
        if self.transition_phase != "fading_in":
            return False

        self.transition_phase = "idle"
        self._player_ref = None
        return True

    def update(self, dt):
        self.current_stage.update(dt)

    def is_transitioning(self):
        return self.transition_phase != "idle"

    def can_enter_exit_zone(self):
        return not self.is_transitioning()

    def consume_stage_title_events(self):
        events = self.stage_title_events
        self.stage_title_events = []
        return events

    def _queue_stage_intro(self):
        arena_number = self.current_stage_index + 1
        self.stage_title_events.append((self.current_stage.name, f"Этап {arena_number}"))

    def _queue_stage_outro(self):
        arena_number = self.current_stage_index + 1
        self.stage_title_events.append(("Этап пройден", f"Этап {arena_number}"))
