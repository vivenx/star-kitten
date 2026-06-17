import json
import os
from pathlib import Path


class SaveManager:
    """Stores a single autosave using an atomic file replacement."""

    SAVE_VERSION = 1

    def __init__(self, save_path="savegame.json"):
        self.save_path = Path(save_path)

    def exists(self):
        return self.save_path.is_file()

    def save(self, model):
        if not model.player or not model.stage_manager:
            return False

        data = {
            "version": self.SAVE_VERSION,
            "stage_index": model.stage_manager.current_stage_index,
            "player": model.player.get_progress_snapshot(),
        }
        data["player"]["unlocked_skills"] = list(
            data["player"]["unlocked_skills"]
        )

        temporary_path = self.save_path.with_suffix(self.save_path.suffix + ".tmp")
        try:
            self.save_path.parent.mkdir(parents=True, exist_ok=True)
            with temporary_path.open("w", encoding="utf-8") as save_file:
                json.dump(data, save_file, ensure_ascii=False, indent=2)
            os.replace(temporary_path, self.save_path)
        except (OSError, TypeError, ValueError):
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
            return False
        return True

    def load(self):
        try:
            with self.save_path.open("r", encoding="utf-8") as save_file:
                data = json.load(save_file)
        except (OSError, json.JSONDecodeError):
            return None

        if not isinstance(data, dict) or data.get("version") != self.SAVE_VERSION:
            return None
        if not isinstance(data.get("stage_index"), int):
            return None
        if not isinstance(data.get("player"), dict):
            return None
        return data

    def delete(self):
        try:
            self.save_path.unlink(missing_ok=True)
        except OSError:
            return False
        return True
