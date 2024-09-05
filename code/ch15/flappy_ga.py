# 基于遗传算法训练的游戏AI

import pygame, sys
from pygame.locals import *
import random
import numpy as np
import torch.nn.functional as F
import torch 
import  torch.nn as nn
from copy import deepcopy


class Linear_Net(nn.Module):
	
	def __init__(self, input_size, hidden_size, output_size):
		super().__init__()
		self.linear1 = nn.Linear(input_size, hidden_size)
		self.linear2 = nn.Linear(hidden_size, output_size)

	def forward(self, x):
		x = F.relu(self.linear1(x))
		x = self.linear2(x)
		return x

	def get_weight(self):
		return deepcopy([self.linear1.weight.data,
				self.linear1.bias.data,
				self.linear2.weight.data,
				self.linear2.bias.data])

	def set_weight(self,weights):
		weights = deepcopy(weights)
		self.linear1.weight = nn.Parameter(weights[0])
		self.linear1.bias = nn.Parameter(weights[1])
		self.linear2.weight = nn.Parameter(weights[2])
		self.linear2.bias = nn.Parameter(weights[3])


class Bird(pygame.sprite.Sprite):
	cap = 10
	input_size = 3
	hidden_size = 16
	output_size = 2
	def __init__(self, x, y):
		super().__init__()
		self.images = []
		self.index = 0
		self.counter = 0
		self.vel = 0
		self.failed = False
		for num in range (1, 4):
			img = pygame.image.load(f"resources/bird{num}.png")
			self.images.append(img)
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.wing = pygame.mixer.Sound('resources\wing.wav')

		self.fitness = 0
		self.score = 0
		self.model = Linear_Net(Bird.input_size, Bird.hidden_size, Bird.output_size)
	
	def handle_action(self,action):
		if action == 1:
			self.vel = -1 * self.cap
			self.wing.play()

	def get_action(self, state):
		prediction = self.model(torch.Tensor(state)) 
		prediction = prediction.detach().numpy().squeeze()
		move = prediction.argmax()
		return move

	def get_state(self, observed):
		return np.array([int(self.vel)/Bird.cap, 
					(self.rect.top - observed['pipe_dist_top'])/Pipe.pipe_gap,
					(observed['pipe_dist_bottom'] - self.rect.bottom)/Pipe.pipe_gap],
					dtype=float)

	def get_fitness(self, observed):
		if (self.rect.top - observed['pipe_dist_top']>0 and 
			observed['pipe_dist_bottom'] - self.rect.bottom > 0):
			self.fitness += 1

	def touch_ground(self):
		return self.rect.bottom >= Game.ground_y

	def animation(self):
		flap_cooldown = 5
		self.counter += 1
		if self.counter > flap_cooldown:
			self.counter = 0
			self.index + 1
			self.index = (self.index + 1) % 3
			self.image = self.images[self.index]
		self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)

	def check_collision(self):
		if self.rect.top < 0 or self.rect.bottom >= Game.ground_y:
			self.failed = True

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

		self.check_collision()


class Pipe(pygame.sprite.Sprite):
	scroll_speed = 4
	pipe_gap = 180
	def __init__(self, x, y, is_top):
		super().__init__()
		self.passed = False
		self.is_top = is_top
		self.image = pygame.image.load("resources/pipe.png")
		self.rect = self.image.get_rect()

		if is_top == True:
			self.image = pygame.transform.flip(self.image, False, True)
			self.rect.bottomleft = [x, y - int(Pipe.pipe_gap / 2)]
		else:
			self.rect.topleft = [x, y + int(Pipe.pipe_gap / 2)]

	def update(self):
		self.rect.x -= Pipe.scroll_speed
		if self.rect.right < 0:
			self.kill()




