# 优化的贪吃蛇游戏版本
# 更精确的控制移动方向
# 更精确的帧率控制

import pygame
import random
from collections import namedtuple
from pygame.locals import K_RIGHT,K_LEFT,K_UP,K_DOWN,QUIT

Position = namedtuple('Point', 'x, y')

class Direction:
    right = 0
    left = 1
    up = 2
    down = 3

class Snake:

    def __init__(self,block_size):
        self.blocks=[]
        self.blocks.append(Position(10,15))
        self.blocks.append(Position(9,15))
        self.block_size = block_size
        self.head = self.blocks[0]
        self.current_direction = Direction.right
        self.image = pygame.image.load('snake.png')
        self.move_time = pygame.time.get_ticks()
        self.open_time = pygame.time.get_ticks()
        self.frame = 0

    
    def move(self):
        if pygame.time.get_ticks() - self.move_time > 200:
            if (self.current_direction == Direction.right):
                movesize = (1, 0)
            elif (self.current_direction == Direction.left):
                movesize = (-1, 0)
            elif (self.current_direction == Direction.up):
                movesize = (0, -1)
            else:
                movesize = (0, 1)
            self.move_time = pygame.time.get_ticks()
            
            new_head = Position(self.head.x + movesize[0], self.head.y + movesize[1])  
            self.blocks.insert(0,new_head)
            self.head = self.blocks[0]
            self.tail = self.blocks.pop()
            
    def handle_input(self, event, game):
        if event.type == pygame.KEYDOWN:
            game.sounds["turn"].play()
            if event.key == K_RIGHT and self.current_direction != Direction.left:
                self.current_direction = Direction.right

            elif event.key == K_LEFT and self.current_direction != Direction.right:
                self.current_direction = Direction.left

            elif event.key == K_UP and self.current_direction != Direction.down:
                self.current_direction = Direction.up

            elif event.key == K_DOWN and self.current_direction != Direction.up:
                self.current_direction = Direction.down



    def draw(self,surface):
        if pygame.time.get_ticks() - self.open_time > 200:
            self.frame = (self.frame + 1)%2
            self.open_time = pygame.time.get_ticks()
        for index, block in enumerate(self.blocks):
            positon = (block.x * self.block_size, 
                    block.y * self.block_size)
            if index == 0:
                src = (((self.current_direction * 2) + self.frame) * self.block_size,
                         0, self.block_size, self.block_size)
            else:
                src = (8 * self.block_size, 0, self.block_size, self.block_size)
            surface.blit(self.image, positon, src)


class Berry:

    def __init__(self,block_size):
        self.block_size = block_size
        self.image = pygame.image.load('berry.png').convert_alpha()
        self.position = Position(1, 1)     

    def draw(self,surface):
        rect = self.image.get_rect()
        rect.left = self.position.x * self.block_size
        rect.top = self.position.y * self.block_size
        surface.blit(self.image, rect)


class Wall:

    def __init__(self,block_size):
        self.block_size = block_size
        self.map = self.load_map('map.txt')
        self.image = pygame.image.load('wall.png')

    def load_map(self,fileName):
        with open(fileName,'r') as map_file:
            content = map_file.readlines()
            content =  [list(line.strip()) for line in content]
        return content  

    def draw(self,surface):
        for row, line in enumerate(self.map):
            for col, char in enumerate(line):
                if char == '1':
                    position = (col*self.block_size,row*self.block_size)
                    surface.blit(self.image, position)     


class Game:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (112,128,144)
    def __init__(self,Width=640, Height=480):
        pygame.init()
        self.block_size = 16
        self.Win_width , self.Win_height = (Width, Height)
        self.Space_width = self.Win_width//self.block_size-2
        self.Space_height = self.Win_height//self.block_size-2
        self.surface = pygame.display.set_mode((self.Win_width, self.Win_height))
        self.score = 0
        self.running = True
        self.Clock = pygame.time.Clock()
        self.fps = 30
        self.font = pygame.font.Font(None, 32)
        self.snake = Snake(self.block_size)
        self.berry = Berry(self.block_size)
        self.wall = Wall(self.block_size)
        self.sounds = self.load_sounds()
        self.position_berry()
        # you can use your own music for the background
        # pygame.mixer.music.load('background.mp3')
        # pygame.mixer.music.play(-1)


    def load_sounds(self):
        turn = pygame.mixer.Sound('step.wav')
        hit = pygame.mixer.Sound('hit.wav')
        point = pygame.mixer.Sound('point.wav')
        return {"turn":turn, "hit":hit, "point":point}

    def position_berry(self):
        bx = random.randint(1, self.Space_width)
        by = random.randint(1, self.Space_height)
        self.berry.position = Position(bx, by)
        if self.berry.position in self.snake.blocks:
            self.position_berry()
            

    # handle collision
    def berry_collision(self):
        if (self.snake.head.x == self.berry.position.x and
            self.snake.head.y == self.berry.position.y):
            self.position_berry()
            self.snake.blocks.append(self.snake.tail)
            self.score += 1
            self.sounds["point"].play()

    def head_hit_body(self):
        if self.snake.head in self.snake.blocks[1:]:
            self.sounds["hit"].play()
            return True 
        return False

    def head_hit_wall(self):
        if (self.wall.map[self.snake.head.y][self.snake.head.x] == '1'):
            self.sounds["hit"].play()
            return True
        return False


    def draw_data(self):
        text = "score: {0}".format(self.score)
        text_img = self.font.render(text, 1, Game.WHITE)
        text_rect = text_img.get_rect(centerx=self.surface.get_width()/2, top=32)
        self.surface.blit(text_img, text_rect)
    
    
    def draw(self):
        self.surface.fill(Game.GRAY)
        self.wall.draw(self.surface)
        self.berry.draw(self.surface)
        self.snake.draw(self.surface)
        self.draw_data()
        pygame.display.update()

    # main loop 
    def play(self):
        while self.running:

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                self.snake.handle_input(event, self)

            self.snake.move()
            self.berry_collision()
            if self.head_hit_wall() or self.head_hit_body():
                print('Final Score', self.score)
                pygame.time.delay(1000)
                self.running = False

            self.draw()
            self.Clock.tick(self.fps)
        
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.play()
