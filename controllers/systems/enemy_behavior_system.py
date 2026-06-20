import pygame


class EnemyBehaviorSystem:
    """Реализует базовое преследование и атаку обычного противника."""
    def update(self, enemy, dt, player, pathfinder, solid_rects, enemies, play_area):
        if not enemy.is_alive():
            return False

        self._update_attack_cooldown(enemy, dt)
        self._update_path(enemy, dt, player, pathfinder)
        self._move_along_path(enemy, dt, solid_rects, enemies, play_area)
        player_died = self._attack_player(enemy, player)
        enemy.sync_rect()
        return player_died

    @staticmethod
    def _update_attack_cooldown(enemy, dt):
        enemy.attack_cooldown = max(0.0, enemy.attack_cooldown - dt)

    @staticmethod
    def _update_path(enemy, dt, player, pathfinder):
        """Периодически обновляет путь врага к игроку с помощью алгоритма A*.

        Новый маршрут строится только после завершения таймера обновления,
        чтобы не выполнять ресурсоёмкий поиск пути на каждом кадре.

        Args:
            enemy: Враг, для которого необходимо обновить маршрут.
            dt: Время в секундах, прошедшее с предыдущего кадра.
            player: Игрок, позиция которого используется как цель маршрута.
            pathfinder: Объект поиска пути, реализующий алгоритм A*.
        """
        enemy.path_update_timer -= dt
        if enemy.path_update_timer > 0:
            return

        enemy.path_update_timer = enemy.path_update_time
        new_path = pathfinder.find_path(
            enemy.get_collision_rect().center,
            player.get_collision_rect().center,
        )
        if new_path:
            enemy.path = new_path
            enemy.path_index = 1 if len(new_path) > 1 else 0

    def _move_along_path(self, enemy, dt, solid_rects, enemies, play_area):
        enemy.is_moving = False
        enemy.velocity.update(0, 0)
        if not enemy.path or enemy.path_index >= len(enemy.path):
            return

        target = enemy.path[enemy.path_index]
        direction = target - pygame.Vector2(enemy.get_collision_rect().center)
        if direction.length() < 5:
            enemy.path_index += 1
            return

        direction = direction.normalize()
        enemy.velocity = direction * enemy.speed
        if enemy.velocity.x > 0:
            enemy.direction = "right"
        elif enemy.velocity.x < 0:
            enemy.direction = "left"

        moved_x = self._move_axis(
            enemy, enemy.velocity.x * dt, 0, solid_rects, enemies, play_area
        )
        moved_y = self._move_axis(
            enemy, 0, enemy.velocity.y * dt, solid_rects, enemies, play_area
        )
        enemy.is_moving = moved_x or moved_y

    def _move_axis(self, enemy, dx, dy, solid_rects, enemies, play_area):
        if dx == 0 and dy == 0:
            return False

        old_position = enemy.position.copy()
        enemy.position.x += dx
        enemy.position.y += dy
        enemy.sync_rect()
        collision_rect = enemy.get_collision_rect()

        collides = any(collision_rect.colliderect(rect) for rect in solid_rects)
        if not collides:
            collides = any(
                other is not enemy
                and other.is_alive()
                and collision_rect.colliderect(other.get_collision_rect())
                for other in enemies
            )
        outside = bool(play_area and not play_area.contains(collision_rect))
        if collides or outside:
            enemy.position = old_position
            enemy.sync_rect()
            return False
        return True

    @staticmethod
    def _attack_player(enemy, player):
        if enemy.attack_cooldown > 0:
            return False
        if not enemy.get_collision_rect().colliderect(player.get_collision_rect()):
            return False

        died = player.take_damage(enemy.damage)
        player.start_damage_cooldown()
        enemy.attack_cooldown = enemy.attack_cooldown_max
        enemy.request_attack_visual(player)
        return died