class Game():
	ground_y = 650
	Width = 600
	Height = 800
	parameter_len = (Bird.input_size+1)*Bird.hidden_size+(Bird.hidden_size+1)*Bird.output_size
	
	def __init__(self,Width=600,Height=800):
		pygame.init()
		self.Win_width , self.Win_height = (Width, Height)
		self.surface = pygame.display.set_mode((self.Win_width, self.Win_height))
		self.ground_x = 0
		self.score = 0
		self.pipe_counter = 0
		self.observed = dict()
		self.Clock = pygame.time.Clock()
		self.font = pygame.font.Font('resources/LuckiestGuy-Regular.ttf', 28)
		self.images = self.loadImages()
		self.sounds = self.loadSounds()

		self.n_generations = 100
		self.generation_size = 10 
		self.weights = []
		self.fitness = []

		self.pipe_group = pygame.sprite.Group()
		self.bird_group = pygame.sprite.Group()
		self.new_birds()
		self.new_pipes(time=0)
		self.get_pipe_dist()
		pygame.display.set_caption('Flappy Bird')
		pygame.mixer.music.load('resources/BGMUSIC.mp3')
		pygame.mixer.music.play()


	def new_birds(self):
		for i in range(self.generation_size):
			bird_height = random.randint(-200, 200)
			bird = Bird(100, int(self.Win_height / 2+bird_height))
			self.bird_group.add(bird)

	def loadImages(self):
		background = pygame.image.load('resources/bg.png')
		ground = pygame.image.load('resources/ground.png')
		return {'bg':background, 'ground':ground}
	
	def loadSounds(self):
		hit = pygame.mixer.Sound('resources\hit.wav')
		point = pygame.mixer.Sound('resources\point.wav')
		return {'hit':hit, 'point':point}

	def reset(self,next_generation):
		self.score = 0
		self.fitness = []
		self.weights = []
		self.pipe_group.empty()
		self.bird_group.empty()
		self.new_pipes(time=0)
		self.get_pipe_dist()
		self.new_birds()
		for i, bird in enumerate(self.bird_group.sprites()):
			bird.model.set_weight(next_generation[i])
		pygame.mixer.music.play(-1)

	def handle_collision(self):
		collide_info = pygame.sprite.groupcollide(self.bird_group, self.pipe_group, False, False)
		collide_bird = collide_info.keys()
		if len(collide_bird)>0:
			self.sounds['hit'].play()
			for bird in collide_bird:
				bird.failed = True

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
					

	def pipe_update(self):
		self.new_pipes()
		self.pipe_group.update()
		if len(self.pipe_group)>0:
			self.get_pipe_dist()

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


	def birds_update(self):
		for i, bird in enumerate(self.bird_group.sprites()):
			if not bird.failed:
				self.score += bird.score
				state = bird.get_state(self.observed)
				action = bird.get_action(state)
				bird.update(action)
				bird.get_fitness(self.observed)
				if bird.rect.left >= self.observed['pipe_dist_right']:
					bird.score += 1
					self.pipe_group.sprites()[0].passed = True
					self.pipe_group.sprites()[1].passed = True
					self.sounds['point'].play()
				if bird.score > 50:
					bird.failed = True
			
			if bird.failed:
				self.weights.append(bird.model.get_weight())
				self.fitness.append(bird.fitness)
				bird.kill()
			
			
	def play_step(self):
		game_over = False
		self.score = 0

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
	
		self.birds_update()
		self.handle_collision()

		if len(self.bird_group) == 0 or self.score>50:
			game_over = True
			return game_over, self.score

		self.pipe_update()
		self.ground_update()
		self.draw()
		self.Clock.tick(60)
		return game_over, self.score 
	
	
class GATrainer:
	def __init__(self):
		self.game = Game()
		self.generate_num = 0
		self.mutate_pop_rate = 0.2
		self.mutate_net_rate = 0.1

	@staticmethod
	def list2tensor(weights):
		return torch.concat([weights[0].flatten(),weights[1],
								weights[2].flatten(),weights[3]])

	@staticmethod
	def tensor2list(weights):
		output_weights = []
		index  = [Bird.input_size*Bird.hidden_size, 
				Bird.input_size*Bird.hidden_size+Bird.hidden_size,
				Bird.input_size*Bird.hidden_size+Bird.hidden_size+Bird.hidden_size*Bird.output_size]
		output_weights.append(weights[:index[0]].reshape(Bird.hidden_size,Bird.input_size))
		output_weights.append(weights[index[0]:index[1]])
		output_weights.append(weights[index[1]:index[2]].reshape(Bird.output_size,Bird.hidden_size))
		output_weights.append(weights[index[2]:])
		return output_weights

	def cross_mutate(self,weights_1, weights_2):
		weights_1 = GATrainer.list2tensor(weights_1)
		weights_2 = GATrainer.list2tensor(weights_2)
		crossover_idx = random.randint(0, Game.parameter_len-1)
		new_weights = torch.concat([weights_1[:crossover_idx] , weights_2[crossover_idx:]])
		if (random.randint(0,self.game.generation_size-1) <= 
      		self.game.generation_size*self.mutate_pop_rate):
			mutate_num = int(self.mutate_net_rate*Game.parameter_len)
			for _ in range(mutate_num):
				i = random.randint(0,Game.parameter_len-1)
				new_weights[i] += torch.randn(1).numpy()
		output_weights = GATrainer.tensor2list(new_weights)
		return 	output_weights
	
	@staticmethod
	def fitness_prob(fitness):
		fitness = np.array(fitness)
		return fitness/np.sum(fitness)

	def reproduce(self):
		next_generation = []
		prob = GATrainer.fitness_prob(self.game.fitness) 
		second_index, first_index= list(np.argsort(prob)[-2:])
		next_generation.append(self.game.weights[first_index])
		next_generation.append(self.game.weights[second_index])
		for _ in range(self.game.generation_size - 2):
			p1, p2 = np.random.choice(len(prob),size=2, replace=False,p=prob) 
			next_generation.append(self.cross_mutate(self.game.weights[p1],self.game.weights[p2]))
		return next_generation

	def run_GA(self):
		while True:
			game_over, score  = self.game.play_step()
			if game_over :
				print(f"generate {self.generate_num} average fitness: {sum(self.game.fitness)/10}")
				next_generation = self.reproduce()
				self.game.reset(next_generation)
				self.generate_num += 1
				

if __name__ == "__main__":
	trainer = GATrainer()
	trainer.run_GA()

