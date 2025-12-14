from __future__ import annotations

from dataclasses import dataclass
from random import choice
from typing import List, Optional, Tuple

import pygame

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 20

GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

Position = Tuple[int, int]
Direction = Tuple[int, int]


def to_pixel(cell: Position) -> Position:
    """Convert grid cell coordinates (x, y) to pixel coordinates."""
    return cell[0] * GRID_SIZE, cell[1] * GRID_SIZE


@dataclass
class GameObject:
    """Base game object that has a position and a body color.

    The draw() method is a stub here and must be overridden in subclasses.
    """

    position: Position
    body_color: Tuple[int, int, int]

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the object on the surface."""
        pass


class Apple(GameObject):
    """Apple that appears in a random free cell."""

    def __init__(self, occupied: Optional[set[Position]] = None):
        super().__init__(position=(0, 0), body_color=RED)
        self.randomize_position(occupied=occupied)

    def randomize_position(
        self,
        occupied: Optional[set[Position]] = None,
    ) -> None:
        """Pick a random position not occupied by the snake."""
        occupied = occupied or set()
        all_cells = {
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
        }
        free_cells = tuple(all_cells - occupied)
        self.position = choice(free_cells) if free_cells else (0, 0)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the apple as a filled 1-cell rectangle."""
        pygame.draw.rect(
            surface,
            self.body_color,
            (*to_pixel(self.position), GRID_SIZE, GRID_SIZE),
        )


class Snake(GameObject):
    """Snake that moves on the grid and grows after eating an apple."""

    def __init__(self):
        start = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
        super().__init__(position=start, body_color=GREEN)
        self.positions: List[Position] = [start]
        self.length = 1
        self.direction: Direction = (1, 0)
        self.next_direction: Optional[Direction] = None

    def get_head_position(self) -> Position:
        """Return the snake head position."""
        return self.positions[0]

    def update_direction(self) -> None:
        """Apply next_direction if it was set by key handling."""
        if self.next_direction is not None:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Move the snake by one cell with wrap-around."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        new_head = (
            (head_x + dx) % GRID_WIDTH,
            (head_y + dy) % GRID_HEIGHT,
        )
        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.positions.pop()

    def reset(self) -> None:
        """Reset the snake to its initial state."""
        start = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.positions = [start]
        self.length = 1
        self.direction = (1, 0)
        self.next_direction = None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the snake segments."""
        for cell in self.positions:
            pygame.draw.rect(
                surface,
                self.body_color,
                (*to_pixel(cell), GRID_SIZE, GRID_SIZE),
            )


def handle_keys(snake: Snake, event: pygame.event.Event) -> None:
    """Handle arrow keys and update snake.next_direction."""
    if event.type != pygame.KEYDOWN:
        return

    opposites = {
        (1, 0): (-1, 0),
        (-1, 0): (1, 0),
        (0, 1): (0, -1),
        (0, -1): (0, 1),
    }
    mapping = {
        pygame.K_UP: (0, -1),
        pygame.K_DOWN: (0, 1),
        pygame.K_LEFT: (-1, 0),
        pygame.K_RIGHT: (1, 0),
    }

    new_dir = mapping.get(event.key)
    if new_dir and opposites[snake.direction] != new_dir:
        snake.next_direction = new_dir


def main() -> None:
    """Run the game loop."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Изгиб Питона')
    clock = pygame.time.Clock()

    snake = Snake()
    apple = Apple(occupied=set(snake.positions))

    running = True
    while running:
        clock.tick(20)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            else:
                handle_keys(snake, event)

        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(occupied=set(snake.positions))

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(occupied=set(snake.positions))

        screen.fill(BLACK)
        apple.draw(screen)
        snake.draw(screen)
        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()
