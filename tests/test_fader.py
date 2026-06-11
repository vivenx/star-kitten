from views.transitions.fader import Fader


def test_fade_out_callback_can_start_fade_in():
    fader = Fader()
    fade_in_completed = []

    def start_fade_in():
        fader.start_fade_in(callback=lambda: fade_in_completed.append(True))

    fader.start_fade_out(callback=start_fade_in)
    fader.update(2.0)

    assert fader.is_fading_in
    assert fader.transition_stage == "in"

    fader.update(2.0)

    assert fade_in_completed == [True]
    assert not fader.is_transitioning()

