# 优化的flappy_bird游戏版本
# 使用枚举值Enum来处理bird的各种状态
# 让背景可以缓慢地移动，实现景深效果


import pygame
import random
from enum import Enum

class Resources:
	def __init__(self):
		self.bird_images = []
		for num in range (1, 4):
			img = pygame.image.load(f"resources/bird{num}.png")
			self.bird_images.append(img)
		self.ground_img = pygame.image.load('resources/ground.png')
		self.background = pygame.image.load('resources/bg.png')
		self.pipe_image = pygame.image.load("resources/pipe.png")
		self.button_image = pygame.image.load('resources/restart.png')


		self.wing_sound = pygame.mixer.Sound('resources/wing.wav')
		self.hit_sound = pygame.mixer.Sound('resources/hit.wav')
		self.point_sound = pygame.mixer.Sound('resources/point.wav')

		pygame.mixer.music.load('resources/BGMUSIC.mp3')
		pygame.mixer.music.set_volume(0.4)


 
class State(Enum):
    waiting = 1
    flying = 2
    falling = 3
    gameover = 4

class Bird(pygame.sprite.Sprite):

	def __init__(self, x, y, resources):
		super().__init__()
		self.x = x
		self.y = y
		self.images = resources.bird_images
		self.index = 0
		self.counter = 0
		self.vel = 0
		self.cap = 10
		self.state = State.waiting
		self.clicked = False
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = (self.x, self.y)
		self.wing = resources.wing_sound

	def handle_input(self):
		if pygame.mouse.get_pressed()[0] == 1 and not self.clicked :
			self.clicked = True
			self.vel = -1 * self.cap
			self.wing.play()
		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

	def animation(self, anim_speed=0.2):
		self.index += anim_speed
		if self.index >= len(self.images):
			self.index = 0
		self.image = pygame.transform.rotate(self.images[int(self.index)], self.vel * -2)

	def touch_ground(self):
		return self.rect.bottom >= Game.ground_y

	def move(self):
		self.vel += 0.5
		if self.vel > 8:
			self.vel = 8
		if not self.touch_ground():
			self.y += self.vel
			self.rect.centery = self.y

	def update(self):
		if self.state == State.waiting:
			self.animation()

		elif self.state == State.flying:
			self.handle_input()
			self.move() 
			self.animation()

		elif self.state == State.falling:
			self.image = pygame.transform.rotate(self.images[int(self.index)], -90)
			self.move()

	def draw(self, screen):
			screen.blit(self.image, self.rect)

class Pipe(pygame.sprite.Sprite):
	scroll_speed = 4
	pipe_gap = 180

	def __init__(self, x, y, is_top, resources):
		super().__init__()
		self.passed = False
		self.is_top = is_top
		self.image = resources.pipe_image
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

class Background(pygame.sprite.Sprite):
	def __init__(self, x, y, resources):
		super().__init__()
		self.image = resources.background
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

	# move the background slow for Parallax scrolling
	def update(self):
		self.rect.x -= 1
		if self.rect.right < 0:
			self.kill()


class Ground(pygame.sprite.Sprite):
	def __init__(self, x, y, resources):
		super().__init__()
		self.image = resources.ground_img
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

	def update(self):
		self.rect.x -= 4
		if abs(self.rect.x) >35:
			self.rect.x = 0

	def draw(self, screen):
		screen.blit(self.image, self.rect)

class Button:

	def __init__(self, x, y, resources):
		self.image = resources.button_image
		self.rect = self.image.get_rect(centerx=x,centery=y)

	def pressed(self, event):
		pressed = False
		if event.type == pygame.MOUSEBUTTONDOWN:
			pos = pygame.mouse.get_pos()
			if self.rect.collidepoint(pos):
				pressed = True
		return pressed
 
	def draw(self,surface):
		surface.blit(self.image, self.rect)

class Text_Game:

	def __init__(self,text,position,size=28):
		self.font = pygame.font.Font('resources/LuckiestGuy-Regular.ttf', size)
		self.text = self.font.render(text, True, Game.WHITE)
		self.rect = self.text.get_rect()
		self.rect.center = position

	def update(self, text):
		self.text = self.font.render(text, True, Game.WHITE)

	def draw(self, screen):
		screen.blit(self.text , self.rect)

