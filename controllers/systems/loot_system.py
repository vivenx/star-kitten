import random
import math

from models.orbs.star_orb import StarOrb
from models.orbs.xp_orb import XPOrb
from settings import (
    CAVE_SLIME_STAR_PICKUP_RADIUS,
    FINAL_STAR_IMAGE_PATH,
    FINAL_STAR_SIZE,
    STAR_DROP_CHANCE,
)


class LootSystem:
    def __init__(self):
        self.xp_orbs = []
        self.star_orbs = []

    def spawn_xp_orbs(self, positions):
        for position in positions:
            self.xp_orbs.append(XPOrb(position[0], position[1]))

    def spawn_star_orbs(self, positions):
        for position in positions:
            if random.random() < STAR_DROP_CHANCE:
                self.star_orbs.append(StarOrb(position[0], position[1]))

    def spawn_guaranteed_star_orbs(self, positions, count_per_position=1):
        for position in positions:
            for index in range(count_per_position):
                angle = math.tau * index / count_per_position
                radius = 52
                self.star_orbs.append(StarOrb(
                    position[0] + math.cos(angle) * radius,
                    position[1] + math.sin(angle) * radius,
                ))

    def spawn_boss_star(self, positions):
        for position in positions:
            orb = StarOrb(
                position[0],
                position[1],
                requires_interaction=True,
                image_path=FINAL_STAR_IMAGE_PATH,
                size=FINAL_STAR_SIZE,
                triggers_cutscene=True,
            )
            orb.rect = orb.rect.inflate(
                CAVE_SLIME_STAR_PICKUP_RADIUS * 2 - orb.rect.width,
                CAVE_SLIME_STAR_PICKUP_RADIUS * 2 - orb.rect.height,
            )
            orb.rect.center = position
            self.star_orbs.append(orb)

    def spawn_enemy_drops(self, defeated_positions):
        self.spawn_xp_orbs(defeated_positions)
        self.spawn_star_orbs(defeated_positions)

    def update(self, dt):
        for orb in self.xp_orbs:
            orb.update(dt)
        for orb in self.star_orbs:
            orb.update(dt)

    def collect_for_player(self, player):
        self.xp_orbs = self._collect_xp_orbs(player)
        self.star_orbs = self._collect_star_orbs(player)

    def _collect_xp_orbs(self, player):
        remaining_orbs = []
        for orb in self.xp_orbs:
            if orb.can_be_picked_up_by(player):
                player.add_xp(orb.value)
            else:
                remaining_orbs.append(orb)
        return remaining_orbs

    def _collect_star_orbs(self, player):
        remaining_orbs = []
        for orb in self.star_orbs:
            if not orb.requires_interaction and orb.can_be_picked_up_by(player):
                player.add_stars(orb.value)
            else:
                remaining_orbs.append(orb)
        return remaining_orbs

    def has_interactive_star_near(self, player):
        return any(
            orb.requires_interaction and orb.can_be_picked_up_by(player)
            for orb in self.star_orbs
        )

    def collect_interactive_star(self, player):
        for orb in self.star_orbs:
            if orb.requires_interaction and orb.can_be_picked_up_by(player):
                if not orb.triggers_cutscene:
                    player.add_stars(orb.value)
                self.star_orbs.remove(orb)
                return orb
        return None

    def clear(self):
        self.xp_orbs = []
        self.star_orbs = []
