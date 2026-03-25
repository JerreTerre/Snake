import pygame    # Importeer de Pygame bibliotheek voor game-ontwikkeling
import random    # Voor het genereren van willekeurige getallen (zoals appel-posities)
import sys       # Voor het correct afsluiten van het programma

pygame.init()          # Initialiseer alle Pygame modules
pygame.mixer.init()    # Initialiseer de audio-mixer voor geluidseffecten

# =========================
# Setup
# =========================
SIZE = 40                  # Grootte van één grid-blokje in pixels
WIDTH, HEIGHT = 1600, 800  # Breedte en hoogte van het venster
BG_COLOR = (99,167,66)     # Achtergrondkleur (groen) in RGB

screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Maak het spelvenster aan
pygame.display.set_caption("Snake")                # Zet de titel van het venster

clock = pygame.time.Clock()  # Maak een klok-object om de FPS (snelheid) te beheren

# =========================
# Joystick
# =========================
pygame.joystick.init()  # Initialiseer de joystick module
# Maak een lijst van alle aangesloten joysticks/controllers
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

for j in joysticks:
    j.init()  # Activeer elke aangesloten joystick

# =========================
# Sounds
# =========================
apple_sound = pygame.mixer.Sound("git/opsnake/images/apple.mp3")  # Laad geluid voor appel eten
death_sound = pygame.mixer.Sound("git/opsnake/images/dood.mp3")   # Laad geluid voor afgaan

pygame.mixer.music.load("git/opsnake/images/achtergrondmuziek.mp3")  # Laad achtergrondmuziek
pygame.mixer.music.play(-1)  # Speel muziek oneindig af (-1)

