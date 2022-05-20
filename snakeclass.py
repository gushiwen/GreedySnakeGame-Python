import pygame, os, sys, time
from pygame.locals import *
import random
import files.pygame_textinput as pygame_textinput
FILE_PATH = os.path.join(os.path.dirname(__file__), 'files')
os.chdir(FILE_PATH)
font = pygame.font.Font(None, 30)

class Snake(pygame.sprite.Sprite):
    snakeHead = pygame.image.load('snake_head.png')  # 30x30px
    snakeBody = pygame.image.load('snake_body_h.png')  # 30x30px
    snakeTurn = pygame.image.load('snake_turn.png')  # 30x30px
    snakeTail = pygame.image.load('snake_tail.png')  # 30x30px

    # In order to draw the snake in Class, pass screen into it
    # snakeLine = [snakeHead_position, snakeBody1_position, SnakeBody2_position ... snakeTail_position]
    def __init__(self, screen):
        pygame.sprite.Sprite.__init__(self)
        self.snakeLine = [(450, 300), (450 - 30, 300), (450 - 60, 300)]  # coordinates of rect's left/top point
        self.screen = screen
        self.rect = Rect(450, 300, 30, 30)  # rect of snake head
        self.lengthening = 0
        self.live = True

    def getBodyImage(self, index):
        # check 3 rects, with one rect before and one rect after
        if self.snakeLine[index - 1][0] == self.snakeLine[index + 1][0]:
            # if same x, move vertically
            return pygame.transform.rotate(Snake.snakeBody, 90)
        elif self.snakeLine[index - 1][1] == self.snakeLine[index + 1][1]:
            # if same y, move horizontally
            return Snake.snakeBody
        else:
            # exclude central rect, one rect's x,y greater than the other one's x,y
            body_offX = self.snakeLine[index - 1][0] - self.snakeLine[index + 1][0]
            body_offY = self.snakeLine[index - 1][1] - self.snakeLine[index + 1][1]
            slope = body_offX/body_offY
            # one rect's x greater than central rect's x
            right = max(self.snakeLine[index - 1][0], self.snakeLine[index + 1][0]) > self.snakeLine[index][0]
            tmpBody = pygame.Surface((30,30))
            if slope > 0 and right: #|__
                tmpBody = pygame.transform.rotate(Snake.snakeTurn, 180)
            elif slope > 0 and not right:#^^|
                tmpBody = Snake.snakeTurn
            elif slope < 0 and right: #|^^
                tmpBody = pygame.transform.rotate(Snake.snakeTurn, 90)
            elif slope < 0 and not right: #__|
                tmpBody = pygame.transform.rotate(Snake.snakeTurn, -90)
            if abs(body_offX) == 870:
                tmpBody = pygame.transform.flip(tmpBody, True, False)
            elif abs(body_offY) == 570:
                tmpBody = pygame.transform.flip(tmpBody, False, True)
            return tmpBody
        return None

    def show(self, newSnakeLine=None):
        if newSnakeLine is not None:
            self.snakeLine = newSnakeLine
            self.rect = Rect(newSnakeLine[0], (30, 30))
        degrees = {K_UP: 90, K_DOWN: -90, K_LEFT: 180, K_RIGHT: 0}
        headDegree = degrees[self.getDirection()]
        self.screen.blit(pygame.transform.rotate(Snake.snakeHead, headDegree), self.snakeLine[0])
        self.rect = Rect(self.snakeLine[0], (30, 30))

        for inx in range(1, len(self.snakeLine) - 1):
            self.screen.blit(self.getBodyImage(inx), self.snakeLine[inx])

        tailDegree = 0
        tail_offX = self.snakeLine[-2][0] - self.snakeLine[-1][0]
        tail_offY = self.snakeLine[-2][1] - self.snakeLine[-1][1]
        if (tail_offX == 30 or tail_offX == -870) and tail_offY == 0:
            tailDegree = 0
        elif (tail_offX == -30 or tail_offX == 870) and tail_offY == 0:
            tailDegree = 180
        elif tail_offX == 0 and (tail_offY == 30 or tail_offY == -570):
            tailDegree = -90
        elif tail_offX == 0 and (tail_offY == -30 or tail_offY == 570):
            tailDegree = 90
        self.screen.blit(pygame.transform.rotate(Snake.snakeTail, tailDegree), self.snakeLine[-1])

    # Snake head's direction is snake's current direction
    def getDirection(self):
        head_offX = self.snakeLine[0][0] - self.snakeLine[1][0]
        head_offY = self.snakeLine[0][1] - self.snakeLine[1][1]
        if (head_offX == 30 or head_offX == -870) and head_offY == 0:  # -870 through right edge
            return K_RIGHT
        elif (head_offX == -30 or head_offX == 870) and head_offY == 0:  # 870 through left edge
            return K_LEFT
        elif head_offX == 0 and (head_offY == -30 or head_offY == 570):  # 570 through top edge
            return K_UP
        elif head_offX == 0 and (head_offY == 30 or head_offY == -570):  # -570 through bottom edge
            return K_DOWN

    def move(self, KEY=None):
        # if duplicate rects existed in snakeLine, snake collide itself
        if len(set(self.snakeLine)) < len(self.snakeLine):
            self.live = False
            return
        wrong_list = [(K_RIGHT, K_RIGHT), (K_RIGHT, K_LEFT), (K_LEFT, K_LEFT), (K_LEFT, K_RIGHT), (K_UP, K_UP),
                      (K_UP, K_DOWN), (K_DOWN, K_DOWN), (K_DOWN, K_UP)]
        if self.lengthening > 0:
            self.enlarge()
            self.lengthening -= 1
        else:
            if KEY is None or (self.getDirection(), KEY) in wrong_list:
                KEY = self.getDirection()
            if KEY == K_RIGHT:
                self.snakeLine = [((self.snakeLine[0][0] + 30) % 900, self.snakeLine[0][1])] + self.snakeLine[0:-1]
            elif KEY == K_UP:
                self.snakeLine = [(self.snakeLine[0][0], (600 + self.snakeLine[0][1] - 30) % 600)] + self.snakeLine[0:-1]
            elif KEY == K_DOWN:
                self.snakeLine = [(self.snakeLine[0][0], (self.snakeLine[0][1] + 30) % 600)] + self.snakeLine[0:-1]
            elif KEY == K_LEFT:
                self.snakeLine = [((900 + self.snakeLine[0][0] - 30) % 900, self.snakeLine[0][1])] + self.snakeLine[0:-1]

    # increase one grid in front of snake head after eating one raspberry
    def enlarge(self):
        adding_block_offset = {K_LEFT:(-30,0),K_RIGHT:(30,0),K_UP:(0,-30),K_DOWN:(0,30)}
        off_set = adding_block_offset[self.getDirection()]
        self.snakeLine.insert(0, (self.snakeLine[0][0]+off_set[0],self.snakeLine[0][1]+off_set[1]))

