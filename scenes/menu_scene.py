import pygame
from settings import WIDTH, HEIGHT


class MenuScene:
    def __init__(self, game):
        self.game = game

        self.bg = pygame.image.load("assets/images/menu_bg.png").convert()
        self.bg = pygame.transform.scale(self.bg, (WIDTH, HEIGHT))

        self.start_button_points = [(545, 408), (117, 410), (120, 507), (554, 509)]

        self.exit_button_points = [(543, 684), (126, 688), (121, 779), (553, 780)]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if self.point_in_polygon(mouse_pos, self.start_button_points):
                        self.game.change_scene("game")
                    
                    if self.point_in_polygon(mouse_pos, self.exit_button_points):
                        self.game.running = False


    def update(self):
        pass

    def point_in_polygon(self, point, polygon):
        """Проверяет, находится ли точка внутри многоугольника"""
        x, y = point
        inside = False
        n = len(polygon)
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def draw(self):
        self.game.screen.blit(self.bg, (0, 0))
