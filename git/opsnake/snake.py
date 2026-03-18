# Snake Plus - Bewerking met extra functionaliteit en examenvoorbereiding
#
# Dit Python-programma gebruikt pygame om een klassieke Snake-game te draaien.
# Heldere spelstatussen: MENU, PLAYING, GAMEOVER.
# 
# Gedurende het spel:
# - De slang beweegt met pijltjestoetsen en joystick (optioneel)
# - Appels verschijnen willekeurig op het grid, maar nooit op obstakels
# - Bij het eten van een appel groeit de slang en stijgt de score
# - Bij botsing met de eigen staart, obstakel of windowrand is GAME OVER
# - Score en high score worden getoond, plus pausestand (P toets)

import pygame
import random
import sys

pygame.init()
pygame.mixer.init()

SIZE = 40
WIDTH, HEIGHT = 1600, 800
BG_COLOR = (34, 49,  33)
FPS = 10

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Plus")

clock = pygame.time.Clock()

pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
for j in joysticks:
    j.init()

apple_sound = pygame.mixer.Sound("git/opsnake/images/apple.mp3")
death_sound = pygame.mixer.Sound("git/opsnake/images/dood.mp3")
pygame.mixer.music.load("git/opsnake/images/achtergrondmuziek.mp3")
pygame.mixer.music.play(-1)


