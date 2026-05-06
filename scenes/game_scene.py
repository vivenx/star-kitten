import pygame
from core.player import Player
from components.health_bar import HealthBar
from stages.stage_manager import StageManager
from settings import PLAYER_SPAWN_DISTANCE_FROM_EXIT


class GameScene:
    def __init__(self, game):
        self.game = game
        self.player = None
        self.health_bar = None
        self.stage_manager = None

        self._setup_stage_manager()
        self._create_player()
        self._create_health_bar()

    def _setup_stage_manager(self):
        """Настройка менеджера этапов."""
        self.stage_manager = StageManager()

    def _create_player(self):
        """Создание игрока на позиции спавна текущего этапа."""
        spawn_pos = self.stage_manager.current_stage.player_spawn
        self.player = Player(spawn_pos.x, spawn_pos.y)

    def _create_health_bar(self):
        """Создание полоски здоровья."""
        self.health_bar = HealthBar(10, 10)

    def handle_events(self):
        """Обработка событий."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.change_scene("menu")

    def _handle_collisions(self, dt):
        """Обработка коллизий игрока с препятствиями."""
        if not self.player:
            return

        current_stage = self.stage_manager.current_stage

        # Получаем твердые препятствия для коллизий
        solid_obstacles = current_stage.get_solid_obstacles()

        # Получаем кусты для замедления
        bushes = [obs for obs in current_stage.obstacles if obs.prefix == "bush"]

        # Проверяем нахождение в кустах для замедления (текущая позиция)
        player_collision_rect = self.player.get_collision_rect()
        in_bush = False
        for bush in bushes:
            if player_collision_rect.colliderect(bush.rect):
                in_bush = True
                break

        # Применяем замедление если в кустах
        speed_multiplier = 0.5 if in_bush else 1.0

        # --- ДВИЖЕНИЕ ПО ОСИ X ---
        if self.player.velocity.x != 0:
            # Вычисляем новую позицию по X с учётом замедления
            new_x = self.player.position.x + self.player.velocity.x * dt * speed_multiplier

            # Создаем тестовый rect для проверки коллизий на основе НОВОЙ позиции X
            # Рассчитываем координаты collision_rect вручную на основе новой позиции
            coll_width = self.player.rect.width
            coll_height = int(self.player.rect.height * self.player.collision_height_ratio)
            # Collision rect находится в нижней части спрайта
            test_x = int(new_x)
            test_y = int(self.player.position.y) + self.player.rect.height - coll_height

            test_rect = pygame.Rect(test_x, test_y, coll_width, coll_height)

            # Проверяем коллизии с каждым твердым препятствием
            collided = False
            for obstacle in solid_obstacles:
                if test_rect.colliderect(obstacle.rect):
                    collided = True
                    break

            if not collided:
                # Нет коллизии - применяем движение
                self.player.position.x = new_x
                self.player.rect.x = int(new_x)
            # Если коллизия - просто не применяем движение (останавливаемся)

        # --- ДВИЖЕНИЕ ПО ОСИ Y ---
        if self.player.velocity.y != 0:
            # Вычисляем новую позицию по Y с учётом замедления
            new_y = self.player.position.y + self.player.velocity.y * dt * speed_multiplier

            # Создаем тестовый rect для проверки коллизий на основе НОВОЙ позиции Y
            # Рассчитываем координаты collision_rect вручную на основе новой позиции
            coll_width = self.player.rect.width
            coll_height = int(self.player.rect.height * self.player.collision_height_ratio)
            # Collision rect находится в нижней части спрайта
            test_x = int(self.player.position.x)
            test_y = int(new_y) + self.player.rect.height - coll_height

            test_rect = pygame.Rect(test_x, test_y, coll_width, coll_height)

            # Проверяем коллизии с каждым твердым препятствием
            collided = False
            for obstacle in solid_obstacles:
                if test_rect.colliderect(obstacle.rect):
                    collided = True
                    break

            if not collided:
                # Нет коллизии - применяем движение
                self.player.position.y = new_y
                self.player.rect.y = int(new_y)
            # Если коллизия - просто не применяем движение (останавливаемся)

        # Финальное обновление collision rect (синхронизация)
        self.player._update_collision_rect()

        # Проверка коллизий с препятствиями наносящими урон (кристаллы)
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
        """Обработка смерти игрока."""
        # Респаун на начале текущего этапа
        spawn_pos = self.stage_manager.current_stage.player_spawn
        self.player.set_position(spawn_pos.x, spawn_pos.y)
        self.player.hp = self.player.max_hp

    def _check_exit_zone(self):
        """Проверка нахождения игрока в зоне выхода."""
        if not self.player or not self.stage_manager:
            return

        current_stage = self.stage_manager.current_stage
        if not current_stage.exit_zone:
            return

        # Проверяем находится ли игрок в зоне выхода (используем collision rect)
        player_collision_rect = self.player.get_collision_rect()
        if current_stage.exit_zone.rect.colliderect(player_collision_rect):
            # Игрок в зоне выхода - начинаем переход
            if self.stage_manager.can_enter_exit_zone():
                self.stage_manager.start_transition(self.player)

    def update(self):
        """Обновление игрового состояния."""
        dt = self.game.clock.get_time() / 1000.0  # delta time в секундах

        # Обновляем менеджер этапов (включая fader)
        if self.stage_manager:
            self.stage_manager.update(dt)

        # Обработка ввода и движения игрока
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

            # Обработка коллизий
            self._handle_collisions(dt)

            # Проверка зоны выхода
            self._check_exit_zone()

    def draw(self):
        """Отрисовка игрового состояния."""
        # Отрисовка этапа
        if self.stage_manager:
            self.stage_manager.draw(self.game.screen)

        # Отрисовка игрока
        if self.player:
            self.game.screen.blit(self.player.image, self.player.rect)

            # Отрисовка UI
            self._draw_ui()

    def _draw_ui(self):
        """Отрисовка интерфейса с HP."""
        if self.health_bar and self.player:
            self.health_bar.draw(self.game.screen, self.player.hp, self.player.max_hp)