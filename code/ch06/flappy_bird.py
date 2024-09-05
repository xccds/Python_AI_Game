import pygame
from pygame.locals import *
import random

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
		self.clicked = False
		for num in range (1, 4):
			img = pygame.image.load(f"resources/bird{num}.png")
			self.images.append(img)
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.wing = pygame.mixer.Sound('resources/wing.wav')

	def handle_input(self):
		if pygame.mouse.get_pressed()[0] == 1 and not self.clicked :
			self.clicked = True
			self.vel = -1 * self.cap
			self.wing.play()
		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

	def animation(self):
		flap_cooldown = 5
		self.counter += 1
		if self.counter > flap_cooldown:
			self.counter = 0
			self.index = (self.index + 1) % 3
			self.image = self.images[self.index]
		self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)

	def touch_ground(self):
		return self.rect.bottom >= Game.ground_y

	def update(self):
		if self.flying : 
			self.handle_input()
			self.vel += 0.5
			if self.vel > 8:
				self.vel = 8
			if not self.touch_ground():
				self.rect.y += int(self.vel)

		if not self.failed:
			self.animation()
		else:
			#point the bird at the ground
			self.image = pygame.transform.rotate(self.images[self.index], -90)



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

class Button:

	def __init__(self, x, y):
		self.image = pygame.image.load('resources/restart.png')
		self.rect = self.image.get_rect(centerx=x,centery=y)

	def pressed(self, event):
		pressed = False
		if event.type == MOUSEBUTTONDOWN:
			pos = pygame.mouse.get_pos()
			if self.rect.collidepoint(pos):
				pressed = True
		return pressed
 
	def draw(self,surface):
		surface.blit(self.image, self.rect)

class Game():
	ground_y = 650
	
	def __init__(self,Width=600,Height=800):
		pygame.init()
		self.Win_width , self.Win_height = (Width, Height)
		self.surface = pygame.display.set_mode((self.Win_width, self.Win_height))
		self.ground_x = 0
		self.score = 0
		self.pipe_counter = 0
		self.observed = dict()
		self.Clock = pygame.time.Clock()
		self.fps = 60
		self.font = pygame.font.Font('resources/LuckiestGuy-Regular.ttf', 28)
		self.images = self.loadImages()
		self.sounds = self.loadSounds()
		self.pipe_group = pygame.sprite.Group()
		self.bird_group = pygame.sprite.Group()
		self.flappy = Bird(100, self.ground_y // 2)
		self.bird_group.add(self.flappy)
		self.new_pipes(time=0)
		self.button = Button(self.Win_width//2 , self.Win_height//2 )
		pygame.display.set_caption('Flappy Bird')
		pygame.mixer.music.load('resources/BGMUSIC.mp3')
		pygame.mixer.music.play(-1)
	
	def loadImages(self):
		background = pygame.image.load('resources/bg.png')
		ground = pygame.image.load('resources/ground.png')
		return {'bg':background, 'ground':ground}
	
	def loadSounds(self):
		hit = pygame.mixer.Sound('resources/hit.wav')
		point = pygame.mixer.Sound('resources/point.wav')
		return {'hit':hit, 'point':point}

	def reset_game(self):
		self.pipe_group.empty()
		self.new_pipes(time=0)
		self.bird_group.empty()
		self.flappy = Bird(100, self.ground_y // 2)
		self.bird_group.add(self.flappy)
		self.score = 0
		self.observed = dict()
		pygame.mixer.music.play(-1)

	def start_flying(self,event):
		if (event.type == pygame.MOUSEBUTTONDOWN 
			and not self.flappy.flying
			and not self.flappy.failed):
			self.flappy.flying = True

	def game_restart(self,event):
		if (self.flappy.failed 
			and self.button.pressed(event)):
				self.reset_game()	

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

	def check_failed(self):
		if self.flappy.failed:
			pygame.mixer.music.stop()
			if self.flappy.touch_ground():
				self.button.draw(self.surface)
				self.flappy.flying = False

	def play_step(self):
		game_over = False
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				game_over = True
			self.start_flying(event)
			self.game_restart(event)
		self.bird_group.update()
		if not self.flappy.failed and self.flappy.flying:
			self.handle_collision()
			self.pipe_update()
			self.ground_update()
		self.draw()
		self.check_failed()
		pygame.display.update()
		self.Clock.tick(self.fps)
		return game_over, self.score 

if __name__ == '__main__':
	game = Game()
	while True:
		game_over, score  = game.play_step()
		if game_over == True:
			break

	print('Final Score', score)
	pygame.quit()
