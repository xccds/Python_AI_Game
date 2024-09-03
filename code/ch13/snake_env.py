import pygame
import random
from collections import namedtuple
from pygame.locals import QUIT
import numpy as np
import sys

Position = namedtuple('Point', 'x, y')

class Direction:
    right = 0
    left = 1
    up = 2
    down = 3

class Snake:

    def __init__(self,block_size):
        self.blocks=[]
        self.blocks.append(Position(20,15))
        self.blocks.append(Position(19,15))
        self.block_size = block_size
        self.current_direction = Direction.right
        self.image = pygame.image.load('snake.png')

    def move(self):
        if (self.current_direction == Direction.right):
            movesize = (1, 0)
        elif (self.current_direction == Direction.left):
            movesize = (-1, 0)
        elif (self.current_direction == Direction.up):
            movesize = (0, -1)
        else:
            movesize = (0, 1)
        head = self.blocks[0]
        new_head = Position(head.x + movesize[0], head.y + movesize[1])  
        self.blocks.insert(0,new_head)

    def handle_action(self,action):
        # action is one of  [straight, right, left]
        clock_wise = [Direction.right,Direction.down,Direction.left,Direction.up] 
        idx = clock_wise.index(self.current_direction)
        if action == 0:
            new_dir = clock_wise[idx] # no change
        elif action == 1:
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx] # right turn r -> d -> l -> u
        elif action == 2:
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx] # left turn r -> u -> l -> d
        self.current_direction = new_dir 
        self.move()

    def draw(self,surface,frame):
        for index, block in enumerate(self.blocks):
            positon = (block.x * self.block_size, 
                    block.y * self.block_size)
            if index == 0:
                src = (((self.current_direction * 2) + frame) * self.block_size,
                         0, self.block_size, self.block_size)
            else:
                src = (8 * self.block_size, 0, self.block_size, self.block_size)
            surface.blit(self.image, positon, src)

class Berry:

    def __init__(self,block_size):
        self.block_size = block_size
        self.image = pygame.image.load('berry.png')
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
    def __init__(self,Width=640,Height=480):
        pygame.init()
        self.block_size = 16        
        self.Win_width , self.Win_height = (Width, Height)
        self.Space_width = self.Win_width//self.block_size-2
        self.Space_height = self.Win_height//self.block_size-2
        self.surface = pygame.display.set_mode((self.Win_width, self.Win_height))
        self.font = pygame.font.Font(None, 32)
        self.Clock = pygame.time.Clock()
        self.snake = Snake(self.block_size)
        self.berry = Berry(self.block_size)
        self.wall = Wall(self.block_size)
        self.nS = 20
        self.nA = 3
        self.reset()
        
    
    def reset(self):
        # init game state
        self.score = 0
        self.frame = 0
        self.snake = Snake(self.block_size)
        self.position_berry()
        self.total_step = 0
        self.reward = 0

    def position_berry(self):
        bx = random.randint(1, self.Space_width)
        by = random.randint(1, self.Space_height)
        self.berry.position = Position(bx, by)
        if self.berry.position in self.snake.blocks:
            self.position_berry()

    def berry_collision(self):
        head = self.snake.blocks[0]
        if (head.x == self.berry.position.x and
            head.y == self.berry.position.y):
            self.position_berry()
            self.score += 1
            self.reward = 10
        else:
            self.snake.blocks.pop()

    def head_hit_body(self,position=None):
        if position is None:
            position = self.snake.blocks[0]
        if position in self.snake.blocks[1:]:
            return True    
        return False
    
    def head_hit_wall(self,position=None):
        if position is None:
            position = self.snake.blocks[0]
        
        if position.y>=29 or position.x>=39 or position.x<=0 or position.y<=0:
            return True
        
        if (self.wall.map[position.y][position.x] == '1'):
            return True
        
        return False

    def draw_data(self):
        text = "score = {0}".format(self.score)
        text_img = self.font.render(text, 1, Game.WHITE)
        text_rect = text_img.get_rect(centerx=self.surface.get_width()/2, top=32)
        self.surface.blit(text_img, text_rect)
    

    def draw(self):
        self.surface.fill(Game.BLACK)
        self.wall.draw(self.surface)
        self.berry.draw(self.surface)
        self.snake.draw(self.surface,self.frame)
        self.draw_data()
        pygame.display.update()

    def play_step(self, action):
        game_over = False
        self.reward = 0

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                     
        self.total_step += 1
        self.frame = (self.frame + 1) % 2
        self.snake.handle_action(action)
        self.berry_collision()

        if (self.head_hit_wall() or 
            self.head_hit_body() or 
            self.total_step > 100*len(self.snake.blocks)):
            game_over = True
            self.reward = -10
            return self.reward, game_over, self.score
  
        self.draw()
        self.Clock.tick(60)
        return self.reward, game_over, self.score

    
    def get_state(self):
        head = self.snake.blocks[0]
        point_l = Position(head.x - 1, head.y)
        point_r = Position(head.x + 1, head.y)
        point_u = Position(head.x, head.y - 1)
        point_d = Position(head.x, head.y + 1)
        danger_1b_r = self.head_hit_body(point_r)
        danger_1b_l = self.head_hit_body(point_l)
        danger_1b_u = self.head_hit_body(point_u)
        danger_1b_d = self.head_hit_body(point_d)
        danger_1w_r = self.head_hit_wall(point_r)
        danger_1w_l = self.head_hit_wall(point_l)
        danger_1w_u = self.head_hit_wall(point_u)
        danger_1w_d = self.head_hit_wall(point_d)
        
        points_l = [Position(i, head.y) for i in range(1,head.x)]
        points_r = [Position(i, head.y) for i in range(head.x+1,self.Space_width)]
        points_u = [Position(head.x , i) for i in range(1,head.y)]
        points_d = [Position(head.x , i) for i in range(head.y+1,self.Space_height)]
        danger_b_l = np.any(np.array([self.head_hit_body(point) for point in points_l]))
        danger_b_r = np.any(np.array([self.head_hit_body(point) for point in points_r]))
        danger_b_u = np.any(np.array([self.head_hit_body(point) for point in points_u]))
        danger_b_d = np.any(np.array([self.head_hit_body(point) for point in points_d]))

        dir_l = self.snake.current_direction == Direction.left
        dir_r = self.snake.current_direction == Direction.right
        dir_u = self.snake.current_direction == Direction.up
        dir_d = self.snake.current_direction == Direction.down

        berry_l = self.berry.position.x < head.x
        berry_r = self.berry.position.x > head.x 
        berry_u = self.berry.position.y < head.y  
        berry_d = self.berry.position.y > head.y

        state = [
            danger_1b_r,danger_1b_l,danger_1b_u,danger_1b_d,
            danger_1w_r,danger_1w_l,danger_1w_u,danger_1w_d,
            danger_b_l,danger_b_r,danger_b_u,danger_b_d,
            dir_l,dir_r,dir_u,dir_d,
            berry_l, berry_r,berry_u,berry_d
            ]

        return np.array(state, dtype=int) 