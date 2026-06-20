import heapq

import pygame


class Pathfinder:
    """Ищет кратчайший путь по сетке с помощью алгоритма A*."""
    def __init__(self, stage, cell_size=40, agent_size=(40, 40)):
        self.stage = stage
        self.cell_size = cell_size
        self.agent_size = agent_size
        self.grid = set()
        self.cols = 0
        self.rows = 0
        self.build_grid()

    def build_grid(self, blocked_rects=None):
        blocked_rects = blocked_rects or []
        play_area = self.stage.play_area
        self.cols = play_area.width // self.cell_size
        self.rows = play_area.height // self.cell_size
        self.grid = set()

        obstacle_rects = [
            obstacle.rect
            for obstacle in self.stage.obstacles
            if obstacle.is_solid or obstacle.deals_damage()
        ]
        obstacle_rects.extend(blocked_rects)

        for row in range(self.rows):
            for col in range(self.cols):
                agent_rect = pygame.Rect(
                    0,
                    0,
                    self.agent_size[0],
                    self.agent_size[1]
                )
                agent_rect.center = self._grid_to_world((col, row))

                blocked = not play_area.contains(agent_rect)
                for rect in obstacle_rects:
                    if agent_rect.colliderect(rect):
                        blocked = True
                        break

                if not blocked:
                    self.grid.add((col, row))

    def find_path(self, start_pos, target_pos, blocked_rects=None):
        """Находит кратчайший путь между точками с помощью алгоритма A*.

        Args:
            start_pos: Начальная позиция в мировых координатах.
            target_pos: Целевая позиция в мировых координатах.
            blocked_rects: Дополнительные прямоугольные области, недоступные
                для перемещения.

        Returns:
            Список точек пути в мировых координатах. Если путь построить
            невозможно, возвращается пустой список.
        """
        self.build_grid(blocked_rects)

        start = self._world_to_grid(start_pos)
        target = self._world_to_grid(target_pos)

        if start not in self.grid or target not in self.grid:
            start = self._nearest_walkable_cell(start)
            target = self._nearest_walkable_cell(target)

        if start is None or target is None:
            return []

        open_heap = []
        heapq.heappush(open_heap, (0, start))

        came_from = {}
        g_score = {start: 0}
        open_set = {start}

        while open_heap:
            current = heapq.heappop(open_heap)[1]
            open_set.discard(current)

            if current == target:
                return self._reconstruct_path(came_from, current)

            for neighbor in self.get_neighbors(current):
                tentative_g_score = g_score[current] + 1

                if tentative_g_score < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + self._heuristic(neighbor, target)

                    if neighbor not in open_set:
                        heapq.heappush(open_heap, (f_score, neighbor))
                        open_set.add(neighbor)

        return []

    def get_neighbors(self, cell):
        col, row = cell
        neighbors = [
            (col + 1, row),
            (col - 1, row),
            (col, row + 1),
            (col, row - 1),
        ]

        return [
            neighbor
            for neighbor in neighbors
            if neighbor in self.grid
        ]

    def _heuristic(self, cell, target):
        return abs(cell[0] - target[0]) + abs(cell[1] - target[1])

    def _nearest_walkable_cell(self, cell):
        if cell in self.grid:
            return cell

        best_cell = None
        best_distance = float("inf")

        for walkable_cell in self.grid:
            distance = self._heuristic(cell, walkable_cell)
            if distance < best_distance:
                best_cell = walkable_cell
                best_distance = distance

        return best_cell

    def _world_to_grid(self, pos):
        play_area = self.stage.play_area
        x = max(play_area.left, min(pos[0], play_area.right - 1))
        y = max(play_area.top, min(pos[1], play_area.bottom - 1))
        col = int((x - play_area.left) // self.cell_size)
        row = int((y - play_area.top) // self.cell_size)
        return col, row

    def _grid_to_world(self, cell):
        play_area = self.stage.play_area
        return pygame.Vector2(
            play_area.left + cell[0] * self.cell_size + self.cell_size // 2,
            play_area.top + cell[1] * self.cell_size + self.cell_size // 2
        )

    def _reconstruct_path(self, came_from, current):
        path = [self._grid_to_world(current)]

        while current in came_from:
            current = came_from[current]
            path.append(self._grid_to_world(current))

        path.reverse()
        return path