def grid_random():
    return random.randint(0, (WIDTH // SIZE) - 1) * SIZE, random.randint(0, (HEIGHT // SIZE) - 1) * SIZE


class Apple:
    """Appelklasse: beheert appelpositie en weergave."""
    def __init__(self, obstacle_positions):
        # Laad appel-afbeelding, schaal naar blokgrootte en zet de eerste positie
        self.image = pygame.image.load("git/opsnake/images/apple.jpg").convert_alpha()
        self.image = pygame.transform.scale(self.image, (SIZE, SIZE))
        self.obstacles = obstacle_positions
        self.move()

    def move(self):
        # Verplaats appel naar willekeurige gridlocatie waar geen obstakel is
        while True:
            self.x, self.y = grid_random()
            if (self.x, self.y) not in self.obstacles:
                break

    def draw(self):
        screen.blit(self.image, (self.x, self.y))


class Obstacle:
    """Obstakelklasse: maakt een set van vaste tegels waar je op kan botsen."""
    def __init__(self, count):
        self.positions = set()
        self.image = pygame.Surface((SIZE, SIZE))
        self.image.fill((139, 69, 19))
        while len(self.positions) < count:
            pos = grid_random()
            self.positions.add(pos)

    def draw(self):
        for pos in self.positions:
            screen.blit(self.image, pos)


class Snake:
    """Slangklasse: beheerst positie, beweging, groei en botsingen."""
    def __init__(self):
        # Laad slangblok-afbeelding, startpositie en richting
        self.image = pygame.image.load("git/opsnake/images/block.jpg").convert_alpha()
        self.image = pygame.transform.scale(self.image, (SIZE, SIZE))
        self.direction = "right"
        self.body = [(SIZE * 5, SIZE * 5)]
        self.grow_pending = 0

    def move(self):
        # Bereken de nieuwe koppositie afhankelijk van richting
        head_x, head_y = self.body[0]
        if self.direction == "right":
            head_x += SIZE
        elif self.direction == "left":
            head_x -= SIZE
        elif self.direction == "up":
            head_y -= SIZE
        elif self.direction == "down":
            head_y += SIZE

        new_head = (head_x, head_y)

        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self):
        self.grow_pending += 1

    def draw(self):
        for part in self.body:
            screen.blit(self.image, part)

    def hit_self(self):
        return self.body[0] in self.body[1:]

    def hit_wall(self):
        x, y = self.body[0]
        return x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT

    def hit_obstacle(self, obstacles):
        return self.body[0] in obstacles


def draw_text(text, size, color, pos):
    font = pygame.font.SysFont("arial", size, bold=True)
    img = font.render(text, True, color)
    screen.blit(img, pos)


def draw_menu():
    screen.fill(BG_COLOR)
    draw_text("SNAKE PLUS", 80, (255, 255, 255), (WIDTH // 2 - 230, 150))
    draw_text("1 - EASY (8 FPS)", 50, (0, 255, 0), (WIDTH // 2 - 220, 300))
    draw_text("2 - MEDIUM (12 FPS)", 50, (255, 235, 0), (WIDTH // 2 - 220, 370))
    draw_text("3 - HARD (18 FPS)", 50, (255, 0, 0), (WIDTH // 2 - 220, 440))
    draw_text("P - Pause / Resume (in-game)", 40, (200, 200, 200), (WIDTH // 2 - 300, 520))
    draw_text("Esc - Quit", 40, (200, 200, 200), (WIDTH // 2 - 120, 580))
    pygame.display.update()


def draw_game_over(score, high_score):
    screen.fill(BG_COLOR)
    draw_text("GAME OVER", 80, (255, 0, 0), (WIDTH // 2 - 210, 250))
    draw_text(f"Score: {score}", 55, (255, 255, 255), (WIDTH // 2 - 140, 360))
    draw_text(f"High Score: {high_score}", 45, (255, 255, 0), (WIDTH // 2 - 170, 440))
    draw_text("R - Restart / M - Menu", 40, (180, 180, 180), (WIDTH // 2 - 240, 540))
    pygame.display.update()


def draw_hud(score, high_score, speed, multiplier):
    draw_text(f"Score: {score}", 30, (255, 255, 255), (20, 10))
    draw_text(f"High: {high_score}", 30, (255, 255, 255), (20, 40))
    draw_text(f"Speed: {speed}", 30, (255, 255, 255), (300, 10))
    draw_text(f"Bonus x{multiplier}", 30, (255, 255, 255), (300, 40))


MENU, PLAYING, GAMEOVER = 0, 1, 2
state = MENU
speed = FPS
pause = False
score = 0
high_score = 0
multiplier = 1

snake = Snake()
obstacle = Obstacle(count=10)
apple = Apple(obstacle.positions)

running = True
while running:
    # Hoofdgame-loop via state-machine.
    # MENU: Toon keuze voor moeilijkheid, start nieuw spel bij toets 1/2/3.
    if state == MENU:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    speed = 8
                    state = PLAYING
                elif event.key == pygame.K_2:
                    speed = 12
                    state = PLAYING
                elif event.key == pygame.K_3:
                    speed = 18
                    state = PLAYING
                # Zet elementen terug naar startniveau bij starten
                if state == PLAYING:
                    snake = Snake()
                    obstacle = Obstacle(count=12)
                    apple = Apple(obstacle.positions)
                    score = 0
                    multiplier = 1
                    pause = False

    elif state == PLAYING:
        # PLAYING staat: verwerk input en beweeg de slang.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False  # Voer meteen exit uit
                if event.key == pygame.K_p:
                    pause = not pause   # Pauze aan/uit
                # Richtingsinput: niet 180° omkeeren
                if event.key == pygame.K_LEFT and snake.direction != "right":
                    snake.direction = "left"
                if event.key == pygame.K_RIGHT and snake.direction != "left":
                    snake.direction = "right"
                if event.key == pygame.K_UP and snake.direction != "down":
                    snake.direction = "up"
                if event.key == pygame.K_DOWN and snake.direction != "up":
                    snake.direction = "down"

        # Joystick input als er een joystick gekoppeld is
        for joystick in joysticks:
            x_axis = joystick.get_axis(0)
            y_axis = joystick.get_axis(1)
            if abs(x_axis) > 0.5:
                snake.direction = "right" if x_axis > 0 else "left"
            if abs(y_axis) > 0.5:
                snake.direction = "down" if y_axis > 0 else "up"

        if not pause:
            snake.move()  # Beweeg slang een stap in huidige richting

# Als slang een appel eet, groeit hij en krijgt score
        if snake.body[0] == (apple.x, apple.y):
            snake.grow()
            apple.move()
            apple_sound.play()
            score_add = 1 * multiplier
            score += score_add
            # Elke 5 punten verhoogt de snelheid
            if score % 5 == 0:
                speed = min(30, speed + 1)
                multiplier += 1
            if score > high_score:
                high_score = score

        # Doodschecks na beweging: eigen lichaam, muur, obstakel
        if snake.hit_self() or snake.hit_wall() or snake.hit_obstacle(obstacle.positions):
            death_sound.play()
            state = GAMEOVER

        screen.fill(BG_COLOR)
        obstacle.draw()
        apple.draw()
        snake.draw()
        draw_hud(score, high_score, speed, multiplier)

        if pause:
            draw_text("PAUSED", 70, (255, 255, 255), (WIDTH // 2 - 110, HEIGHT // 2 - 35))

        pygame.display.update()
        clock.tick(speed)

    elif state == GAMEOVER:
        draw_game_over(score, high_score)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    snake = Snake()
                    obstacle = Obstacle(count=12)
                    apple = Apple(obstacle.positions)
                    score = 0
                    multiplier = 1
                    speed = FPS
                    pause = False
                    state = PLAYING
                if event.key == pygame.K_m:
                    state = MENU

pygame.quit()
sys.exit()