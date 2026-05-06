import pygame

# Window settings
WIDTH = 1600
HEIGHT = 900
FPS = 60

# Player settings
PLAYER_SPEED = 300  # pixels per second (FPS independent)
PLAYER_MAX_HP = 100
PLAYER_SIZE = (64, 64)
PLAYER_SPAWN_DISTANCE_FROM_EXIT = 200  # минимальное расстояние спавна от выхода
PLAYER_COLLISION_HEIGHT_RATIO = 0.5  # какая часть высоты игрока используется для коллизий (низ тела)

# Obstacle settings
OBSTACLE_MIN_COUNT = 8
OBSTACLE_MAX_COUNT = 15
OBSTACLE_MIN_DISTANCE_FROM_PLAYER = 150
OBSTACLE_MIN_DISTANCE_FROM_EXIT = 100

# Obstacle types with their weights and properties
# Format: (image_prefix, weight, size, is_solid, damage, damage_cooldown)
OBSTACLE_TYPES = [
    # (prefix, weight, size, is_solid, damage, damage_cooldown)
    ("stone", 25, (120, 80), True, 0, 0),      # камни - твердые
    ("bush", 25, (100, 100), False, 0, 0),     # кусты - замедляют
    ("timber", 20, (140, 60), True, 0, 0),     # брёвна - твердые
    ("tree", 20, (100, 120), True, 0, 0),      # деревья - твердые
    ("cristal", 10, (80, 100), False, 10, 0.5),  # кристаллы - не твердые, наносят урон
]

# Stage settings
STAGE_PLAY_AREA_MARGIN = 100  # отступ от краев экрана для play area
EXIT_ZONE_SIZE = (150, 150)
EXIT_ZONE_POSITION = "bottom_right"  # где размещать выход

# Fade settings
FADE_SPEED = 2.0  # seconds for full fade
FADE_COLOR = (0, 0, 0)

# Colors
COLOR_FOREST_NORMAL = (34, 139, 34)
COLOR_FOREST_INFECTED = (139, 69, 19)
COLOR_FOREST_BOSS = (50, 20, 50)
COLOR_OBSTACLE_SOLID = (100, 100, 100)
COLOR_EXIT_ZONE = (255, 215, 0)
COLOR_DAMAGE_FLASH = (255, 0, 0)

# Damage settings
DAMAGE_COOLDOWN_DEFAULT = 0.5