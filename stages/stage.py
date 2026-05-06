import pygame
import random
from settings import (
    WIDTH, HEIGHT,
    OBSTACLE_TYPES, OBSTACLE_MIN_COUNT, OBSTACLE_MAX_COUNT,
    OBSTACLE_MIN_DISTANCE_FROM_PLAYER, OBSTACLE_MIN_DISTANCE_FROM_EXIT,
    STAGE_PLAY_AREA_MARGIN, EXIT_ZONE_SIZE, EXIT_ZONE_POSITION,
    COLOR_FOREST_NORMAL, COLOR_FOREST_INFECTED, COLOR_FOREST_BOSS,
)


class Obstacle:
    """Препятствие на арене."""

    def __init__(self, x, y, obstacle_type_data, image=None):
        self.x = x
        self.y = y
        self.prefix = obstacle_type_data[0]
        self.weight = obstacle_type_data[1]
        self.size = obstacle_type_data[2]
        self.is_solid = obstacle_type_data[3]
        self.damage = obstacle_type_data[4]
        self.damage_cooldown = obstacle_type_data[5]

        self.image = image
        if self.image is None:
            self.image = self._load_random_image()

        # Масштабируем изображение под размер
        if self.image:
            self.image = pygame.transform.scale(self.image, self.size)

        self.rect = pygame.Rect(x, y, self.size[0], self.size[1])

    def _load_random_image(self):
        """Загружает случайное изображение для этого типа препятствия."""
        base_path = f"assets/images/forest/obstacles/{self.prefix}"
        images = []

        for i in range(1, 4):  # пробуем найти 1.png, 2.png, 3.png
            try:
                img = pygame.image.load(f"{base_path}_{i}.png").convert_alpha()
                images.append(img)
            except FileNotFoundError:
                break

        if images:
            return random.choice(images)
        return None

    def draw(self, surface):
        """Отрисовка препятствия."""
        if self.image:
            surface.blit(self.image, self.rect)
        else:
            # Fallback: рисуем прямоугольник
            color = COLOR_FOREST_INFECTED if "cristal" in self.prefix else COLOR_FOREST_NORMAL
            pygame.draw.rect(surface, color, self.rect)

    def deals_damage(self):
        """Возвращает True если препятствие наносит урон."""
        return self.damage > 0


class ExitZone:
    """Зона выхода для перехода на следующий этап."""

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.active = True

    def draw(self, surface):
        """Отрисовка зоны выхода - скрыта (без визуального отображения)."""
        # Зона выхода невидима - игрок просто входит в неё
        pass

    def contains_point(self, point):
        """Проверяет находится ли точка внутри зоны выхода."""
        return self.rect.collidepoint(point)


