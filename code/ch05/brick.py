import pygame
from pygame.locals import *
import random
from  math import radians, sin, cos, asin

class Bat:
    def __init__(self,playerY=540):
        self.image = pygame.image.load('bat.png')
        self.rect = self.image.get_rect()
        self.mousey = playerY

    def draw(self, surface):
        surface.blit(self.image, self.rect)
    
    def update(self,win_width):
        mousex, _ = pygame.mouse.get_pos()
        if (mousex > win_width - self.rect.width):
            mousex = win_width - self.rect.width
        self.rect.topleft = (mousex, self.mousey)


# ball init
class Ball:
    
    def __init__(self,win_width):
        self.image = pygame.image.load('ball.png')
        self.rect = self.image.get_rect()
        self.reset(win_width)

    def reset(self,win_width,startY=220,speed=5, degree=45):
        self.served = False
        self.positionX = random.randint(0,win_width)
        self.positionY = startY
        self.rect.topleft = (self.positionX, self.positionY)
        self.speed = speed
        self.speedX = self.speed * sin(radians(degree))
        self.speedY = self.speed * cos(radians(degree))
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update(self,win_width):
        if self.served:    
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
        self.bat = Bat()
        self.ball = Ball(self.Win_width) 
        self.bricks = Bricks() 
        self.font = pygame.font.SysFont('microsoftyahei',26)
        self.score = 0
        self.Clock = pygame.time.Clock()
        self.fps = 60
        self.running = True
        pygame.display.set_caption('Bricks')
        

    def bat_collision(self):
        if self.ball.rect.colliderect(self.bat.rect):
            self.ball.rect.bottom = self.bat.mousey
            self.ball.speed += 0.1
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
            if len(self.bricks.contains)==0:
                self.running = False 
    
    def check_failed(self):
        if self.ball.rect.bottom >= self.Win_height:
            self.ball.reset(self.Win_width)
            self.score = 0

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


    def play(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False

                if event.type == MOUSEBUTTONUP and not self.ball.served:
                    self.ball.served = True

            self.bat.update(self.Win_width)
            self.ball.update(self.Win_width)
            self.check_failed()
            self.bat_collision()
            self.bricks_collision()
            self.draw()
            self.Clock.tick(self.fps)

        pygame.quit()
        print('Good Job! Final Score:', self.score)


if __name__ == '__main__':
    game = Game()
    game.play()
