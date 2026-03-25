import pygame
import random
import sys

pygame.init()
pygame.mixer.init()

# =========================
# Setup
# =========================
SIZE = 40
WIDTH, HEIGHT = 1800, 1000
BG_COLOR = (99,167,66)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")

clock = pygame.time.Clock()

# =========================
# Joystick
# =========================
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

for j in joysticks:
    j.init()

# =========================
# Sounds
# =========================
apple_sound = pygame.mixer.Sound("git/opsnake/images/apple.mp3")
death_sound = pygame.mixer.Sound("git/opsnake/images/dood.mp3")

pygame.mixer.music.load("git/opsnake/images/achtergrondmuziek.mp3")
pygame.mixer.music.play(-1)

# =========================
# Classes
# =========================
class Levens:
    def __init__(self):
        self.image= pygame.image.load("git/opsnake/images/hartje.png").convert_alpha()
        self.image=pygame.transform.scale(self.image,(SIZE,SIZE))
        self.x=5
        self.y=5
    def draw(self):
            screen.blit(self.image,(self.x,self.y))   
class Muur:
    def __init__(self):
        self.image= pygame.image.load("git/opsnake/images/muur.png").convert_alpha()
        self.image=pygame.transform.scale(self.image,(SIZE,SIZE))
        self.x=5
        self.y=5
        self.move()
    def move(self):

        self.x = random.randint(0,(WIDTH//SIZE)-1)*SIZE
        self.y = random.randint(0,(HEIGHT//SIZE)-3)*SIZE
    def draw(self):
        for i in range(3):
            screen.blit(self.image,(self.x,self.y+(i*SIZE)))    
class Mine:
    def __init__(self):
        self.image= pygame.image.load("git/opsnake/images/mine.png").convert_alpha()
        self.image=pygame.transform.scale(self.image,(SIZE,SIZE))
        self.x=5
        self.y=5
        self.move()
    def move(self):

        self.x = random.randint(0,(WIDTH//SIZE)-1)*SIZE
        self.y = random.randint(0,(HEIGHT//SIZE)-1)*SIZE
    def draw(self):
        screen.blit(self.image,(self.x,self.y))


class Apple:

    def __init__(self):
        self.image = pygame.image.load("git/opsnake/images/apple.jpg").convert_alpha()
        self.image = pygame.transform.scale(self.image,(SIZE,SIZE))
        self.move()

    def move(self):

        self.x = random.randint(0,(WIDTH//SIZE)-1)*SIZE
        self.y = random.randint(0,(HEIGHT//SIZE)-1)*SIZE

    def draw(self):
        screen.blit(self.image,(self.x,self.y))


class Snake:

    def __init__(self):

        self.image = pygame.image.load("git/opsnake/images/block.jpg").convert_alpha()
        self.image = pygame.transform.scale(self.image,(SIZE,SIZE))

        self.direction = "right"
        self.length = 1

        self.x = [SIZE*5]
        self.y = [SIZE*5]

    def move(self):

        for i in range(self.length-1,0,-1):
            self.x[i] = self.x[i-1]
            self.y[i] = self.y[i-1]

        if self.direction == "right":
            self.x[0]+=SIZE

        if self.direction == "left":
            self.x[0]-=SIZE

        if self.direction == "up":
            self.y[0]-=SIZE

        if self.direction == "down":
            self.y[0]+=SIZE


    def grow(self):

        self.length+=1
        self.x.append(-100)
        self.y.append(-100)


    def draw(self):

        for i in range(self.length):
            screen.blit(self.image,(self.x[i],self.y[i]))


    def check_dead(self):

        if self.x[0] < 0 or self.x[0] >= WIDTH:
            return True

        if self.y[0] < 0 or self.y[0] >= HEIGHT:
            return True

        for i in range(1,self.length):

            if self.x[0] == self.x[i] and self.y[0] == self.y[i]:
                return True

        return False


# =========================
# Functions
# =========================

def draw_score(snake):
    global score

    font = pygame.font.SysFont("arial",30)

    score = font.render("Score: "+str(snake.length-1),True,(255,255,255))

    screen.blit(score,(WIDTH//2-70,10))


def draw_menu():

    screen.fill(BG_COLOR)

    font = pygame.font.SysFont("arial",50)

    title = font.render("Choose Difficulty",True,(255,255,255))

    easy = font.render("1 - EASY",True,(0,255,0))
    medium = font.render("2 - MEDIUM",True,(255,255,0))
    hard = font.render("3 - HARD",True,(255,0,0))

    screen.blit(title,(WIDTH//2-250,200))
    screen.blit(easy,(WIDTH//2-150,350))
    screen.blit(medium,(WIDTH//2-150,450))
    screen.blit(hard,(WIDTH//2-150,550))

    pygame.display.update()


def draw_game_over(score):

    screen.fill(BG_COLOR)

    font = pygame.font.SysFont("arial",60)

    over = font.render("GAME OVER",True,(255,0,0))
    sc = font.render("Score: "+str(score),True,(255,255,255))
    restart = font.render("Press R to Restart",True,(255,255,255))

    screen.blit(over,(WIDTH//2-200,300))
    screen.blit(sc,(WIDTH//2-150,400))
    screen.blit(restart,(WIDTH//2-250,500))

    pygame.display.update()


# =========================
# Game States
# =========================

MENU = 0
PLAYING = 1
GAMEOVER = 2
teller=0
state = MENU
speed = 10
aantal=5
snake = Snake()
apple = Apple()
aantal_levens = 0  # Dit moet een getal zijn voor de logica
levens = []  # Dit is voor de hartjes-objecten
mine=[]
muur=[]
# =========================
# Main Loop
# =========================

running = True

while running:

    if state == MENU:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    aantal, wall ,start_levens= 5, 1,3
                    state = PLAYING
                if event.key == pygame.K_2:
                    aantal, wall,start_levens = 10, 3,2
                    state = PLAYING
                if event.key == pygame.K_3:
                    aantal, wall,start_levens = 20, 6,1
                    state = PLAYING

                if state == PLAYING:
                    aantal_levens=start_levens
                    levens  = [Levens() for _ in range(aantal_levens)]
                    for i, h in enumerate(levens):
                        h.x = 10 + (i * (SIZE + 5))
                        h.y = 10
                    mine = [Mine() for _ in range(aantal)]
                    muur = [Muur() for _ in range(wall)]
                    # Zorg dat de appel direct op een vrije plek start
                    overlap = True
                    while overlap:
                        apple.move()
                        overlap = False
                        for m in mine: 
                            if apple.x == m.x and apple.y == m.y: overlap = True
                        for w in muur:
                            for i in range(3):
                                if apple.x == w.x and apple.y == w.y + (i * SIZE): overlap = True

    elif state == PLAYING:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and snake.direction != "right": snake.direction = "left"
                if event.key == pygame.K_RIGHT and snake.direction != "left": snake.direction = "right"
                if event.key == pygame.K_UP and snake.direction != "down": snake.direction = "up"
                if event.key == pygame.K_DOWN and snake.direction != "up": snake.direction = "down"

        # ... (Joystick logica blijft hetzelfde) ...

        snake.move()

        # Collisions
        for w in muur:
            for i in range(3):
                if snake.x[0] == w.x and snake.y[0] == w.y + (i * SIZE):
                    aantal_levens-=1
                    for m in mine: m.move()
                    for w in muur: w.move()
                    if aantal_levens==0:
                        death_sound.play()
                        state = GAMEOVER
        for m in mine:
 
            if snake.x[0] == m.x and snake.y[0] == m.y :
                aantal_levens-=1
                for m in mine: m.move()
                for w in muur: w.move()
                if aantal_levens==0:
                    death_sound.play()
                    state = GAMEOVER
        
        if snake.x[0] == apple.x and snake.y[0] == apple.y:
            snake.grow()
            apple.move()
            apple_sound.play()
            teller += 1
            if teller == 5:
                for m in mine: m.move()
                teller = 0

        if snake.check_dead():
            death_sound.play()
            state = GAMEOVER

        # Tekenen
        screen.fill(BG_COLOR)
        # Teken muren en mijnen eerst
        for w in muur: w.draw()
        for m in mine: m.draw()
        for i in range(aantal_levens):
            levens[i].draw()
        # Teken de appel als LAATSTE zodat hij bovenop ligt
        apple.draw()
        snake.draw()
        draw_score(snake)
        pygame.display.update()
        clock.tick(speed)

    elif state == GAMEOVER:
        draw_game_over(snake.length-1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # AFSLUITEN MET ESC
                if event.key == pygame.K_ESCAPE:
                    running = False
                # RESTART MET R
                if event.key == pygame.K_r:
                    snake = Snake()
                    apple = Apple()
                    mine = []
                    muur = []
                    teller = 0
                    state = MENU

pygame.quit()
sys.exit()