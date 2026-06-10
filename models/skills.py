from dataclasses import dataclass, field

import pygame

from settings import SKILL_LOCKED


@dataclass(frozen=True)
class SkillNode:
    skill_id: str
    icon_rect: pygame.Rect
    state: str = SKILL_LOCKED
    cost: int = 0
    dependencies: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_locked(self):
        return self.state == SKILL_LOCKED


SKILL_TREE_NODES = (
    SkillNode("attack_slash", pygame.Rect(62, 253, 158, 154), cost=5),
    SkillNode(
        "attack_wave",
        pygame.Rect(62, 487, 158, 154),
        cost=8,
        dependencies=("attack_slash",),
    ),
    SkillNode(
        "attack_double_hit",
        pygame.Rect(62, 747, 158, 154),
        cost=12,
        dependencies=("attack_wave",),
    ),
    SkillNode("fairy_heal", pygame.Rect(559, 253, 158, 154), cost=5),
    SkillNode(
        "fairy_cooldown",
        pygame.Rect(559, 489, 158, 154),
        cost=8,
        dependencies=("fairy_heal",),
    ),
    SkillNode(
        "fairy_rescue",
        pygame.Rect(559, 747, 158, 154),
        cost=12,
        dependencies=("fairy_cooldown",),
    ),
    SkillNode("defense_hp", pygame.Rect(1056, 282, 157, 177), cost=5),
    SkillNode(
        "defense_shield",
        pygame.Rect(1056, 625, 157, 177),
        cost=10,
        dependencies=("defense_hp",),
    ),
)
