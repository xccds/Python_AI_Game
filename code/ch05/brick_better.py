# 优化的砖块游戏版本
# 增加游戏音效和爆炸动画
# 使用resources类来管理游戏资源

import pygame
from pygame.locals import *
import random
from  math import radians, sin, cos, asin

class Resources:

	def __init__(self):
		self.explosion = []
		for i in range(1,5):
			self.explosion.append(pygame.image.load(f"item-feedback/item-feedback-{i}.png"))
 
		self.bat_img = pygame.image.load('bat.png')
		self.ball_img = pygame.image.load('ball.png')
		self.brick_img = pygame.image.load('brick.png')

		self.point = pygame.mixer.Sound('point.wav')
		self.pong = pygame.mixer.Sound('pong.ogg')
		self.failed = pygame.mixer.Sound('failed.wav')


class Bat:
	def __init__(self, resource,playerY=540):
		self.image = resource.bat_img
		self.rect = self.image.get_rect()
		self.mousey = playerY

	def draw(self, surface):
		surface.blit(self.image, self.rect)
	
	def update(self,win_width):
		mousex, _ = pygame.mouse.get_pos()
		self.rect.center = (mousex, self.mousey)
		if self.rect.right > win_width:
			self.rect.right = win_width
		if self.rect.left < 0:
			self.rect.left = 0


# ball init
class Ball:
	
	def __init__(self,resource, win_width):
		self.image = resource.ball_img
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

	def speed_up(self):
		self.speed += 0.5

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

	def __init__(self,resource,row=5, col=12):
		self.image = resource.brick_img
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


class Explosion:

	def __init__(self, resource, position):
		self.anim = resource.explosion
		self.index = 0
		self.image = self.anim[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = position
		self.finished = False

	def update(self):
		self.animation(self.anim)

	def animation(self, anim_img, anim_speed=0.2):
		self.index += anim_speed
		if self.index >= len(anim_img):
			self.finished = True
			return
		self.image = anim_img[int(self.index)]
	

	def draw(self, screen):
		screen.blit(self.image, self.rect)

class Game:
	WHITE = (255, 255, 255)
	BLACK = (0, 0, 0)
	GRAY = (112,128,144)
	GREEN = (127,255,0)

	def __init__(self, Width=800,Height=600):
		pygame.init()
		self.Win_width , self.Win_height = (Width, Height)
		self.surface = pygame.display.set_mode((self.Win_width, self.Win_height))
		self.resource = Resources()
		self.bat = Bat(self.resource)
		self.ball = Ball(self.resource,self.Win_width) 
		self.bricks = Bricks(self.resource) 
		self.font = pygame.font.SysFont('microsoftyahei',26)
		self.score = 0
		self.Clock = pygame.time.Clock()
		self.fps = 60
		self.running = True
	
		self.explosions = []
		pygame.display.set_caption('Bricks')
		pygame.mouse.set_visible(False) # hide the mouse cursor
		
		
	def bat_collision(self):
		if self.ball.rect.colliderect(self.bat.rect):
			self.resource.pong.play()
			self.ball.speed_up()
			self.ball.rect.bottom = self.bat.mousey
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
			self.resource.point.play()
			self.explosions.append(Explosion(self.resource,brick.center))
			if len(self.bricks.contains)==0:
				self.running = False 
		
	def update_explosions(self):
		for e in self.explosions.copy():
			if e.finished:
				self.explosions.remove(e)
			else:
				e.update()
	
	def check_failed(self):
		if self.ball.rect.bottom >= self.Win_height:
			self.resource.failed.play()
			self.ball.reset(self.Win_width)
			self.score = 0

	def draw_data(self):
		score_text = "得分：{score}".format(score=self.score)
		score_img = self.font.render(score_text, 1, Game.WHITE)
		score_rect = score_img.get_rect(centerx=self.Win_width//2, top=5)
		self.surface.blit(score_img, score_rect)

	def draw(self):
		self.surface.fill(Game.GRAY)
		self.draw_data()
		self.bricks.draw(self.surface)
		self.bat.draw(self.surface)
		self.ball.draw(self.surface)
		for e in self.explosions:
			e.draw(self.surface)
		pygame.display.update()

	def update(self):
		self.bat.update(self.Win_width)
		self.ball.update(self.Win_width)
		self.check_failed()
		self.bat_collision()
		self.bricks_collision()
		self.update_explosions()

	def play(self):
		while self.running:
			for event in pygame.event.get():
				if event.type == QUIT:
					self.running = False

				if event.type == MOUSEBUTTONUP and not self.ball.served:
					self.ball.served = True

			self.update()
			self.draw()
			self.Clock.tick(self.fps)

		pygame.quit()
		print('Good Job! Final Score:', self.score)


if __name__ == '__main__':
	game = Game()
	game.play()
