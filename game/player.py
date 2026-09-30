import pygame
from game.maze import CELL

SPEED = 3

class Player:
    def __init__(self, r, c):
        self.r = r
        self.c = c
        x = c * CELL + CELL // 2
        y = r * CELL + CELL // 2
        self.rect = pygame.Rect(x - 10, y - 10, 20, 20)
        self.color = (60, 120, 220)

    def move(self, keys, walls, rows, cols):
        dx, dy = 0, 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = SPEED

        # Wall-aware movement
        new_rect = self.rect.move(dx, 0)
        if not self._hits_wall(new_rect, walls, rows, cols):
            self.rect = new_rect

        new_rect = self.rect.move(0, dy)
        if not self._hits_wall(new_rect, walls, rows, cols):
            self.rect = new_rect

    def _hits_wall(self, rect, walls, rows, cols):
        # Check overall maze boundaries
        if rect.left < 0 or rect.right > cols * CELL:
            return True

        if rect.top < 0 or rect.bottom > rows * CELL:
            return True

        # Current cell based on player's center
        current_c = self.rect.centerx // CELL
        current_r = self.rect.centery // CELL

        # Moving right: check East wall
        if rect.right > (current_c + 1) * CELL:
            if current_c < cols and walls[current_r][current_c][2]:
                return True

        # Moving left: check West wall
        if rect.left < current_c * CELL:
            if current_c >= 0 and walls[current_r][current_c][3]:
                return True

        # Moving down: check South wall
        if rect.bottom > (current_r + 1) * CELL:
            if current_r < rows and walls[current_r][current_c][1]:
                return True

        # Moving up: check North wall
        if rect.top < current_r * CELL:
            if current_r >= 0 and walls[current_r][current_c][0]:
                return True

        return False

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)