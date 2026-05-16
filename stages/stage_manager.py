from stages.stage import Stage
from stages.fader import Fader
from stages.stage_title import StageTitle
from settings import (
    ARENA_COUNT,
    COLOR_FOREST_NORMAL, COLOR_FOREST_INFECTED, COLOR_FOREST_BOSS,
    DIFFICULTY_PER_ARENA,
)


class StageManager:

    def __init__(self):
        self.stages = []
        self.current_stage_index = 0
        self.fader = Fader()
        self.stage_title = StageTitle()
        self.stage_configs = []
        self._setup_stages()
        self._show_stage_intro()

    def _setup_stages(self):
        self.stage_configs = [
            ("Дремучий лес", COLOR_FOREST_NORMAL, "assets/images/forest/stages/stage_1.png"),
            ("Зараженный лес", COLOR_FOREST_INFECTED, "assets/images/forest/stages/stage_2.png"),
            ("Сердце леса", COLOR_FOREST_BOSS, "assets/images/forest/stages/stage_3.png"),
        ]

        for stage_index in range(ARENA_COUNT):
            self.stages.append(self._create_stage(stage_index))

    def _create_stage(self, stage_index):
        name, background_color, background_image_path = self.stage_configs[
            stage_index % len(self.stage_configs)
        ]
        arena_number = stage_index + 1
        stage_name = name if stage_index < len(self.stage_configs) else f"{name} {arena_number}"

        return Stage(
            stage_index=stage_index,
            name=stage_name,
            background_color=background_color,
            background_image_path=background_image_path
        )

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
        if not self.has_next_stage:
            return False

        self.current_stage_index += 1


        self.current_stage.generate_obstacles()

        return True

    def start_transition(self, player_ref=None):
        if not self.has_next_stage:
            return False

        self._player_ref = player_ref
        self._show_stage_outro()
        self.fader.start_fade_out(callback=lambda: self._on_fade_out_complete(self._player_ref))
        return True

    def _on_fade_out_complete(self, player_ref):
        self.load_next_stage()

        spawn_pos = self.current_stage.player_spawn
        if player_ref:
            player_ref.set_position(spawn_pos.x, spawn_pos.y)
        self._show_stage_intro()
        self.fader.start_fade_in()

    def update(self, dt):
        self.fader.update(dt)
        self.stage_title.update(dt)
        self.current_stage.update(dt)

    def draw(self, surface):
        self.current_stage.draw(surface)
        self.fader.draw(surface)
        self.stage_title.draw(surface)

    def is_transitioning(self):
        return self.fader.is_transitioning()

    def can_enter_exit_zone(self):
        return not self.is_transitioning()

    def _show_stage_intro(self):
        arena_number = self.current_stage_index + 1
        self.stage_title.show(self.current_stage.name, f"Этап {arena_number}")

    def _show_stage_outro(self):
        arena_number = self.current_stage_index + 1
        self.stage_title.show("Этап пройден", f"Этап {arena_number}")
