import pygame

from controllers.systems.enemy_behavior_system import EnemyBehaviorSystem
from models.slime import SlimeProjectile
from settings import (
    SLIME_ATTACK_RANGE,
    SLIME_PREFERRED_DISTANCE,
    SLIME_PROJECTILE_DAMAGE,
    SLIME_PROJECTILE_SPEED,
)


class SlimeBehaviorSystem(EnemyBehaviorSystem):
    def update(self, slime, dt, player, pathfinder, solid_rects, enemies, play_area):
        if not slime.is_alive():
            return False

        self._update_attack_cooldown(slime, dt)
        distance = pygame.Vector2(slime.get_collision_rect().center).distance_to(
            player.get_collision_rect().center
        )
        if distance > SLIME_PREFERRED_DISTANCE:
            self._update_path(slime, dt, player, pathfinder)
            self._move_along_path(slime, dt, solid_rects, enemies, play_area)
        else:
            slime.velocity.update(0, 0)
            slime.is_moving = False

        if distance <= SLIME_ATTACK_RANGE and slime.attack_cooldown <= 0:
            self._shoot(slime, player)

        player_died = self._update_projectiles(slime, dt, player, play_area)
        slime.sync_rect()
        return player_died

    @staticmethod
    def _shoot(slime, player):
        origin = pygame.Vector2(slime.get_collision_rect().center)
        direction = pygame.Vector2(player.get_collision_rect().center) - origin
        if direction.length_squared() == 0:
            direction.update(1, 0)
        direction = direction.normalize()
        slime.projectiles.append(
            SlimeProjectile(origin, direction * SLIME_PROJECTILE_SPEED)
        )
        slime.attack_cooldown = slime.attack_cooldown_max
        slime.request_attack_visual(player)

    @staticmethod
    def _update_projectiles(slime, dt, player, play_area):
        player_died = False
        for projectile in slime.projectiles:
            projectile.position += projectile.velocity * dt
            projectile.rect.center = (
                round(projectile.position.x), round(projectile.position.y)
            )
            if not play_area.colliderect(projectile.rect):
                projectile.alive = False
            elif projectile.rect.colliderect(player.get_collision_rect()):
                if not player.invincible:
                    player_died = player.take_damage(SLIME_PROJECTILE_DAMAGE)
                    player.start_damage_cooldown()
                projectile.alive = False

        slime.projectiles = [p for p in slime.projectiles if p.alive]
        return player_died
