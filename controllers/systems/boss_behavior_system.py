import math
import random

import pygame

from models.boss import BossOrb, BossSpike
from settings import (
    BOSS_ATTACK_ANIMATION_DURATION,
    BOSS_ATTACK_INTERVAL,
    BOSS_ORB_COUNT,
    BOSS_ORB_DAMAGE,
    BOSS_ORB_SPEED,
    BOSS_SPIKE_COUNT,
    BOSS_SPIKE_DAMAGE,
)


class BossBehaviorSystem:
    def update(
        self,
        boss,
        dt,
        player,
        pathfinder,
        solid_rects,
        enemies,
        play_area,
    ):
        if not boss.is_alive():
            return False

        boss.direction = (
            "left"
            if player.get_collision_rect().centerx < boss.get_collision_rect().centerx
            else "right"
        )
        boss.attack_timer -= dt
        boss.attack_visual_timer = max(0.0, boss.attack_visual_timer - dt)
        if boss.attack_timer <= 0:
            self.start_attack(boss, player, play_area)
            boss.attack_timer = BOSS_ATTACK_INTERVAL

        self._update_hazards(boss, dt, play_area)
        player_died = self._damage_player(boss, player)
        boss.orbs = [orb for orb in boss.orbs if orb.alive]
        boss.spikes = [spike for spike in boss.spikes if spike.alive]
        return player_died

    def start_attack(self, boss, player, play_area):
        boss.request_attack_visual(player)
        boss.attack_visual_timer = BOSS_ATTACK_ANIMATION_DURATION
        if boss.attack_number % 2 == 0:
            self._spawn_orbs(boss, player)
        else:
            self._spawn_spikes(boss, player, play_area)
        boss.attack_number += 1

    @staticmethod
    def _update_hazards(boss, dt, play_area):
        for orb in boss.orbs:
            orb.position += orb.velocity * dt
            orb.rect.center = (round(orb.position.x), round(orb.position.y))
            if not play_area.inflate(100, 100).colliderect(orb.rect):
                orb.alive = False

        for spike in boss.spikes:
            spike.age += dt
            if spike.age >= spike.WARNING_TIME + spike.ACTIVE_TIME:
                spike.alive = False

    @staticmethod
    def _spawn_orbs(boss, player):
        origin = boss.get_collision_rect().center
        target = pygame.Vector2(player.get_collision_rect().center)
        base_angle = math.atan2(target.y - origin[1], target.x - origin[0])
        spread = math.radians(66)
        for index in range(BOSS_ORB_COUNT):
            offset = spread * (index / (BOSS_ORB_COUNT - 1) - 0.5)
            direction = pygame.Vector2(
                math.cos(base_angle + offset),
                math.sin(base_angle + offset),
            )
            boss.orbs.append(BossOrb(origin, direction * BOSS_ORB_SPEED))

    @staticmethod
    def _spawn_spikes(boss, player, play_area):
        target = pygame.Vector2(player.get_collision_rect().center)
        for index in range(BOSS_SPIKE_COUNT):
            point = target + pygame.Vector2(
                random.randint(-170, 170),
                random.randint(-130, 130),
            )
            point.x = max(play_area.left + 35, min(play_area.right - 35, point.x))
            point.y = max(play_area.top + 100, min(play_area.bottom, point.y))
            boss.spikes.append(BossSpike(point, 1 + index % 2))

    def _damage_player(self, boss, player):
        player_rect = player.get_collision_rect()
        for orb in boss.orbs:
            if orb.alive and orb.rect.colliderect(player_rect):
                orb.alive = False
                if self._apply_damage(player, BOSS_ORB_DAMAGE):
                    return True

        for spike in boss.spikes:
            hit_rect = spike.rect.inflate(-24, -20)
            if spike.is_dangerous and not spike.has_hit and hit_rect.colliderect(player_rect):
                spike.has_hit = True
                if self._apply_damage(player, BOSS_SPIKE_DAMAGE):
                    return True
        return False

    @staticmethod
    def _apply_damage(player, damage):
        if player.invincible:
            return False
        died = player.take_damage(damage)
        player.start_damage_cooldown()
        return died
