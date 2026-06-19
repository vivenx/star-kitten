import pygame
import random
from settings import (
    WIDTH, HEIGHT,
    OBSTACLE_TYPES, OBSTACLE_VARIANT_COUNTS, OBSTACLE_MIN_COUNT, OBSTACLE_MAX_COUNT,
    OBSTACLE_MIN_DISTANCE_FROM_PLAYER, OBSTACLE_MIN_DISTANCE_FROM_EXIT,
    OBSTACLE_MIN_DISTANCE_BETWEEN, OBSTACLE_COLLISION_HEIGHT_RATIO,
    STAGE_PLAY_AREA_MARGIN, EXIT_ZONE_SIZE,
    BOSS_STAGE_OBSTACLE_MIN_COUNT, BOSS_STAGE_OBSTACLE_MAX_COUNT,
)


class Obstacle:

    def __init__(self, x, y, obstacle_type_data, image=None, variant_index=None):
        self.x = x
        self.y = y
        self.prefix = obstacle_type_data[0]
        self.weight = obstacle_type_data[1]
        self.size = obstacle_type_data[2]
        self.is_solid = obstacle_type_data[3]
        self.damage = obstacle_type_data[4]
        self.damage_cooldown = obstacle_type_data[5]
        variant_count = OBSTACLE_VARIANT_COUNTS.get(self.prefix, 1)
        self.variant_index = variant_index if variant_index is not None else random.randint(1, variant_count)

        self.rect = pygame.Rect(x, y, self.size[0], self.size[1])
        self.mask = self._create_mask(image)

    def _create_mask(self, image=None):
        collision_surface = pygame.Surface(self.size, pygame.SRCALPHA)
        collision_height = max(1, int(self.size[1] * OBSTACLE_COLLISION_HEIGHT_RATIO))
        collision_rect = pygame.Rect(
            0,
            self.size[1] - collision_height,
            self.size[0],
            collision_height
        )

        if image:
            image = pygame.transform.scale(image, self.size)
            collision_surface.blit(
                image,
                collision_rect,
                collision_rect
            )
        else:
            collision_surface.fill((255, 255, 255, 255), collision_rect)

        return pygame.mask.from_surface(collision_surface)

    def collides_with_mask(self, other_rect, other_mask):
        return self.get_mask_overlap_area(other_rect, other_mask) > 0

    def get_mask_overlap_area(self, other_rect, other_mask):
        if not self.rect.colliderect(other_rect):
            return 0

        offset = (self.rect.x - other_rect.x, self.rect.y - other_rect.y)
        return other_mask.overlap_area(self.mask, offset)

    def get_depth_y(self):
        return self.rect.bottom

    def deals_damage(self):
        return self.damage > 0


class ExitZone:

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.active = True

    def contains_point(self, point):
        return self.rect.collidepoint(point)


