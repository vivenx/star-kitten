import pygame
import os

class HealthBar:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.images = {}
        self.current_image = None

        hp_values = [100, 75, 50, 25]
        base_path = os.path.join('assets', 'images', 'hp')

        for value in hp_values:
            filename = f"{value}.png"
            filepath = os.path.join(base_path, filename)

            image = pygame.image.load(filepath).convert_alpha()
            image = pygame.transform.scale(image, (325, 120))
            self.images[value] = image

        # Инициализируем первым доступным изображением
        if self.images:
            self.current_image = self.images[100]

    def get_image(self, current_hp, max_hp):
        """Возвращает спрайт в зависимости от процента здоровья."""
        if max_hp <= 0:
            percent = 0
        else:
            percent = (current_hp / max_hp) * 100

        # Логика выбора спрайта:
        # > 75% -> 100
        # > 50% -> 75
        # > 25% -> 50
        # <= 25% -> 25

        if percent > 75:
            key = 100
        elif percent > 50:
            key = 75
        elif percent > 25:
            key = 50
        else:
            key = 25

        return self.images.get(key, self.images.get(25))

    def draw(self, surface, current_hp, max_hp):
        """Отрисовка полоски здоровья."""
        image = self.get_image(current_hp, max_hp)
        if image:
            # Центрируем или просто ставим по координатам
            rect = image.get_rect(topleft=(self.x + 20, self.y))
            surface.blit(image, rect)