class Stage:
    """Класс этапа/арены."""

    def __init__(self, stage_index, name, background_color, background_image_path=None):
        self.stage_index = stage_index
        self.name = name
        self.background_color = background_color
        self.background_image_path = background_image_path
        self.background_image = None

        self.obstacles = []
        self.exit_zone = None
        self.player_spawn = pygame.Vector2(100, 100)

        # Play area boundaries
        self.play_area = pygame.Rect(
            STAGE_PLAY_AREA_MARGIN,
            STAGE_PLAY_AREA_MARGIN,
            WIDTH - 2 * STAGE_PLAY_AREA_MARGIN,
            HEIGHT - 2 * STAGE_PLAY_AREA_MARGIN
        )

        self._load_background()
        self._setup_exit_zone()  # Сначала устанавливаем спавн и выход
        self.generate_obstacles()  # Потом генерируем препятствия с учётом спавна

    def _load_background(self):
        """Загрузка фона арены."""
        if self.background_image_path:
            try:
                self.background_image = pygame.image.load(self.background_image_path).convert()
                self.background_image = pygame.transform.scale(self.background_image, (WIDTH, HEIGHT))
            except FileNotFoundError:
                pass

    def generate_obstacles(self):
        """Генерация препятствий с учетом весов и ограничений."""
        self.obstacles = []

        # Определяем количество препятствий
        count = random.randint(OBSTACLE_MIN_COUNT, OBSTACLE_MAX_COUNT)

        # Получаем типы препятствий и их веса
        types = [t for t in OBSTACLE_TYPES]
        weights = [t[1] for t in types]

        attempts = 0
        max_attempts = count * 20  # лимит попыток

        while len(self.obstacles) < count and attempts < max_attempts:
            attempts += 1

            # Выбираем тип препятствия через weighted random
            chosen_type = random.choices(types, weights=weights)[0]

            # Генерируем позицию
            x = random.randint(self.play_area.left, self.play_area.right - chosen_type[2][0])
            y = random.randint(self.play_area.top, self.play_area.bottom - chosen_type[2][1])

            new_rect = pygame.Rect(x, y, chosen_type[2][0], chosen_type[2][1])

            # Проверяем что не спавнится слишком близко к спавну игрока
            spawn_rect = pygame.Rect(
                self.player_spawn.x - OBSTACLE_MIN_DISTANCE_FROM_PLAYER,
                self.player_spawn.y - OBSTACLE_MIN_DISTANCE_FROM_PLAYER,
                OBSTACLE_MIN_DISTANCE_FROM_PLAYER * 2,
                OBSTACLE_MIN_DISTANCE_FROM_PLAYER * 2
            )
            if new_rect.colliderect(spawn_rect):
                continue

            # Проверяем что не спавнится слишком близко к выходу
            if self.exit_zone:
                exit_buffer = pygame.Rect(
                    self.exit_zone.rect.left - OBSTACLE_MIN_DISTANCE_FROM_EXIT,
                    self.exit_zone.rect.top - OBSTACLE_MIN_DISTANCE_FROM_EXIT,
                    self.exit_zone.rect.width + OBSTACLE_MIN_DISTANCE_FROM_EXIT * 2,
                    self.exit_zone.rect.height + OBSTACLE_MIN_DISTANCE_FROM_EXIT * 2
                )
                if new_rect.colliderect(exit_buffer):
                    continue

            # Проверяем что не пересекается с другими препятствиями
            overlaps = False
            for obs in self.obstacles:
                if new_rect.colliderect(obs.rect):
                    overlaps = True
                    break

            if not overlaps:
                obstacle = Obstacle(x, y, chosen_type)
                self.obstacles.append(obstacle)

    def _setup_exit_zone(self):
        """Настройка зоны выхода."""
        # Выход всегда справа (чтобы игрок шел слева направо)
        x = self.play_area.right - EXIT_ZONE_SIZE[0]
        y = self.play_area.centery - EXIT_ZONE_SIZE[1] // 2

        self.exit_zone = ExitZone(x, y, EXIT_ZONE_SIZE[0], EXIT_ZONE_SIZE[1])

        # Спавн игрока всегда слева по центру
        self.player_spawn = pygame.Vector2(
            self.play_area.left + 50,
            self.play_area.centery
        )

    def update(self, dt):
        """Обновление состояния арены."""
        pass  # Можно добавить анимации или другие обновления

    def draw(self, surface):
        """Отрисовка арены."""
        # Фон
        if self.background_image:
            surface.blit(self.background_image, (0, 0))
        else:
            surface.fill(self.background_color)

        # Зона выхода
        if self.exit_zone:
            self.exit_zone.draw(surface)

        # Препятствия
        for obstacle in self.obstacles:
            obstacle.draw(surface)

    def get_solid_obstacles(self):
        """Возвращает список твердых препятствий для коллизий."""
        return [obs for obs in self.obstacles if obs.is_solid]

    def get_damaging_obstacles(self):
        """Возвращает список препятствий наносящих урон."""
        return [obs for obs in self.obstacles if obs.deals_damage()]

    def regenerate_with_new_spawn(self, new_spawn_pos):
        """Перегенерация препятствий с новым спавном игрока."""
        self.player_spawn = pygame.Vector2(new_spawn_pos)
        self.generate_obstacles()