class Raspberry(pygame.sprite.Sprite):
    group = pygame.sprite.Group()
    # all 30x30 grids's left-top position on the screen
    screenBlankGrid = [(x*30,y*30) for x in range(30) for y in range(20)]

    def __init__(self, snake_line=[]):
        pygame.sprite.Sprite.__init__(self)
        blank_grid = list(filter(lambda x:x not in snake_line, Raspberry.screenBlankGrid))
        xy = random.choice(blank_grid)
        Raspberry.screenBlankGrid.remove(xy) # Occupied
        self.rect = Rect(xy[0], xy[1], 30, 30)
        self.image = pygame.image.load('snake_food.png')
        Raspberry.group.add(self)

def show_start(screen):
    #Load image by file path
    background = pygame.image.load('snake_start.png')
    #Load sound by file path
    pygame.mixer.music.load('sound_snake_start.mp3')
    pygame.mixer.music.play(loops=-1) #Play sound repeatedly
    #Add background image onto screen position (0,0)
    screen.blit(background,[0,0])
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            if event.type == KEYUP:
                pygame.mixer.music.stop()
                return
        time.sleep(0.05)
        screen.fill(pygame.Color(0,0,0), Rect(0,560,900,40))
        if int(time.time())%2 == 0:  #Show text if even number
            screen.blit(font.render('Press any key to start...', 1, Color(255,255,255)), [200,565])
        pygame.display.update()

def main_loop(screen):
    bg = pygame.image.load('bg.jpg')
    pygame.mixer.music.load('sound_snake_play.mp3')
    pygame.mixer.music.play(loops=-1)
    sound_eat = pygame.mixer.Sound('sound_snake_get.wav')
    sound_hit = pygame.mixer.Sound('sound_snake_fail.wav')
    snake = Snake(screen)
    clock = pygame.time.Clock()
    level = 1
    last_collide = None
    KEY = None
    SNAKEEVENT = USEREVENT + 1
    pygame.time.set_timer(SNAKEEVENT, 300)
    eaten = []
    food_score, time_score = 0, 0
    while True:
        clock.tick(20)
        time_score = int(pygame.time.get_ticks()/1000)
        screen.blit(bg, (0, 0))
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == KEYUP:
                KEY = event.key
            elif event.type == SNAKEEVENT:
                snake.move(KEY)
        snake.show()
        # increase rasp's amount by level
        while len(Raspberry.group.sprites()) < int(level):
            Raspberry(snake.snakeLine)
        Raspberry.group.draw(screen)
        # what food the snake collided, return none if nothing
        rasp = pygame.sprite.spritecollideany(snake, Raspberry.group)
        if rasp:
            if rasp != last_collide:  # collide new food
                food_score += 10
                level += 1
                eaten.append(rasp)
                snake.lengthening += 1
                last_collide = rasp
                sound_eat.play()
            else:  # collide same food, shrink the food image
                rasp.image = pygame.transform.smoothscale(rasp.image, (int(rasp.rect.width-2), int(rasp.rect.height-2)))
                rasp.rect.inflate_ip(-2, -2)
        # kill previous rasp once snake head/rect touch next grid, either empty (rasp=None) or new rasp
        if last_collide and rasp != last_collide and last_collide in Raspberry.group.sprites():
            for one_eaten in eaten:
                one_eaten.kill()
            eaten = []
        pygame.display.update()
        if not snake.live:
            sound_hit.play()
            break
    return food_score, time_score

