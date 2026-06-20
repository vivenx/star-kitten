import pygame
from config import FADE_SPEED, FADE_COLOR


class Fader:
    """Создаёт плавное затемнение и осветление между состояниями сцены."""

    def __init__(self):
        self.fade_surface = pygame.Surface((pygame.display.get_surface().get_width(),
                                            pygame.display.get_surface().get_height()))
        self.fade_surface.fill(FADE_COLOR)
        self.alpha = 0
        self.is_fading_out = False
        self.is_fading_in = False
        self.fade_complete_callback = None
        self.transition_stage = None

    def start_fade_out(self, callback=None):
        self.is_fading_out = True
        self.is_fading_in = False
        self.fade_complete_callback = callback
        self.transition_stage = "out"

    def start_fade_in(self, callback=None):
        self.is_fading_in = True
        self.is_fading_out = False
        self.fade_complete_callback = callback
        self.transition_stage = "in"

    def update(self, dt):
        alpha_change = int(255 * dt / FADE_SPEED)

        if self.is_fading_out:
            self.alpha += alpha_change
            if self.alpha >= 255:
                self.alpha = 255
                self.is_fading_out = False
                callback = self.fade_complete_callback
                should_call = callback and self.transition_stage == "out"
                self.fade_complete_callback = None
                self.transition_stage = None
                if should_call:
                    callback()

        elif self.is_fading_in:
            self.alpha -= alpha_change
            if self.alpha <= 0:
                self.alpha = 0
                self.is_fading_in = False
                callback = self.fade_complete_callback
                should_call = callback and self.transition_stage == "in"
                self.fade_complete_callback = None
                self.transition_stage = None
                if should_call:
                    callback()

        self.fade_surface.set_alpha(self.alpha)

    def draw(self, surface):
        if self.alpha > 0:
            surface.blit(self.fade_surface, (0, 0))

    def is_transitioning(self):
        return self.is_fading_out or self.is_fading_in

    def is_fully_faded(self):
        return self.alpha >= 255