# =========================
# Classes
# =========================
class Muur:
    def __init__(self):
        # Laad muur-afbeelding en maak de achtergrond transparant
        self.image = pygame.image.load("git/opsnake/images/muur.png").convert_alpha()
        # Schaal de afbeelding naar de blokgrootte
        self.image = pygame.transform.scale(self.image,(SIZE,SIZE))
        self.move()  # Zet de muur op een startpositie

    def move(self):
        # Kies een willekeurige grid-positie voor de muur
        self.x = random.randint(0,(WIDTH//SIZE)-1)*SIZE
        self.y = random.randint(0,(HEIGHT//SIZE)-3)*SIZE

    def draw(self):
        # Teken een verticale muur van 3 blokjes hoog
        for i in range(3):
            screen.blit(self.image,(self.x,self.y+(i*SIZE)))    

class Mines:
    def __init__(self):
        # Laad mine-afbeelding en schaal deze
        self.image = pygame.image.load("git/opsnake/images/mine.png").convert_alpha()
        self.image = pygame.transform.scale(self.image,(SIZE,SIZE))
        self.move()

    def move(self):
        # Verplaats de mijn naar een willekeurige plek op het grid
        self.x = random.randint(0,(WIDTH//SIZE)-1)*SIZE
        self.y = random.randint(0,(HEIGHT//SIZE)-1)*SIZE

    def draw(self):
        # Teken de mijn op het scherm
        screen.blit(self.image,(self.x,self.y))

class Apple:
    def __init__(self):
        # Laad appel-afbeelding en schaal deze
        self.image = pygame.image.load("git/opsnake/images/apple.jpg").convert_alpha()
        self.image = pygame.transform.scale(self.image,(SIZE,SIZE))
        self.move()

    def move(self):
        # Verplaats de appel naar een willekeurige plek
        self.x = random.randint(0,(WIDTH//SIZE)-1)*SIZE
        self.y = random.randint(0,(HEIGHT//SIZE)-1)*SIZE

    def draw(self):
        # Teken de appel op het scherm
        screen.blit(self.image,(self.x,self.y))

class Snake:
    def __init__(self):
        # Laad de afbeelding voor de slang-onderdelen
        self.image = pygame.image.load("git/opsnake/images/block.jpg").convert_alpha()
        self.image = pygame.transform.scale(self.image,(SIZE,SIZE))

        self.direction = "right"  # Begin-richting
        self.length = 3           # Begin-lengte

        # Maak lijsten voor de X en Y posities van elk lichaamsdeel
        self.x = [SIZE*5]*self.length
        self.y = [SIZE*5]*self.length

    def move(self):
        # Schuif elk lichaamsdeel op naar de positie van zijn voorganger
        for i in range(self.length-1,0,-1):
            self.x[i] = self.x[i-1]
            self.y[i] = self.y[i-1]

        # Verplaats de kop in de huidige richting
        if self.direction == "right": self.x[0]+=SIZE
        if self.direction == "left":  self.x[0]-=SIZE
        if self.direction == "up":    self.y[0]-=SIZE
        if self.direction == "down":  self.y[0]+=SIZE

    def grow(self):
        # Maak de slang langer en voeg een tijdelijk segment toe buiten beeld
        self.length+=1
        self.x.append(-100)
        self.y.append(-100)

    def shrink(self):
        # Maak de slang korter als hij langer is dan 1 segment
        if self.length>1:
            self.length-=1
            self.x.pop()
            self.y.pop()
        elif self.length==1:
            dead()  # Als de slang verdwijnt, is het game over

    def draw(self):
        # Teken elk segment van de slang
        for i in range(self.length):
            screen.blit(self.image,(self.x[i],self.y[i]))

    def check_dead(self):
        # Controleer of de kop de randen van het scherm raakt
        if self.x[0] < 0 or self.x[0] >= WIDTH: return True
        if self.y[0] < 0 or self.y[0] >= HEIGHT: return True

        # Controleer of de kop het eigen lichaam raakt
        for i in range(1,self.length):
            if self.x[0] == self.x[i] and self.y[0] == self.y[i]:
                return True
        return False

# =========================
# Functions
# =========================

def draw_score(snake):
    # Maak een lettertype aan en render de score (lengte - 1)
    font = pygame.font.SysFont("arial",30)
    score = font.render("Score: "+str(snake.length-1),True,(255,255,255))
    screen.blit(score,(WIDTH//2-70,10))

def dead():
    # Verander de status naar game over en speel geluid
    global state
    death_sound.play()
    state=GAMEOVER

def draw_menu():
    # Teken het hoofdmenu met moeilijkheidsgraden
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
    # Teken het game-over scherm met de eindscore
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

state = MENU    # Start in het menu
speed = 10      # Snelheid (FPS)
aantal = 5      # Standaard aantal mijnen
walls = 0       # Standaard aantal muren
snake = Snake() # Initialiseer slang
apple = Apple() # Initialiseer appel
mine = []       # Lijst voor mijnen
muur = []       # Lijst voor muren

# =========================
# Main Loop
# =========================
running = True

while running:
    if state == MENU:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False
            if event.type == pygame.KEYDOWN:
                # Keuze moeilijkheidsgraad bepaalt aantal mijnen en muren
                if event.key == pygame.K_1:
                    aantal=5; walls=1; state=PLAYING
                if event.key == pygame.K_2:
                    aantal=10; walls=3; state=PLAYING
                if event.key == pygame.K_3:
                    aantal=20; walls=6; state=PLAYING
                
                if state==PLAYING:
                    # Maak de objecten aan op basis van gekozen moeilijkheid
                    mine=[Mines() for _ in range(aantal)]
                    muur = [Muur() for _ in range(walls)]
                    overlap = True
                    # Zorg dat de appel niet op een mijn of muur verschijnt
                    while overlap:
                        apple.move()
                        overlap = False
                        for m in mine: 
                            if apple.x == m.x and apple.y == m.y: overlap = True
                        for w in muur:
                            for i in range(3):
                                if apple.x == w.x and apple.y == w.y + (i * SIZE): overlap = True
                        # Zorg dat mijnen niet in muren staan
                        for w in muur:
                            for i in range(3):
                                for m in mine:
                                    if m.x==w.x and m.y==w.y+(i*SIZE):
                                        m.move()
                                        overlap=True

    elif state == PLAYING:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False
            if event.type == pygame.KEYDOWN:
                # Besturing via toetsenbord (voorkom 180-graden draai)
                if event.key == pygame.K_LEFT and snake.direction!="right": snake.direction="left"
                if event.key == pygame.K_RIGHT and snake.direction!="left": snake.direction="right"
                if event.key == pygame.K_UP and snake.direction!="down": snake.direction="up"
                if event.key == pygame.K_DOWN and snake.direction!="up": snake.direction="down"

        # Besturing via joystick assen
        for joystick in joysticks:
            x_axis = joystick.get_axis(0)
            y_axis = joystick.get_axis(1)
            if abs(x_axis)>0.5:
                if x_axis>0 and snake.direction!="left": snake.direction="right"
                if x_axis<0 and snake.direction!="right": snake.direction="left"
            elif abs(y_axis)>0.5:
                if y_axis>0 and snake.direction!="up": snake.direction="down"
                if y_axis<0 and snake.direction!="down": snake.direction="up"

        snake.move() # Beweeg de slang

        # Check collision met appel
        if snake.x[0] == apple.x and snake.y[0] == apple.y:
            snake.grow()
            apple.move()
            apple_sound.play()
            
        # Check collision met mijnen (slang krimpt)
        for m in mine:
            if snake.x[0]==m.x and snake.y[0]==m.y:
                snake.shrink()
                m.move()
                
        # Check collision met muren (dood)
        for w in muur:
            for i in range(3):
                if snake.x[0]==w.x and snake.y[0]==w.y+(i*SIZE):
                    death_sound.play()
                    state=GAMEOVER
                    
        # Check of slang uit veld is of zichzelf bijt
        if snake.check_dead():
            death_sound.play()
            state = GAMEOVER

        # Teken alles op het scherm
        screen.fill(BG_COLOR)
        apple.draw()
        snake.draw()
        for w in muur: w.draw()
        for m in mine: m.draw()
        draw_score(snake)

        pygame.display.update() # Update het scherm
        clock.tick(speed)       # Controleer de snelheid van de loop

    elif state == GAMEOVER:
        draw_game_over(snake.length-1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False
            if event.type == pygame.KEYDOWN:
                # Reset het spel als 'R' wordt ingedrukt
                if event.key == pygame.K_r:
                    snake = Snake()
                    apple = Apple()
                    mine=[]
                    state = MENU

pygame.quit() # Sluit pygame af
sys.exit()    # Stop het script volledig