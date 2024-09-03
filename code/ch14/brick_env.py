import pygame, sys
from pygame.locals import *
import numpy as np
import random
from  math import radians, sin, cos, asin


class Bat:
    def __init__(self,StartX=400, StartY=540,speedX=5):
        self.image = pygame.image.load('bat.png')
        self.rect = self.image.get_rect()
        self.positionX, self.positionY = StartX,StartY
        self.speedX= speedX
        self.rect.topleft = (self.positionX, self.positionY)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update(self,win_width):
        self.positionX += self.speedX
        if self.positionX < 0:
            self.positionX = 0
        if (self.positionX > win_width - self.rect.width):
            self.positionX = win_width - self.rect.width
        self.rect.topleft = (self.positionX, self.positionY)



# ball init
class Ball:
    def __init__(self,win_width):
        self.image = pygame.image.load('ball.png')
        self.rect = self.image.get_rect()
        self.reset(win_width)

    def reset(self,win_width,startY=220,speed=5):
        self.served = False
        self.positionX = random.randint(200,600)
        self.degree = random.randint(-45,45)
        self.positionY = startY
        self.rect.topleft = (self.positionX, self.positionY)
        self.speed = speed
        self.speedX = self.speed * sin(radians(self.degree))
        self.speedY = self.speed * cos(radians(self.degree))

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update(self,win_width): 
        self.positionX += self.speedX
        self.positionY += self.speedY
        self.rect.topleft = (self.positionX, self.positionY)

        if (self.positionY <= 0):
            self.positionY = 0
            self.speedY *= -1

        if (self.positionX <= 0):
            self.positionX = 0
            self.speedX *= -1

        if (self.positionX >=win_width - self.rect.width):
            self.positionX = win_width - self.rect.width
            self.speedX *= -1

class Bricks:
    def __init__(self,row=5, col=12):
        self.image = pygame.image.load('brick.png')
        self.rect = self.image.get_rect()
        self.contains = []
        for y in range(row):
            brickY = (y * 24) + 100
            for x in range(col):
                brickX = (x * 31) + 214
                rect = Rect(brickX, brickY, self.rect.width, self.rect.height)
                self.contains.append(rect)

    def draw(self, surface):
        for rect in self.contains:
            surface.blit(self.image, rect)


class Game:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    def __init__(self, Width=800,Height=600):
        pygame.init()
        self.Win_width , self.Win_height = (Width, Height)
        self.surface = pygame.display.set_mode((self.Win_width, self.Win_height))
        self.font = pygame.font.SysFont('microsoftyahei',26)
        self.reset()
        self.nS = 5
        self.nA = 3
        self.Clock = pygame.time.Clock()
        pygame.display.set_caption('Bricks')

    def reset(self):
        self.bat = Bat()
        self.ball = Ball(self.Win_width) 
        self.bricks = Bricks() 
        self.score = 0
        self.reward = 0

    def bat_collision(self):
        if self.ball.rect.colliderect(self.bat.rect):
            self.reward = 10
            self.ball.rect.bottom = self.bat.rect.top
            diff_x = self.ball.rect.centerx - self.bat.rect.centerx
            diff_ratio = min(0.95,abs(diff_x)/(0.5*self.bat.rect.width))
            theta = asin(diff_ratio)
            self.ball.speedX = self.ball.speed * sin(theta)
            self.ball.speedY = self.ball.speed * cos(theta)
            self.ball.speedY *= -1
            if (diff_x<0 and self.ball.speedX>0) or (diff_x>0 and self.ball.speedX<0):
                self.ball.speedX *= -1
            
    def bricks_collision(self):
        brickHitIndex = self.ball.rect.collidelist(self.bricks.contains)
        if brickHitIndex >= 0:
            brick = self.bricks.contains[brickHitIndex]
            if (self.ball.rect.centerx > brick.right or 
                self.ball.rect.centerx < brick.left):
                self.ball.speedX *= -1
            else:
                self.ball.speedY *= -1
            del (self.bricks.contains[brickHitIndex])
            self.score +=1
    
    def check_failed(self):
        if self.ball.rect.bottom >= self.Win_height:
            return True 
        else:
            return False


    def draw_data(self):
        score_text = "得分：{score}".format(score=self.score)
        score_img = self.font.render(score_text, 1, Game.WHITE)
        score_rect = score_img.get_rect(centerx=self.Win_width//2, top=5)
        self.surface.blit(score_img, score_rect)

    def draw(self):
        self.surface.fill(Game.BLACK)
        self.draw_data()
        self.bricks.draw(self.surface)
        self.bat.draw(self.surface)
        self.ball.draw(self.surface)
        pygame.display.update()

    def handle_action(self, action):
        if action==0:
            self.bat.speedX = 0
        elif action==1:
            self.bat.speedX = -6
        else: 
            self.bat.speedX = 6
        self.bat.update(self.Win_width)
    
    def ball_near_bat(self):
        if abs(self.bat.rect.centery - self.ball.rect.centery)<300:
            return True
        else :
            return False

    def play_step(self,action):
        game_over = False
        self.reward = 0

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        self.handle_action(action)    
        self.ball.update(self.Win_width)
        self.bat_collision()
        self.bricks_collision()

        if self.check_failed():
            game_over = True
            self.reward = -10
            return self.reward, game_over, self.score
        
        if len(self.bricks.contains)==0:
            self.reward = 10
            game_over = True
            return self.reward, game_over, self.score

        self.draw()
        self.Clock.tick(60)
        return self.reward, game_over, self.score

    def get_state(self):
        states = [
            self.ball.rect.centerx<self.bat.rect.left-self.bat.rect.width,
            self.ball.rect.centerx<self.bat.rect.left,
            self.ball.rect.centerx>self.bat.rect.right,
            self.ball.rect.centerx>self.bat.rect.right+self.bat.rect.width,
            self.ball.rect.centerx>self.bat.rect.centerx
        ]
        return np.array(states, dtype=float)