class Stage:

    def __init__(
        self,
        stage_index,
        name,
        background_color,
        background_image_path=None,
        biome="forest",
        boss_type=None,
        endless=False,
    ):
        self.stage_index = stage_index
        self.name = name
        self.background_color = background_color
        self.background_image_path = background_image_path
        self.biome = biome
        # Keep direct Stage(index, ...) construction backwards compatible.
        self.boss_type = boss_type or ({2: "forest", 5: "cave"}.get(stage_index))
        self.endless = endless

        self.obstacles = []
        self.exit_zone = None
        self.player_spawn = pygame.Vector2(100, 100)


        self.play_area = pygame.Rect(
            STAGE_PLAY_AREA_MARGIN,
            STAGE_PLAY_AREA_MARGIN,
            WIDTH - 2 * STAGE_PLAY_AREA_MARGIN,
            HEIGHT - 2 * STAGE_PLAY_AREA_MARGIN
        )

        self._setup_exit_zone()
        self.generate_obstacles()

    def generate_obstacles(self):
        self.obstacles = []

        is_boss_stage = self.boss_type == "forest"
        if is_boss_stage:
            count = random.randint(
                BOSS_STAGE_OBSTACLE_MIN_COUNT,
                BOSS_STAGE_OBSTACLE_MAX_COUNT,
            )
            types = [t for t in OBSTACLE_TYPES if t[0] == "crystal"]
        elif self.biome == "cave":
            count = random.randint(OBSTACLE_MIN_COUNT, OBSTACLE_MAX_COUNT)
            types = [
                ("stone", 65, (120, 80), True, 0, 0),
                ("crystal", 35, (80, 100), False, 10, 0.5),
            ]
        else:
            count = random.randint(OBSTACLE_MIN_COUNT, OBSTACLE_MAX_COUNT)
            types = list(OBSTACLE_TYPES)
        weights = [t[1] for t in types]

        attempts = 0
        max_attempts = count * 80

        while len(self.obstacles) < count and attempts < max_attempts:
            attempts += 1


            chosen_type = random.choices(types, weights=weights)[0]


            x = random.randint(self.play_area.left, self.play_area.right - chosen_type[2][0])
            y = random.randint(self.play_area.top, self.play_area.bottom - chosen_type[2][1])

            new_rect = pygame.Rect(x, y, chosen_type[2][0], chosen_type[2][1])


            spawn_rect = pygame.Rect(
                self.player_spawn.x - OBSTACLE_MIN_DISTANCE_FROM_PLAYER,
                self.player_spawn.y - OBSTACLE_MIN_DISTANCE_FROM_PLAYER,
                OBSTACLE_MIN_DISTANCE_FROM_PLAYER * 2,
                OBSTACLE_MIN_DISTANCE_FROM_PLAYER * 2
            )
            if new_rect.colliderect(spawn_rect):
                continue


            if self.exit_zone:
                exit_buffer = pygame.Rect(
                    self.exit_zone.rect.left - OBSTACLE_MIN_DISTANCE_FROM_EXIT,
                    self.exit_zone.rect.top - OBSTACLE_MIN_DISTANCE_FROM_EXIT,
                    self.exit_zone.rect.width + OBSTACLE_MIN_DISTANCE_FROM_EXIT * 2,
                    self.exit_zone.rect.height + OBSTACLE_MIN_DISTANCE_FROM_EXIT * 2
                )
                if new_rect.colliderect(exit_buffer):
                    continue


            overlaps = False
            for obs in self.obstacles:
                obstacle_buffer = obs.rect.inflate(
                    OBSTACLE_MIN_DISTANCE_BETWEEN,
                    OBSTACLE_MIN_DISTANCE_BETWEEN
                )
                if new_rect.colliderect(obstacle_buffer):
                    overlaps = True
                    break

            if not overlaps:
                obstacle = Obstacle(x, y, chosen_type)
                obstacle.biome = self.biome
                self.obstacles.append(obstacle)

    def _setup_exit_zone(self):

        if self.boss_type in ("forest", "cave"):
            x = self.play_area.centerx - EXIT_ZONE_SIZE[0] // 2
            y = self.play_area.centery - EXIT_ZONE_SIZE[1] // 2
        else:
            x = self.play_area.right - EXIT_ZONE_SIZE[0]
            y = self.play_area.centery - EXIT_ZONE_SIZE[1] // 2

        self.exit_zone = ExitZone(x, y, EXIT_ZONE_SIZE[0], EXIT_ZONE_SIZE[1])


        self.player_spawn = pygame.Vector2(
            self.play_area.left + 50,
            self.play_area.centery
        )

    def update(self, dt):
        pass

    def get_solid_obstacles(self):
        return [obs for obs in self.obstacles if obs.is_solid]

    def get_damaging_obstacles(self):
        return [obs for obs in self.obstacles if obs.deals_damage()]

    def regenerate_with_new_spawn(self, new_spawn_pos):
        self.player_spawn = pygame.Vector2(new_spawn_pos)
        self.generate_obstacles()