class Game:
	WHITE = (255, 255, 255)
	BLACK = (0, 0, 0)
	GRAY = (127, 127, 127)
	BLUE = (135,206,250)
	ground_y = 650
	
	def __init__(self,Width=600,Height=800):
		pygame.init()
		self.Win_width , self.Win_height = (Width, Height)
		self.screen = pygame.display.set_mode((self.Win_width, self.Win_height))
		self.Clock = pygame.time.Clock()
		self.fps = 60
		self.running = True
		self.resources = Resources()
		self.score_text = Text_Game('Score: 0', (80, 20))
		self.flappy = Bird(100, self.ground_y // 2, self.resources)
		self.button = Button(self.Win_width//2 , self.Win_height//2 , self.resources)
		self.reset_game()
		pygame.display.set_caption('Flappy Bird')
	
	def reset_game(self):
		pygame.mixer.music.play(-1)
		self.pipe_counter = 0
		self.pipe_group = pygame.sprite.Group()
		self.new_pipes(time=0)
		self.flappy = Bird(100, self.ground_y // 2, self.resources)
		self.background = Background(0, 0, self.resources)
		self.bg_group = pygame.sprite.Group(self.background)
		self.ground = Ground(0, Game.ground_y, self.resources)
		self.score = 0
		self.observed = dict()

	def start_flying(self,event):
		if (event.type == pygame.MOUSEBUTTONDOWN 
			and self.flappy.state == State.waiting):
			self.flappy.state = State.flying

	def game_restart(self,event):
		if (self.flappy.state== State.gameover
			and self.button.pressed(event)):
				self.reset_game()		

	def handle_collision(self):
		hit_list = pygame.sprite.spritecollide(self.flappy, self.pipe_group, False) 
		if (len(hit_list)>0 or 
	  		self.flappy.rect.top < 0 or
			self.flappy.rect.bottom >= Game.ground_y):
			self.failed()

	def failed(self):
		self.flappy.state = State.falling
		self.resources.hit_sound.play()
		pygame.mixer.music.stop()

	def new_pipes(self, time = 90):
		self.pipe_counter += 1
		if self.pipe_counter >= time:
			pipe_height = random.randint(-150, 150)
			top_pipe = Pipe(self.Win_width,  self.ground_y // 2 + pipe_height, True,self.resources)
			btm_pipe = Pipe(self.Win_width, self.ground_y // 2 + pipe_height, False,self.resources)
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
			self.resources.point_sound.play()

	def pipe_update(self):
		self.new_pipes()
		self.pipe_group.update()
		if len(self.pipe_group)>0:
			self.get_pipe_dist()
			self.check_pipe_pass()


	def draw(self):
		self.bg_group.draw(self.screen)
		self.pipe_group.draw(self.screen)
		self.flappy.draw(self.screen)
		self.ground.draw(self.screen)
		self.score_text.draw(self.screen)
		if self.flappy.state == State.gameover:
			self.button.draw(self.screen)
		pygame.display.update()

	def check_failed(self):
		if self.flappy.state == State.falling:
			if self.flappy.touch_ground():
				self.flappy.state = State.gameover

	# once the background will out of the screen, create a new one
	def bg_update(self):
		if (len(self.bg_group)==1 and 
	  		self.bg_group.sprites()[0].rect.right <= self.Win_width+10):
			self.bg_group.add(Background(self.Win_width, 0, self.resources))
		self.bg_group.update()

	def update(self):
		self.flappy.update()
		if self.flappy.state == State.flying:
			self.handle_collision()
			self.pipe_update()
			self.ground.update()
			self.bg_update()
			
		self.score_text.update(f'Score: {self.score}')
		self.check_failed()


	def play(self):
		while self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
				self.start_flying(event)
				self.game_restart(event)
				
			self.update()
			self.draw()
			self.Clock.tick(self.fps)
		pygame.quit()


if __name__ == '__main__':
	game = Game()
	game.play()
