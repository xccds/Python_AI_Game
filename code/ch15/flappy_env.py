import pygame, sys
from pygame.locals import *
import random
import numpy as np

class Bird(pygame.sprite.Sprite):

	def __init__(self, x, y):
		super().__init__()
		self.images = []
		self.index = 0
		self.counter = 0
		self.vel = 0
		self.cap = 10
		self.flying = False
		self.failed = False
		for num in range (1, 4):
			img = pygame.image.load(f"resources/bird{num}.png")
			self.images.append(img)
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.wing = pygame.mixer.Sound('resources\wing.wav')

	def touch_ground(self):
		return self.rect.bottom >= Game.ground_y

	def animation(self):
		flap_cooldown = 5
		self.counter += 1
		if self.counter > flap_cooldown:
			self.counter = 0
			self.index = (self.index + 1) % 3
			self.image = self.images[self.index]
		self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)

	def handle_action(self,action):
		if action == 1:
			self.vel = -1 * self.cap
			self.wing.play()

	def update(self,action):
		#apply gravity
		self.vel += 0.5
		if self.vel > 8:
			self.vel = 8
		if not self.touch_ground():
			self.rect.y += int(self.vel)

		if not self.failed:
			self.handle_action(action)
			self.animation()
		

class Pipe(pygame.sprite.Sprite):
	scroll_speed = 4
	pipe_gap = 180
	def __init__(self, x, y, is_top):
		super().__init__()
		self.passed = False
		self.is_top = is_top
		self.image = pygame.image.load("resources/pipe.png")
		self.rect = self.image.get_rect()
		
		if is_top :
			self.image = pygame.transform.flip(self.image, False, True)
			self.rect.bottomleft = [x, y - Pipe.pipe_gap // 2]
		else:
			self.rect.topleft = [x, y + Pipe.pipe_gap // 2]

	def update(self):
		self.rect.x -= Pipe.scroll_speed
		if self.rect.right < 0:
			self.kill()



class Game():
	ground_y = 650
	nS = 3
	nA = 2
	def __init__(self,Width=600,Height=800):
		pygame.init()
		self.Win_width , self.Win_height = (Width, Height)
		self.surface = pygame.display.set_mode((self.Win_width, self.Win_height))
		self.ground_x = 0
		self.score = 0
		self.pipe_counter = 0
		self.reward = 0
		self.observed = dict()
		self.Clock = pygame.time.Clock()
		self.font = pygame.font.Font('resources/LuckiestGuy-Regular.ttf', 28)
		self.images = self.loadImages()
		self.sounds = self.loadSounds()
		self.pipe_group = pygame.sprite.Group()
		self.bird_group = pygame.sprite.Group()
		self.flappy = Bird(100, self.Win_height//2 + random.randrange(-200,200))
		self.bird_group.add(self.flappy)
		self.new_pipes(time=0)
		self.get_pipe_dist()
		pygame.display.set_caption('Flappy Bird')
		pygame.mixer.music.load('resources/BGMUSIC.mp3')
		pygame.mixer.music.play()
	
	def loadImages(self):
		background = pygame.image.load('resources/bg.png')
		ground = pygame.image.load('resources/ground.png')
		return {'bg':background, 'ground':ground}
	
	def loadSounds(self):
		hit = pygame.mixer.Sound('resources\hit.wav')
		point = pygame.mixer.Sound('resources\point.wav')
		return {'hit':hit, 'point':point}

	def reset(self):
		self.score = 0
		self.reward = 0
		self.flappy.rect.x = 100
		self.flappy.rect.y = self.Win_height//2 + random.randrange(-200,200)
		self.flappy.failed = False
		self.pipe_group.empty()
		self.new_pipes(time=0)
		self.get_pipe_dist()
		pygame.mixer.music.play()

	def handle_collision(self):
		if (pygame.sprite.groupcollide(self.bird_group, self.pipe_group, False, False) 
			or self.flappy.rect.top < 0 
			or self.flappy.rect.bottom >= Game.ground_y):
			self.flappy.failed = True
			self.sounds['hit'].play()
			pygame.mixer.music.stop()

	def ground_update(self):
		self.ground_x -= Pipe.scroll_speed
		if abs(self.ground_x) > 35:
			self.ground_x = 0

	def new_pipes(self, time = 90):
		self.pipe_counter += 1
		if self.pipe_counter >= time:
			pipe_height = random.randint(-150, 150)
			top_pipe = Pipe(self.Win_width,  self.ground_y // 2 + pipe_height, True)
			btm_pipe = Pipe(self.Win_width, self.ground_y // 2 + pipe_height, False)
			self.pipe_group.add(top_pipe)
			self.pipe_group.add(btm_pipe)
			self.pipe_counter = 0

	def get_pipe_dist(self):
		pipe_2 = [pipe for pipe in self.pipe_group.sprites() if pipe.passed==False][:2]
		for pipe in pipe_2:
			if pipe.is_top:
				self.observed['pipe_dist_right'] = pipe.rect.right 
				self.observed['pipe_dist_top'] = pipe.rect.bottom
			else:
				self.observed['pipe_dist_bottom'] = pipe.rect.top
			
	def check_pipe_pass(self):
		if self.flappy.rect.left >= self.observed['pipe_dist_right']:
			self.score += 1
			self.reward = 10
			self.pipe_group.sprites()[0].passed = True
			self.pipe_group.sprites()[1].passed = True
			self.sounds['point'].play()

	def pipe_update(self):
		self.new_pipes()
		self.pipe_group.update()
		if len(self.pipe_group)>0:
			self.get_pipe_dist()
			self.check_pipe_pass()

	def draw_text(self,text,color,x,y):
		img = self.font.render(text, True, color)
		self.surface.blit(img,(x,y))

	def draw(self):
		self.surface.blit(self.images['bg'],(0,0))
		self.pipe_group.draw(self.surface)
		self.bird_group.draw(self.surface)
		self.surface.blit(self.images['ground'],(self.ground_x,self.ground_y))
		self.draw_text(f'score: {self.score}', (255, 255, 255), 20, 20)	
		pygame.display.update()

	def flying_good(self):
		if (self.flappy.rect.top >= self.observed['pipe_dist_top'] 
		and self.flappy.rect.bottom <= self.observed['pipe_dist_bottom'] ):
			self.reward = 1

	def play_step(self,action):
		game_over = False
		self.reward = -1
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

		self.bird_group.update(action)
		self.handle_collision()

		if self.flappy.failed:
			game_over = True
			pygame.mixer.music.stop()
			self.reward = -20
			return self.reward, game_over, self.score
		
		self.pipe_update()
		self.ground_update()
		self.flying_good()
		self.draw()
		self.Clock.tick(60)
		return self.reward, game_over, self.score 
	

	def get_state(self):
		states =np.array([float(self.flappy.vel)/self.flappy.cap, 
				(self.flappy.rect.top-self.observed['pipe_dist_top'])/Pipe.pipe_gap,
				(self.observed['pipe_dist_bottom'] - self.flappy.rect.bottom)/Pipe.pipe_gap
				],dtype=float)
		return states


if __name__ == "__main__":
	game = Game()
	while True:
		action = 0
		state = game.get_state()
		if state[2]  < 0.1:
			action = 1
		print(state)

		reward, game_over, score  = game.play_step(action)
		print(reward)
		if game_over == True:
			break

	print('Final Score', score)
	pygame.quit()
