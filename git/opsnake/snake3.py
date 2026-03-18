import pygame
import random
import sys

# Snake 3 - Variant met wrap-edges, speed boost apple en extra visual

pygame.init()

SIZE = 32
WIDTH, HEIGHT = 960, 640
BG_COLOR = (15, 18, 26)
SNAKE_COLOR = (50, 240, 170)
APPLE_COLOR = (255, 70, 70)
BOOST_COLOR = (70, 145, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake 3 - Variant")
clock = pygame.time.Clock()

font_small = pygame.font.SysFont("consolas", 24)
font_big = pygame.font.SysFont("consolas", 60)

class Snake:
    def __init__(self):
        self.body = [(5 * SIZE, 5 * SIZE), (4 * SIZE, 5 * SIZE), (3 * SIZE, 5 * SIZE)]
        self.direction = "right"

    def move(self):
        x, y = self.body[0]
        if self.direction == "left":
            x -= SIZE
        elif self.direction == "right":
            x += SIZE
        elif self.direction == "up":
            y -= SIZE
        elif self.direction == "down":
            y += SIZE

        x %= WIDTH
        y %= HEIGHT

        self.body.insert(0, (x, y))
        self.body.pop()

    def grow(self):
        self.body.append(self.body[-1])

    def head(self):
        return self.body[0]

    def hit_self(self):
        return self.head() in self.body[1:]

    def draw(self):
        for index, (x, y) in enumerate(self.body):
            size = SIZE - (index // 5) if (SIZE - (index // 5)) > 10 else 10
            rect = pygame.Rect(x + (SIZE - size) // 2, y + (SIZE - size) // 2, size, size)
            alpha = max(40, 255 - index * 6)
            surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            surf.fill((*SNAKE_COLOR, alpha))
            screen.blit(surf, (rect.x, rect.y))

class Apple:
    def __init__(self, snake_body):
        self.position = self.random_pos(snake_body)
        self.is_boost = random.random() < 0.2

    def random_pos(self, occupied):
        while True:
            pos = (random.randrange(0, WIDTH, SIZE), random.randrange(0, HEIGHT, SIZE))
            if pos not in occupied:
                return pos

    def draw(self):
        color = BOOST_COLOR if self.is_boost else APPLE_COLOR
        x, y = self.position
        pygame.draw.rect(screen, color, (x + 4, y + 4, SIZE - 8, SIZE - 8), border_radius=8)

def draw_text(text, size, color, x, y):
    surf = pygame.font.SysFont("consolas", size, bold=True).render(text, True, color)
    screen.blit(surf, (x, y))


def main():
    snake = Snake()
    apple = Apple(snake.body)
    score = 0
    speed = 8
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_UP and snake.direction != "down":
                    snake.direction = "up"
                elif event.key == pygame.K_DOWN and snake.direction != "up":
                    snake.direction = "down"
                elif event.key == pygame.K_LEFT and snake.direction != "right":
                    snake.direction = "left"
                elif event.key == pygame.K_RIGHT and snake.direction != "left":
                    snake.direction = "right"
                if event.key == pygame.K_r and game_over:
                    return main()

        if not game_over:
            snake.move()

            if snake.head() == apple.position:
                snake.grow()
                score += 2 if apple.is_boost else 1
                if apple.is_boost:
                    speed = min(25, speed + 2)
                else:
                    speed = min(25, speed + 1)
                apple = Apple(snake.body)

            if snake.hit_self():
                game_over = True

        screen.fill(BG_COLOR)
        snake.draw()
        apple.draw()

        draw_text(f"Score: {score}", 24, (220, 220, 220), 10, 10)
        draw_text(f"Speed: {speed}", 24, (220, 220, 220), 10, 40)

        if game_over:
            draw_text("GAME OVER", 60, (255, 100, 100), WIDTH // 2 - 180, HEIGHT // 2 - 60)
            draw_text("Press R to restart", 30, (200, 200, 200), WIDTH // 2 - 130, HEIGHT // 2 + 20)

        pygame.display.flip()
        clock.tick(speed)


if __name__ == "__main__":
    main()