def show_end(screen, food_score=0, time_score=0):
    old_screen = screen.copy()
    end_clock = pygame.time.Clock()
    origin_end_image = pygame.image.load('end.png')
    ratios = origin_end_image.get_rect().width/origin_end_image.get_rect().height
    newWidth = 200
    old_ticks = pygame.time.get_ticks() #millisedonds from pygame.init()
    while True:
        end_clock.tick(20) # fps=20, time intervals 1000/20 milliseconds
        ticks = pygame.time.get_ticks() - old_ticks # integer multiples of 1000/20
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            # if image is bigger enough, press any key to return
            if event.type==KEYUP and newWidth>700:
                return
        # enlarge image from width 200 until width 700
        if newWidth<=700:
            newWidth += int(ticks/1000*20)
        # after enlarging
        end_image = pygame.transform.smoothscale(origin_end_image, (newWidth,int(newWidth/ratios)))
        x,y = int(900/2-end_image.get_rect().width/2), int(400/2-end_image.get_rect().height/2)
        screen.blit(old_screen, (0,0))
        screen.blit(end_image, (x,y))
        # show scores after enlarging done
        if newWidth>700:
            pygame.draw.rect(screen, Color(153,204,51), Rect(150,350,600,200))
            screen.blit(pygame.image.load('snake_food.png'), (350,380))
            screen.blit(font.render(str(food_score)+' Points',True,Color(255,0,0)), (500,385))
            screen.blit(pygame.image.load('time.png'), (350,430))
            screen.blit(font.render(str(time_score)+' Points',True,Color(255,0,0)), (500,435))
            screen.blit(font.render('Total',True,Color(255,0,0)), (350,480))
            screen.blit(font.render(str(time_score+food_score)+' Points',True,Color(255,0,0)), (500,480))
        pygame.display.update()

def show_top10(screen, score):
    #Jack                92
    #PEKKAKOOPP          90
    open('snake_top10.txt','a').close()
    file = open('snake_top10.txt', 'r+')
    top10 = []
    for line in file.readlines():
        top10.append((line[0:20],int(line[20:]))) #('Jack                ',80)
    #if current score > last score on list or <10 players listed
    if score>=top10[-1][1] or len(top10)<10:
        top10.insert(0, (('%-20s'%input_name(screen))[0:20], score))
        top10.sort(key=lambda x:x[1], reverse=True)
    if len(top10) > 10:
        top10 = top10[0:10]
    file.seek(0)
    fileContent = '\n'.join([x[0]+str(x[1]) for x in top10])
    file.write(fileContent)
    file.close()

    old_screen = screen.copy()
    top10_bg = pygame.Surface((900,600), SRCALPHA, 32)
    top10_bg.fill(Color(0,0,0,50),None)
    font = pygame.font.Font(None, 48)
    top10_bg.blit(font.render('TOP 10 PLAYERS',True,Color(255,255,255)), (300,20))
    for (i,textline) in enumerate(top10):
        top10_bg.blit(font.render('%-4d'%(i+1)+textline[0],True,Color(255,255,255)), (180,120+i*40))
        top10_bg.blit(font.render(str(textline[1]),True,Color(255,255,255)), (710,120+i*40))
    y = 600
    clock = pygame.time.Clock()
    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            if event.type == KEYUP and y<=0:
                return
        screen.blit(old_screen, (0,0))
        screen.blit(top10_bg, (0,y))
        pygame.display.update()
        y -= 20
        if y<=0:
            y = 0

def input_name(screen):
    textInput = pygame_textinput.TextInput()
    textInput.font_size = 30
    textInput.set_text_color(Color(255,0,0))
    textInput.set_cursor_color(Color(255,0,0))
    clock = pygame.time.Clock()
    old_screen = screen.copy()
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                sys.exit()
        if textInput.update(events):
            return textInput.get_text()
        screen.blit(old_screen, (0,0))
        screen.blit(font.render('Congratulations! You are one of the top 10!',True,Color(255,0,0)), (170,10))
        screen.blit(font.render('Input your name: ',True,Color(255,0,0)), (200,50))
        screen.blit(textInput.get_surface(), (450,50))
        pygame.display.update()
        clock.tick(30)
