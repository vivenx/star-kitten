import pygame

from settings import COLOR_FOREST_INFECTED, COLOR_FOREST_NORMAL, HEIGHT, WIDTH


class StageView:
    def __init__(self):
        self.background_cache = {}
        self.obstacle_cache = {}

    def draw_background(self, surface, stage):
        background = self._get_background(stage)
        if background:
            surface.blit(background, (0, 0))
        else:
            surface.fill(stage.background_color)

    def draw_obstacle(self, surface, obstacle):
        image = self._get_obstacle_image(obstacle)
        if image:
            surface.blit(image, obstacle.rect)
            return

        color = COLOR_FOREST_INFECTED if "crystal" in obstacle.prefix else COLOR_FOREST_NORMAL
        pygame.draw.rect(surface, color, obstacle.rect)

    def _get_background(self, stage):
        if not stage.background_image_path:
            return None

        if stage.background_image_path not in self.background_cache:
            try:
                image = pygame.image.load(stage.background_image_path).convert()
                image = pygame.transform.scale(image, (WIDTH, HEIGHT))
            except FileNotFoundError:
                image = None
            self.background_cache[stage.background_image_path] = image

        return self.background_cache[stage.background_image_path]

    def _get_obstacle_image(self, obstacle):
        key = (obstacle.prefix, obstacle.variant_index, obstacle.size)
        if key not in self.obstacle_cache:
            image = self._load_obstacle_image(obstacle.prefix, obstacle.variant_index, obstacle.size)
            if image is None:
                for fallback_index in range(1, 4):
                    image = self._load_obstacle_image(obstacle.prefix, fallback_index, obstacle.size)
                    if image is not None:
                        break
            self.obstacle_cache[key] = image
        return self.obstacle_cache[key]

    def _load_obstacle_image(self, prefix, variant_index, size):
        try:
            image = pygame.image.load(
                f"assets/images/forest/obstacles/{prefix}_{variant_index}.png"
            ).convert_alpha()
            return pygame.transform.scale(image, size)
        except FileNotFoundError:
            return None
