from models.scenes.ending_scene_model import EndingSceneModel


def test_ending_contains_all_five_frames():
    model = EndingSceneModel()

    assert len(model.FRAMES) == 5
    assert "упавшую звезду" in model.text


def test_ending_advances_and_stops_on_last_frame():
    model = EndingSceneModel()

    for expected_index in range(1, 5):
        assert model.advance()
        assert model.frame_index == expected_index

    assert model.is_last_frame
    assert not model.advance()
    assert model.frame_index == 4
