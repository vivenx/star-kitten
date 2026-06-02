import pygame
from core.player import Player
from components.health_bar import HealthBar
from components.skill_tree_ui import SkillTreeUI
from components.visual_effects import DamageNumber, StageClearMessage
from components.xp_bar import XPBar
from components.xp_orb import XPOrb
from enemies.enemy_manager import EnemyManager
from stages.stage_manager import StageManager
from settings import (
    DAMAGE_NUMBER_ENEMY_HIT_COLOR, DAMAGE_NUMBER_PLAYER_HIT_COLOR,
    EXIT_LOCK_MESSAGE_TIME, HEIGHT, PLAYER_ATTACK_RANGE,
    PLAYER_ATTACK_WIDTH, PLAYER_SPAWN_DISTANCE_FROM_EXIT, WIDTH
)


class GameScene:
    def __init__(self, game):
        self.game = game
        self.player = None
        self.health_bar = None
        self.stage_manager = None
        self.enemy_manager = None
        self.xp_bar = None
        self.xp_orbs = []
        self.damage_numbers = []
        self.current_stage_index = 0
        self.stage_start_progress = None
        self.stage_cleared = False
        self.stage_clear_message = StageClearMessage()
        self.exit_message = "Уничтожьте всех врагов"
        self.exit_message_timer = 0.0
        self.exit_message_font = pygame.font.Font(None, 48)
        self.skill_tree_open = False
        self.skill_tree_ui = SkillTreeUI()

        self._setup_stage_manager()
        self._create_player()
        self._create_health_bar()
        self._create_xp_bar()
        self._create_enemy_manager()
        self._save_stage_start_progress()

    def _setup_stage_manager(self):
        self.stage_manager = StageManager()

    def _create_player(self):
        spawn_pos = self.stage_manager.current_stage.player_spawn
        self.player = Player(spawn_pos.x, spawn_pos.y)

    def _create_health_bar(self):
        self.health_bar = HealthBar(10, 10)

    def _create_xp_bar(self):
        self.xp_bar = XPBar(42, 116)

    def _create_enemy_manager(self):
        self.enemy_manager = EnemyManager(
            self.stage_manager.current_stage,
            self.player,
            self.stage_manager.difficulty_multiplier,
            self.stage_manager.current_stage_index
        )

    def _save_stage_start_progress(self):
        if self.player:
            self.stage_start_progress = self.player.get_progress_snapshot()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    self.skill_tree_open = not self.skill_tree_open
                    continue
                if event.key == pygame.K_ESCAPE:
                    self.game.change_scene("menu")

            if self.skill_tree_open:
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._handle_player_attack(event.pos)

    def _handle_player_attack(self, mouse_pos):
        if not self.player or not self.enemy_manager or self.stage_manager.is_transitioning():
            return

        if self.player.start_attack(mouse_pos):
            attack_rect = self._get_player_attack_rect()
            defeated_positions = self.enemy_manager.damage_enemies(attack_rect, self.player.attack_damage)
            self._spawn_xp_orbs(defeated_positions)
            self._spawn_damage_numbers_from_events()
            self._update_stage_clear_state()

    def _spawn_xp_orbs(self, positions):
        for position in positions:
            self.xp_orbs.append(XPOrb(position[0], position[1]))

    def _get_player_attack_rect(self):
        player_rect = self.player.get_collision_rect()
        attack_height = PLAYER_ATTACK_WIDTH

        if self.player.direction == 'left':
            return pygame.Rect(
                player_rect.centerx - PLAYER_ATTACK_RANGE,
                player_rect.centery - attack_height // 2,
                PLAYER_ATTACK_RANGE,
                attack_height
            )

        return pygame.Rect(
            player_rect.centerx,
            player_rect.centery - attack_height // 2,
            PLAYER_ATTACK_RANGE,
            attack_height
        )

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

        self._handle_xp_orb_pickups()


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
        self.player.restore_progress_snapshot(self.stage_start_progress)
        self.player.set_position(spawn_pos.x, spawn_pos.y)
        self.player.hp = self.player.max_hp
        self.xp_orbs = []
        self.damage_numbers = []
        self.stage_cleared = False
        self.stage_clear_message.reset()
        if self.enemy_manager:
            self.enemy_manager.reset_stage(
                self.stage_manager.current_stage,
                self.player,
                self.stage_manager.difficulty_multiplier,
                self.stage_manager.current_stage_index
            )

    def _handle_xp_orb_pickups(self):
        if not self.player or not self.xp_orbs:
            return

        remaining_orbs = []
        for orb in self.xp_orbs:
            if orb.can_be_picked_up_by(self.player):
                self.player.add_xp(orb.value)
            else:
                remaining_orbs.append(orb)

        self.xp_orbs = remaining_orbs

    def _spawn_damage_numbers_from_events(self):
        if not self.enemy_manager:
            return

        for event in self.enemy_manager.consume_damage_number_events():
            color = (
                DAMAGE_NUMBER_PLAYER_HIT_COLOR
                if event["target"] == "player"
                else DAMAGE_NUMBER_ENEMY_HIT_COLOR
            )
            position = event["position"]
            self.damage_numbers.append(DamageNumber(position[0], position[1], event["amount"], color))

    def _update_stage_clear_state(self):
        if self.stage_cleared or not self.enemy_manager:
            return

        if self.enemy_manager.is_stage_cleared():
            self.stage_cleared = True
            self.stage_clear_message.show()

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
        if self.skill_tree_open:
            return

        dt = self.game.clock.get_time() / 1000.0


        if self.stage_manager:
            self.stage_manager.update(dt)

        if self.exit_message_timer > 0:
            self.exit_message_timer -= dt
            if self.exit_message_timer < 0:
                self.exit_message_timer = 0

        self.stage_clear_message.update(dt)

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
            if self.xp_bar:
                self.xp_bar.update(dt, self.player)
            for orb in self.xp_orbs:
                orb.update(dt)
            for number in self.damage_numbers:
                number.update(dt)
            self.damage_numbers = [number for number in self.damage_numbers if number.is_alive()]


            self._handle_collisions(dt)

            if self.enemy_manager:
                player_died = self.enemy_manager.update(dt)
                if player_died or not self.player.is_alive():
                    self._on_player_death()
                else:
                    self._spawn_damage_numbers_from_events()
                    self._update_stage_clear_state()


            self._check_exit_zone()

        if self.stage_manager.current_stage_index != self.current_stage_index:
            self.current_stage_index = self.stage_manager.current_stage_index
            self.xp_orbs = []
            self.damage_numbers = []
            self.stage_cleared = False
            self.stage_clear_message.reset()
            if self.enemy_manager:
                self.enemy_manager.reset_stage(
                    self.stage_manager.current_stage,
                    self.player,
                    self.stage_manager.difficulty_multiplier,
                    self.stage_manager.current_stage_index
                )
            self._save_stage_start_progress()

    def draw(self):

        if self.stage_manager:
            self.stage_manager.draw(self.game.screen)


        if self.player:
            for orb in self.xp_orbs:
                orb.draw(self.game.screen)

            if self.enemy_manager:
                self.enemy_manager.draw(self.game.screen)

            self.game.screen.blit(self.player.image, self.player.rect)
            for number in self.damage_numbers:
                number.draw(self.game.screen)


            self._draw_ui()

        if self.skill_tree_open:
            self.skill_tree_ui.draw(self.game.screen)

    def _draw_ui(self):
        if self.health_bar and self.player:
            self.health_bar.draw(self.game.screen, self.player.hp, self.player.max_hp)

        if self.xp_bar and self.player:
            self.xp_bar.draw(self.game.screen, self.player)

        self.stage_clear_message.draw(self.game.screen)

        if self.exit_message_timer > 0:
            self._draw_exit_message()

    def _draw_exit_message(self):
        text_surface = self.exit_message_font.render(self.exit_message, True, (255, 255, 255))
        shadow_surface = self.exit_message_font.render(self.exit_message, True, (20, 20, 20))
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT - 80))
        shadow_rect = shadow_surface.get_rect(center=(WIDTH // 2 + 2, HEIGHT - 78))

        self.game.screen.blit(shadow_surface, shadow_rect)
        self.game.screen.blit(text_surface, text_rect)
