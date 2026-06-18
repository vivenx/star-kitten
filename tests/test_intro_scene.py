from models.scenes.intro_scene_model import IntroSceneModel


def test_intro_contains_all_six_frames():
    model = IntroSceneModel()

    assert len(model.FRAMES) == 6
    assert model.title == "Мир заражается"
    assert "темная болезнь" in model.text


def test_intro_advances_and_stops_on_last_frame():
    model = IntroSceneModel()

    for expected_index in range(1, 6):
        assert model.advance()
        assert model.frame_index == expected_index

    assert model.is_last_frame
    assert not model.advance()
    assert model.frame_index == 5
