import pygame
import time
import json
import os
from collections import deque

from game.maze import generate_maze, CELL
from game.player import Player


FPS = 60

BG = (240, 235, 220)
WALL_COLOR = (40, 40, 60)
EXIT_COLOR = (80, 200, 80)
HINT_COLOR = (255, 215, 0)
FOG_COLOR = (10, 10, 15)

HUD_HEIGHT = 60

LEADERBOARD_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "leaderboard.json"
)


class GameEngine:
    def __init__(self):
        pygame.init()

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(
            "monospace",
            22
        )

        self.big_font = pygame.font.SysFont(
            "monospace",
            36,
            bold=True
        )

        # Difficulty settings
        self.difficulties = {
            "Easy": (10, 8),
            "Medium": (15, 13),
            "Hard": (20, 18)
        }

        self.difficulty = None
        self.cols = None
        self.rows = None

        self.screen = None

        self.load_leaderboard()

        # Select difficulty before starting the game
        self.select_difficulty()

        self.reset()

    # ---------------------------------------------------------
    # DIFFICULTY SELECTION
    # ---------------------------------------------------------

    def select_difficulty(self):
        selecting = True

        while selecting:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_1:
                        self.difficulty = "Easy"
                        selecting = False

                    elif event.key == pygame.K_2:
                        self.difficulty = "Medium"
                        selecting = False

                    elif event.key == pygame.K_3:
                        self.difficulty = "Hard"
                        selecting = False

            if self.screen is None:
                self.screen = pygame.display.set_mode(
                    (700, 400)
                )

            self.screen.fill(
                BG
            )

            title = self.big_font.render(
                "MAZE RUNNER",
                True,
                (30, 30, 50)
            )

            self.screen.blit(
                title,
                (
                    self.screen.get_width() // 2
                    - title.get_width() // 2,
                    50
                )
            )

            instruction = self.font.render(
                "Select Difficulty",
                True,
                (50, 50, 70)
            )

            self.screen.blit(
                instruction,
                (
                    self.screen.get_width() // 2
                    - instruction.get_width() // 2,
                    120
                )
            )

            easy = self.font.render(
                "1 - Easy     10 x 8",
                True,
                (50, 50, 70)
            )

            medium = self.font.render(
                "2 - Medium   15 x 13",
                True,
                (50, 50, 70)
            )

            hard = self.font.render(
                "3 - Hard     20 x 18",
                True,
                (50, 50, 70)
            )

            self.screen.blit(
                easy,
                (
                    self.screen.get_width() // 2
                    - easy.get_width() // 2,
                    180
                )
            )

            self.screen.blit(
                medium,
                (
                    self.screen.get_width() // 2
                    - medium.get_width() // 2,
                    220
                )
            )

            self.screen.blit(
                hard,
                (
                    self.screen.get_width() // 2
                    - hard.get_width() // 2,
                    260
                )
            )

            pygame.display.flip()

            self.clock.tick(FPS)

        self.cols, self.rows = self.difficulties[
            self.difficulty
        ]

        self.resize_window()

    # ---------------------------------------------------------
    # WINDOW SIZE
    # ---------------------------------------------------------

    def resize_window(self):
        width = self.cols * CELL
        height = self.rows * CELL + HUD_HEIGHT

        self.screen = pygame.display.set_mode(
            (width, height)
        )

        pygame.display.set_caption(
            f"Maze Runner - {self.difficulty}"
        )

    # ---------------------------------------------------------
    # TASK 3: LEADERBOARD
    # ---------------------------------------------------------

    def load_leaderboard(self):
        if not os.path.exists(LEADERBOARD_FILE):
            self.leaderboard = []
            return

        try:
            with open(LEADERBOARD_FILE, "r") as file:
                data = json.load(file)

            if isinstance(data, list):
                self.leaderboard = data
            else:
                self.leaderboard = []

        except (json.JSONDecodeError, OSError):
            self.leaderboard = []

    def save_leaderboard(self):
        try:
            with open(LEADERBOARD_FILE, "w") as file:
                json.dump(
                    self.leaderboard,
                    file,
                    indent=4
                )

        except OSError:
            pass

    def add_completion_time(self):
        self.leaderboard.append(
            round(self.elapsed, 2)
        )

        self.leaderboard.sort()

        self.leaderboard = self.leaderboard[:5]

        self.save_leaderboard()

    # ---------------------------------------------------------
    # RESET
    # ---------------------------------------------------------

    def reset(self):
        # Generate a new maze using the currently
        # selected difficulty.
        self.walls = generate_maze(
            self.cols,
            self.rows
        )

        self.player = Player(0, 0)

        self.exit_rect = pygame.Rect(
            (self.cols - 1) * CELL + 5,
            (self.rows - 1) * CELL + 5,
            CELL - 10,
            CELL - 10
        )

        self.start_time = time.time()
        self.elapsed = 0
        self.won = False

        # Task 1: BFS hint
        self.show_hint = False

    # ---------------------------------------------------------
    # EVENTS
    # ---------------------------------------------------------

    def handle_events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:

                # R = New maze of same difficulty
                if event.key == pygame.K_r:
                    self.reset()

                # H = Toggle BFS hint
                if event.key == pygame.K_h:
                    self.show_hint = not self.show_hint

        return True

    # ---------------------------------------------------------
    # TASK 1: EXACT TWO-SIDED BFS WALL CHECK
    # ---------------------------------------------------------

    def get_player_cell(self):
        center_x = self.player.rect.centerx
        center_y = self.player.rect.centery

        c = center_x // CELL
        r = center_y // CELL

        return r, c

    def get_shortest_path(self):
        start = self.get_player_cell()
        target = (
            self.rows - 1,
            self.cols - 1
        )

        queue = deque([start])
        previous = {start: None}

        # N, S, E, W
        directions = [
            (-1, 0, 0, 1),
            (1, 0, 1, 0),
            (0, 1, 2, 3),
            (0, -1, 3, 2)
        ]

        while queue:
            current = queue.popleft()
            r, c = current

            if current == target:
                break

            for dr, dc, wall_dir, opposite_dir in directions:
                nr = r + dr
                nc = c + dc

                if not (
                    0 <= nr < self.rows
                    and 0 <= nc < self.cols
                ):
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

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------

    def update(self):
        if self.won:
            return

        keys = pygame.key.get_pressed()

        self.player.move(
            keys,
            self.walls,
            self.rows,
            self.cols
        )

        self.elapsed = time.time() - self.start_time

        if self.player.rect.colliderect(
            self.exit_rect
        ):

            self.elapsed = (
                time.time() - self.start_time
            )

            self.won = True

            # Task 3
            self.add_completion_time()

    # ---------------------------------------------------------
    # DRAW MAZE
    # ---------------------------------------------------------

    def draw_maze(self):
        wall_w = 3

        for r in range(self.rows):
            for c in range(self.cols):

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

    # ---------------------------------------------------------
    # TASK 1: DRAW BFS HINT
    # ---------------------------------------------------------

    def draw_hint(self):
        if not self.show_hint or self.won:
            return

        path = self.get_shortest_path()

        for r, c in path:

            x = c * CELL
            y = r * CELL

            marker = pygame.Rect(
                x + CELL // 2 - 7,
                y + CELL // 2 - 7,
                14,
                14
            )

            pygame.draw.circle(
                self.screen,
                HINT_COLOR,
                marker.center,
                7
            )

    # ---------------------------------------------------------
    # TASK 2: FOG OF WAR
    # ---------------------------------------------------------

    def draw_fog(self):
        player_r, player_c = self.get_player_cell()

        radius = 3

        fog = pygame.Surface(
            (
                self.cols * CELL,
                self.rows * CELL
            ),
            pygame.SRCALPHA
        )

        # Everything starts as opaque fog.
        fog.fill(
            (
                FOG_COLOR[0],
                FOG_COLOR[1],
                FOG_COLOR[2],
                255
            )
        )

        # Cells inside radius 3 are transparent.
        for r in range(self.rows):
            for c in range(self.cols):

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

        self.screen.blit(
            fog,
            (0, 0)
        )

    # ---------------------------------------------------------
    # TASK 3: DRAW LEADERBOARD
    # ---------------------------------------------------------

    def draw_leaderboard(self):

        title = self.font.render(
            "TOP 5 TIMES",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            title,
            (
                self.cols * CELL // 2
                - title.get_width() // 2,
                self.rows * CELL // 2 + 65
            )
        )

        if not self.leaderboard:

            empty = self.font.render(
                "No completed runs yet",
                True,
                (200, 200, 200)
            )

            self.screen.blit(
                empty,
                (
                    self.cols * CELL // 2
                    - empty.get_width() // 2,
                    self.rows * CELL // 2 + 100
                )
            )

            return

        for index, score in enumerate(
            self.leaderboard,
            start=1
        ):

            score_text = self.font.render(
                f"{index}. {score:.2f}s",
                True,
                (255, 255, 255)
            )

            self.screen.blit(
                score_text,
                (
                    self.cols * CELL // 2
                    - score_text.get_width() // 2,
                    self.rows * CELL // 2
                    + 100
                    + (index - 1) * 28
                )
            )

    # ---------------------------------------------------------
    # DRAW EVERYTHING
    # ---------------------------------------------------------

    def draw(self):

        self.screen.fill(BG)

        # 1. Draw complete maze
        self.draw_maze()

        # 2. Draw BFS hint
        self.draw_hint()

        # 3. Draw exit
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

        # 4. Draw transparent fog
        self.draw_fog()

        # 5. Draw player LAST
        self.player.draw(
            self.screen
        )

        # -----------------------------------------------------
        # HUD
        # -----------------------------------------------------

        hud = pygame.Rect(
            0,
            self.rows * CELL,
            self.cols * CELL,
            HUD_HEIGHT
        )

        pygame.draw.rect(
            self.screen,
            (30, 30, 50),
            hud
        )

        time_surf = self.font.render(
            f"Time: {self.elapsed:.1f}s   "
            f"R = New Maze   H = Hint",
            True,
            (200, 200, 200)
        )

        self.screen.blit(
            time_surf,
            (
                10,
                self.rows * CELL + 18
            )
        )

        # -----------------------------------------------------
        # WIN SCREEN
        # -----------------------------------------------------

        if self.won:

            overlay = pygame.Surface(
                (
                    self.cols * CELL,
                    self.rows * CELL
                ),
                pygame.SRCALPHA
            )

            overlay.fill(
                (0, 0, 0, 160)
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

            self.screen.blit(
                msg,
                (
                    self.cols * CELL // 2
                    - msg.get_width() // 2,
                    30
                )
            )

            self.draw_leaderboard()

            sub = self.font.render(
                "Press R for a new maze",
                True,
                (200, 200, 200)
            )

            self.screen.blit(
                sub,
                (
                    self.cols * CELL // 2
                    - sub.get_width() // 2,
                    self.rows * CELL - 35
                )
            )

        pygame.display.flip()

    # ---------------------------------------------------------
    # MAIN GAME LOOP
    # ---------------------------------------------------------

    def run(self):

        running = True

        while running:

            running = self.handle_events()

            self.update()

            self.draw()

            self.clock.tick(FPS)

        pygame.quit()