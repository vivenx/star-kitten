import pygame


class PlayerCollisionSystem:
    def handle_stage_collisions(self, player, stage, dt, on_player_death):
        if not player:
            return

        solid_obstacles = stage.get_solid_obstacles()
        speed_multiplier = self._get_speed_multiplier(player, stage)

        self._move_player_axis(player, solid_obstacles, dt, speed_multiplier, "x", stage.play_area)
        self._move_player_axis(player, solid_obstacles, dt, speed_multiplier, "y", stage.play_area)
        player._update_collision_rect()

        self._handle_damaging_obstacles(player, stage, on_player_death)

    def _get_speed_multiplier(self, player, stage):
        player_collision_rect = player.get_collision_rect()
        player_collision_mask = self._get_player_collision_mask(player, player_collision_rect)
        for obstacle in stage.obstacles:
            if (
                obstacle.prefix == "bush"
                and self._collides_with_obstacle_mask(
                    player_collision_rect,
                    player_collision_mask,
                    obstacle
                )
            ):
                return 0.5
        return 1.0

    def _move_player_axis(self, player, solid_obstacles, dt, speed_multiplier, axis, play_area=None):
        velocity = player.velocity.x if axis == "x" else player.velocity.y
        if velocity == 0:
            return

        new_position = (
            player.position.x + velocity * dt * speed_multiplier
            if axis == "x"
            else player.position.y + velocity * dt * speed_multiplier
        )
        test_rect = self._get_test_rect(player, new_position, axis)
        if play_area and not play_area.contains(test_rect):
            return

        test_mask = self._get_player_collision_mask(player, test_rect)

        current_rect = player.get_collision_rect()
        current_mask = self._get_player_collision_mask(player, current_rect)
        current_overlap = self._get_obstacles_overlap_area(
            current_rect,
            current_mask,
            solid_obstacles
        )
        test_overlap = self._get_obstacles_overlap_area(
            test_rect,
            test_mask,
            solid_obstacles
        )

        if test_overlap == 0 or (current_overlap > 0 and test_overlap < current_overlap):
            if axis == "x":
                player.position.x = new_position
                player.rect.x = int(new_position)
            else:
                player.position.y = new_position
                player.rect.y = int(new_position)

    def _get_test_rect(self, player, new_position, axis):
        collision_height = int(player.rect.height * player.collision_height_ratio)
        test_x = int(new_position) if axis == "x" else int(player.position.x)
        test_y = (
            int(new_position) + player.rect.height - collision_height
            if axis == "y"
            else int(player.position.y) + player.rect.height - collision_height
        )
        return pygame.Rect(test_x, test_y, player.rect.width, collision_height)

    def _get_player_collision_mask(self, player, collision_rect):
        collision_surface = pygame.Surface(collision_rect.size, pygame.SRCALPHA)
        collision_surface.fill((255, 255, 255, 255))
        return pygame.mask.from_surface(collision_surface)

    def _collides_with_obstacles(self, test_rect, test_mask, solid_obstacles):
        return self._get_obstacles_overlap_area(test_rect, test_mask, solid_obstacles) > 0

    def _get_obstacles_overlap_area(self, test_rect, test_mask, obstacles):
        return sum(
            self._get_obstacle_overlap_area(test_rect, test_mask, obstacle)
            for obstacle in obstacles
        )

    def _collides_with_obstacle_mask(self, test_rect, test_mask, obstacle):
        return self._get_obstacle_overlap_area(test_rect, test_mask, obstacle) > 0

    def _get_obstacle_overlap_area(self, test_rect, test_mask, obstacle):
        if hasattr(obstacle, "get_mask_overlap_area"):
            return obstacle.get_mask_overlap_area(test_rect, test_mask)

        if hasattr(obstacle, "collides_with_mask"):
            return 1 if obstacle.collides_with_mask(test_rect, test_mask) else 0

        return 1 if test_rect.colliderect(obstacle.rect) else 0

    def _handle_damaging_obstacles(self, player, stage, on_player_death):
        player_collision_rect = player.get_collision_rect()
        player_collision_mask = self._get_player_collision_mask(player, player_collision_rect)
        for obstacle in stage.get_damaging_obstacles():
            if not self._collides_with_obstacle_mask(
                player_collision_rect,
                player_collision_mask,
                obstacle
            ):
                continue
            if not player.is_taking_damage_from_crystal():
                continue

            died = player.take_damage(obstacle.damage)
            player.start_damage_cooldown()
            if died:
                on_player_death()
