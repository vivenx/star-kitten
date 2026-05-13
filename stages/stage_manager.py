from stages.stage import Stage
from stages.fader import Fader
from settings import (
    COLOR_FOREST_NORMAL, COLOR_FOREST_INFECTED, COLOR_FOREST_BOSS,
)


class StageManager:

    def __init__(self):
        self.stages = []
        self.current_stage_index = 0
        self.fader = Fader()
        self._setup_stages()

    def _setup_stages(self):

        stage1 = Stage(
            stage_index=0,
            name="Normal Forest",
            background_color=COLOR_FOREST_NORMAL,
            background_image_path="assets/images/forest/stages/stage_1.png"
        )
        self.stages.append(stage1)


        stage2 = Stage(
            stage_index=1,
            name="Infected Forest",
            background_color=COLOR_FOREST_INFECTED,
            background_image_path="assets/images/forest/stages/stage_2.png"
        )
        self.stages.append(stage2)


        stage3 = Stage(
            stage_index=2,
            name="Boss Arena",
            background_color=COLOR_FOREST_BOSS,
            background_image_path="assets/images/forest/stages/stage_3.png"
        )
        self.stages.append(stage3)

    @property
    def current_stage(self):
        return self.stages[self.current_stage_index]

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
        self.fader.start_fade_out(callback=lambda: self._on_fade_out_complete(self._player_ref))
        return True

    def _on_fade_out_complete(self, player_ref):
        self.load_next_stage()

        spawn_pos = self.current_stage.player_spawn
        if player_ref:
            player_ref.set_position(spawn_pos.x, spawn_pos.y)
        self.fader.start_fade_in()

    def update(self, dt):
        self.fader.update(dt)
        self.current_stage.update(dt)

    def draw(self, surface):
        self.current_stage.draw(surface)
        self.fader.draw(surface)

    def is_transitioning(self):
        return self.fader.is_transitioning()

    def can_enter_exit_zone(self):
        return not self.is_transitioning()
