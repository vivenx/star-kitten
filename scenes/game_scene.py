import pygame
from core.player import Player
from components.health_bar import HealthBar
from enemies.enemy_manager import EnemyManager
from stages.stage_manager import StageManager
from settings import EXIT_LOCK_MESSAGE_TIME, HEIGHT, PLAYER_SPAWN_DISTANCE_FROM_EXIT, WIDTH


class GameScene:
    def __init__(self, game):
        self.game = game
        self.player = None
        self.health_bar = None
        self.stage_manager = None
        self.enemy_manager = None
        self.current_stage_index = 0
        self.exit_message = "Уничтожьте всех врагов"
        self.exit_message_timer = 0.0
        self.exit_message_font = pygame.font.Font(None, 48)

        self._setup_stage_manager()
        self._create_player()
        self._create_health_bar()
        self._create_enemy_manager()

    def _setup_stage_manager(self):
        self.stage_manager = StageManager()

    def _create_player(self):
        spawn_pos = self.stage_manager.current_stage.player_spawn
        self.player = Player(spawn_pos.x, spawn_pos.y)

    def _create_health_bar(self):
        self.health_bar = HealthBar(10, 10)

    def _create_enemy_manager(self):
        self.enemy_manager = EnemyManager(self.stage_manager.current_stage, self.player)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.change_scene("menu")

    def _handle_collisions(self, dt):
        if not self.player:
            return

        current_stage = self.stage_manager.current_stage


        solid_obstacles = current_stage.get_solid_obstacles()


        bushes = [obs for obs in current_stage.obstacles if obs.prefix == "bush"]


        player_collision_rect = self.player.get_collision_rect()
        in_bush = False
        for bush in bushes:
            if player_collision_rect.colliderect(bush.rect):
                in_bush = True
                break


        speed_multiplier = 0.5 if in_bush else 1.0


        if self.player.velocity.x != 0:

            new_x = self.player.position.x + self.player.velocity.x * dt * speed_multiplier


            coll_width = self.player.rect.width
            coll_height = int(self.player.rect.height * self.player.collision_height_ratio)

            test_x = int(new_x)
            test_y = int(self.player.position.y) + self.player.rect.height - coll_height

            test_rect = pygame.Rect(test_x, test_y, coll_width, coll_height)


            collided = False
            for obstacle in solid_obstacles:
                if test_rect.colliderect(obstacle.rect):
                    collided = True
                    break

            if not collided:

                self.player.position.x = new_x
                self.player.rect.x = int(new_x)


        if self.player.velocity.y != 0:

            new_y = self.player.position.y + self.player.velocity.y * dt * speed_multiplier


            coll_width = self.player.rect.width
            coll_height = int(self.player.rect.height * self.player.collision_height_ratio)

            test_x = int(self.player.position.x)
            test_y = int(new_y) + self.player.rect.height - coll_height

            test_rect = pygame.Rect(test_x, test_y, coll_width, coll_height)


            collided = False
            for obstacle in solid_obstacles:
                if test_rect.colliderect(obstacle.rect):
                    collided = True
                    break

            if not collided:

                self.player.position.y = new_y
                self.player.rect.y = int(new_y)


        self.player._update_collision_rect()


        damaging_obstacles = current_stage.get_damaging_obstacles()
        player_collision_rect = self.player.get_collision_rect()
        for obstacle in damaging_obstacles:
            if player_collision_rect.colliderect(obstacle.rect):
                if self.player.is_taking_damage_from_crystal():
                    died = self.player.take_damage(obstacle.damage)
                    self.player.start_damage_cooldown()
                    if died:
                        self._on_player_death()

    def _on_player_death(self):

        spawn_pos = self.stage_manager.current_stage.player_spawn
        self.player.set_position(spawn_pos.x, spawn_pos.y)
        self.player.hp = self.player.max_hp
        if self.enemy_manager:
            self.enemy_manager.reset_stage(self.stage_manager.current_stage, self.player)

    def _check_exit_zone(self):
        if not self.player or not self.stage_manager:
            return

        current_stage = self.stage_manager.current_stage
        if not current_stage.exit_zone:
            return


        player_collision_rect = self.player.get_collision_rect()
        if current_stage.exit_zone.rect.colliderect(player_collision_rect):
            if self.enemy_manager and not self.enemy_manager.is_stage_cleared():
                self.exit_message_timer = EXIT_LOCK_MESSAGE_TIME
                return


            if self.stage_manager.can_enter_exit_zone():
                self.stage_manager.start_transition(self.player)

    def update(self):
        dt = self.game.clock.get_time() / 1000.0


        if self.stage_manager:
            self.stage_manager.update(dt)

        if self.exit_message_timer > 0:
            self.exit_message_timer -= dt
            if self.exit_message_timer < 0:
                self.exit_message_timer = 0


        if self.player and not self.stage_manager.is_transitioning():
            keys = pygame.key.get_pressed()
            dx = 0
            dy = 0

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = 1

            self.player.move(dx, dy, dt)
            self.player.update(dt)
            self.player.update_cooldown(dt)


            self._handle_collisions(dt)

            if self.enemy_manager:
                player_died = self.enemy_manager.update(dt)
                if player_died or not self.player.is_alive():
                    self._on_player_death()


            self._check_exit_zone()

        if self.stage_manager.current_stage_index != self.current_stage_index:
            self.current_stage_index = self.stage_manager.current_stage_index
            if self.enemy_manager:
                self.enemy_manager.reset_stage(self.stage_manager.current_stage, self.player)

    def draw(self):

        if self.stage_manager:
            self.stage_manager.draw(self.game.screen)


        if self.player:
            if self.enemy_manager:
                self.enemy_manager.draw(self.game.screen)

            self.game.screen.blit(self.player.image, self.player.rect)


            self._draw_ui()

    def _draw_ui(self):
        if self.health_bar and self.player:
            self.health_bar.draw(self.game.screen, self.player.hp, self.player.max_hp)

        if self.exit_message_timer > 0:
            self._draw_exit_message()

    def _draw_exit_message(self):
        text_surface = self.exit_message_font.render(self.exit_message, True, (255, 255, 255))
        shadow_surface = self.exit_message_font.render(self.exit_message, True, (20, 20, 20))
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT - 80))
        shadow_rect = shadow_surface.get_rect(center=(WIDTH // 2 + 2, HEIGHT - 78))

        self.game.screen.blit(shadow_surface, shadow_rect)
        self.game.screen.blit(text_surface, text_rect)
