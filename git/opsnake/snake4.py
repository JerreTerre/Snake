import pygame
import random
import sys

# Snake 4 - Variant bovenop snake2:
#  - tunnels (linker/rechter rand teleport) in plaats van muur-dood
#  - verplaatsende obstakels
#  - timer survival score

pygame.init()

SIZE = 30
WIDTH, HEIGHT = 900, 600
BG_COLOR = (18, 20, 31)
SNAKE_COLOR = (0, 210, 255)
APPLE_COLOR = (255, 100, 90)
OBSTACLE_COLOR = (160, 70, 20)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake 4 - Tunnel Survival")
clock = pygame.time.Clock()

font_small = pygame.font.SysFont("Arial", 22)
font_big = pygame.font.SysFont("Arial", 58)

class Snake:
    def __init__(self):
        self.body = [(10 * SIZE, 10 * SIZE), (9 * SIZE, 10 * SIZE), (8 * SIZE, 10 * SIZE)]
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

        # Tunnel effect links/rechts
        if x < 0:
            x = WIDTH - SIZE
        elif x >= WIDTH:
            x = 0

        # Tunnel effect boven/onder
        if y < 0:
            y = HEIGHT - SIZE
        elif y >= HEIGHT:
            y = 0

        self.body.insert(0, (x, y))
        self.body.pop()

    def grow(self):
        self.body.append(self.body[-1])

    def head(self):
        return self.body[0]

    def hit_self(self):
        return self.head() in self.body[1:]

    def draw(self):
        for part in self.body:
            pygame.draw.rect(screen, SNAKE_COLOR, (*part, SIZE, SIZE))

class Apple:
    def __init__(self, snake_body, obstacles):
        self.position = self.random_pos(snake_body, obstacles)

    def random_pos(self, snake_body, obstacles):
        while True:
            pos = (random.randrange(0, WIDTH, SIZE), random.randrange(0, HEIGHT, SIZE))
            if pos not in snake_body and pos not in obstacles:
                return pos

    def draw(self):
        x, y = self.position
        pygame.draw.rect(screen, APPLE_COLOR, (x+4, y+4, SIZE-8, SIZE-8), border_radius=6)

class Obstacles:
    def __init__(self, count):
        self.positions = [self.random_pos([]) for _ in range(count)]
        self.direction = 1

    def random_pos(self, avoid):
        while True:
            pos = (random.randrange(0, WIDTH, SIZE), random.randrange(0, HEIGHT, SIZE))
            if pos not in avoid:
                return pos

    def move(self):
        # horizontale pendelbeweging voor obstakels in plaatselijke lijnen
        new_positions = []
        for x, y in self.positions:
            x += SIZE * self.direction
            if x < 0:
                x = WIDTH - SIZE
            elif x >= WIDTH:
                x = 0
            new_positions.append((x, y))
        self.positions = new_positions

    def draw(self):
        for x, y in self.positions:
            pygame.draw.rect(screen, OBSTACLE_COLOR, (x, y, SIZE, SIZE))


def draw_text(msg, font, color, x, y):
    screen.blit(font.render(msg, True, color), (x, y))


def main():
    snake = Snake()
    obstacles = Obstacles(8)
    apple = Apple(snake.body, obstacles.positions)
    score = 0
    timer = 0
    speed = 9
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
            obstacles.move()
            timer += 1
            if timer % 20 == 0:
                score += 1

            if snake.head() == apple.position:
                snake.grow()
                score += 10
                apple = Apple(snake.body, obstacles.positions)
                if score % 50 == 0 and speed < 20:
                    speed += 1

            if snake.hit_self() or snake.head() in obstacles.positions:
                game_over = True

        screen.fill(BG_COLOR)
        snake.draw()
        obstacles.draw()
        apple.draw()

        draw_text(f"Score: {score}", font_small, (240, 240, 240), 10, 10)
        draw_text(f"Time: {timer//60}s", font_small, (240, 240, 240), 10, 35)

        if game_over:
            draw_text("GAME OVER", font_big, (255, 120, 120), WIDTH//2 - 180, HEIGHT//2 - 60)
            draw_text("Press R to restart", font_small, (220, 220, 220), WIDTH//2 - 110, HEIGHT//2 + 20)

        pygame.display.flip()
        clock.tick(speed)


if __name__ == "__main__":
    main()
