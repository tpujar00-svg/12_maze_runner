import pygame
import time
from collections import deque
from game.maze import generate_maze, CELL
from game.player import Player

FPS = 60

BG = (240, 235, 220)
WALL_COLOR = (40, 40, 60)
EXIT_COLOR = (80, 200, 80)
HINT_COLOR = (255, 215, 0)
FOG_COLOR = (15, 15, 25)

COLS, ROWS = 15, 13

WIDTH = COLS * CELL
HEIGHT = ROWS * CELL + 60


class GameEngine:

    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Maze Runner")

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("monospace", 22)
        self.big_font = pygame.font.SysFont(
            "monospace",
            36,
            bold=True
        )

        self.reset()

    def reset(self):
        self.walls = generate_maze(COLS, ROWS)

        self.player = Player(0, 0)

        self.exit_rect = pygame.Rect(
            (COLS - 1) * CELL + 5,
            (ROWS - 1) * CELL + 5,
            CELL - 10,
            CELL - 10
        )

        self.start_time = time.time()
        self.elapsed = 0
        self.won = False

        self.show_hint = False

    def handle_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:
                    self.reset()

                if event.key == pygame.K_h:
                    self.show_hint = not self.show_hint

        return True

    def get_player_cell(self):

        center_x = self.player.rect.centerx
        center_y = self.player.rect.centery

        c = center_x // CELL
        r = center_y // CELL

        return r, c

    def get_shortest_path(self):

        start = self.get_player_cell()
        target = (ROWS - 1, COLS - 1)

        queue = deque([start])
        previous = {start: None}

        directions = [
            (-1, 0, 0, 1),
            (1, 0, 1, 0),
            (0, 1, 2, 3),
            (0, -1, 3, 2)
        ]

        while queue:

            current = queue.popleft()

            if current == target:
                break

            r, c = current

            for dr, dc, wall_dir, opposite_dir in directions:

                nr = r + dr
                nc = c + dc

                if not (0 <= nr < ROWS and 0 <= nc < COLS):
                    continue

                if self.walls[r][c][wall_dir]:
                    continue

                if self.walls[nr][nc][opposite_dir]:
                    continue

                neighbour = (nr, nc)

                if neighbour not in previous:
                    previous[neighbour] = current
                    queue.append(neighbour)

        if target not in previous:
            return []

        path = []
        current = target

        while current is not None:
            path.append(current)
            current = previous[current]

        path.reverse()

        return path

    def update(self):

        if self.won:
            return

        keys = pygame.key.get_pressed()

        self.player.move(
            keys,
            self.walls,
            ROWS,
            COLS
        )

        self.elapsed = time.time() - self.start_time

        if self.player.rect.colliderect(self.exit_rect):
            self.won = True

    def draw_maze(self):

        wall_w = 3

        for r in range(ROWS):

            for c in range(COLS):

                x = c * CELL
                y = r * CELL

                w = self.walls[r][c]

                if w[0]:
                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x, y),
                        (x + CELL, y),
                        wall_w
                    )

                if w[1]:
                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x, y + CELL),
                        (x + CELL, y + CELL),
                        wall_w
                    )

                if w[2]:
                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x + CELL, y),
                        (x + CELL, y + CELL),
                        wall_w
                    )

                if w[3]:
                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x, y),
                        (x, y + CELL),
                        wall_w
                    )

    def draw_hint(self):

        if not self.show_hint:
            return

        if self.won:
            return

        path = self.get_shortest_path()

        for r, c in path:

            x = c * CELL
            y = r * CELL

            center = (
                x + CELL // 2,
                y + CELL // 2
            )

            pygame.draw.circle(
                self.screen,
                HINT_COLOR,
                center,
                7
            )

    def draw_fog(self):

        player_r, player_c = self.get_player_cell()

        radius = 3

        fog = pygame.Surface(
            (WIDTH, ROWS * CELL),
            pygame.SRCALPHA
        )

        fog.fill(
            (15, 15, 25, 230)
        )

        for r in range(ROWS):

            for c in range(COLS):

                distance = max(
                    abs(r - player_r),
                    abs(c - player_c)
                )

                if distance <= radius:

                    cell_rect = pygame.Rect(
                        c * CELL,
                        r * CELL,
                        CELL,
                        CELL
                    )

                    fog.fill(
                        (0, 0, 0, 0),
                        cell_rect
                    )

        self.screen.blit(fog, (0, 0))

    def draw(self):

        self.screen.fill(BG)

        self.draw_maze()

        self.draw_hint()

        pygame.draw.rect(
            self.screen,
            EXIT_COLOR,
            self.exit_rect,
            border_radius=4
        )

        ex_label = self.font.render(
            "EXIT",
            True,
            (20, 80, 20)
        )

        self.screen.blit(
            ex_label,
            (
                self.exit_rect.x + 2,
                self.exit_rect.y + 4
            )
        )

        self.player.draw(self.screen)

        # Task 2: Fog of War
        self.draw_fog()

        hud = pygame.Rect(
            0,
            ROWS * CELL,
            WIDTH,
            60
        )

        pygame.draw.rect(
            self.screen,
            (30, 30, 50),
            hud
        )

        time_surf = self.font.render(
            f"Time: {self.elapsed:.1f}s   R = New Maze   H = Hint",
            True,
            (200, 200, 200)
        )

        self.screen.blit(
            time_surf,
            (
                10,
                ROWS * CELL + 18
            )
        )

        if self.won:

            overlay = pygame.Surface(
                (WIDTH, ROWS * CELL),
                pygame.SRCALPHA
            )

            overlay.fill(
                (0, 0, 0, 120)
            )

            self.screen.blit(
                overlay,
                (0, 0)
            )

            msg = self.big_font.render(
                f"Solved in {self.elapsed:.1f}s!",
                True,
                (80, 240, 80)
            )

            sub = self.font.render(
                "Press R for a new maze",
                True,
                (200, 200, 200)
            )

            self.screen.blit(
                msg,
                (
                    WIDTH // 2 - msg.get_width() // 2,
                    ROWS * CELL // 2 - 30
                )
            )

            self.screen.blit(
                sub,
                (
                    WIDTH // 2 - sub.get_width() // 2,
                    ROWS * CELL // 2 + 20
                )
            )

        pygame.display.flip()

    def run(self):

        running = True

        while running:

            running = self.handle_events()

            self.update()

            self.draw()

            self.clock.tick(FPS)

        pygame.quit()