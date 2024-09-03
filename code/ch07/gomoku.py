from collections import namedtuple
import pygame
from pygame.locals import *
from board import Board

Output = namedtuple('Output', 'action, value')

class Button:

	def __init__(self,x,y,width,height,text=''):
		self.color = (245, 245, 245)
		self.rect = Rect(x,y,width,height)
		self.text = text

	def pressed(self, pos):
		return self.rect.collidepoint(pos)

	def draw(self,surface,textsize):
		pygame.draw.rect(surface, self.color, self.rect)
		pygame.draw.rect(surface, Game.BLACK, self.rect, width=1)
		Game.draw_text(surface,self.text, self.rect.center, textsize)
		

class Board_Area:

	def __init__(self, unitsize, boardsize):
		self.color = (254, 185, 120)
		self.UnitSize = unitsize
		self.BoardSize = boardsize
		self.board_lenth = self.UnitSize * self.BoardSize
		self.rect = Rect(self.UnitSize, self.UnitSize, self.board_lenth, self.board_lenth)

	def draw(self, surface,textsize):
		pygame.draw.rect(surface, self.color, self.rect)
		for i in range(self.BoardSize):
			start = self.UnitSize * (i + 0.5)
			pygame.draw.line(surface, Game.BLACK, (start + self.UnitSize, self.UnitSize*1.5),
							 (start + self.UnitSize, self.board_lenth + self.UnitSize*0.5))
			pygame.draw.line(surface, Game.BLACK, (self.UnitSize*1.5, start + self.UnitSize),
							 (self.board_lenth + self.UnitSize*0.5, start + self.UnitSize))
			Game.draw_text(surface, text = self.BoardSize - i - 1, position= (self.UnitSize / 2, start + self.UnitSize), text_height=textsize)
			Game.draw_text(surface,text =i, position=(start + self.UnitSize, self.UnitSize / 2), text_height=textsize)

class Message_Area:

	def __init__(self, x, y, width, height):
		self.rect = Rect(x,y,width,height)

	def draw(self, surface, text, textsize):
		pygame.draw.rect(surface, Game.BackGround, self.rect)
		Game.draw_text(surface,text, self.rect.center, textsize)
		pygame.display.update()


class Game:

	WHITE = (255, 255, 255)
	BLACK = (0,0,0)
	BackGround =(197, 227, 205)

	def __init__(self, width=9, height=9, n_in_row=5):
		pygame.init()
		self.board = Board(width, height, n_in_row)
		self.BoardSize = width
		self.UnitSize = 45      # the basic size of all elements, try a different value!
		self.TextSize = int(self.UnitSize * 0.3)
		self.buttons = dict()
		self.last_move_player = None 
		self.game_end = False
		self.init_screen()
		self.restart_game()

	def init_screen(self):
		self.ScreenSize = (self.BoardSize * self.UnitSize + 2 * self.UnitSize,
						   self.BoardSize * self.UnitSize + 3 * self.UnitSize)
		self.surface = pygame.display.set_mode(self.ScreenSize)
		pygame.display.set_caption('Gomoku')
		self.buttons['RestartGame'] = Button(0, self.ScreenSize[1] - self.UnitSize, self.UnitSize*3, self.UnitSize,text = "再战江湖")
		self.buttons['SwitchPlayer'] = Button(self.ScreenSize[0] - self.UnitSize*3, self.ScreenSize[1] - self.UnitSize, self.UnitSize*3, self.UnitSize,text = "交换先手")
		self.board_area = Board_Area(self.UnitSize, self.BoardSize)
		self.message_area = Message_Area(0, self.ScreenSize[1]-self.UnitSize*2, self.ScreenSize[0], self.UnitSize)

	def restart_game(self):	
		self.draw_static()
		self.last_move_player = None

	def render_step(self, move):
		for event in pygame.event.get():
			if event.type == QUIT:
				exit()
		if self.last_move_player:
			self.draw_pieces(self.last_move_player[0], self.last_move_player[1], False)
		self.draw_pieces(move, self.board.current_player, True)
		self.last_move_player = move, self.board.current_player
		pygame.display.update()
		
	def move_2_loc(self, move):
		return move % self.BoardSize, move // self.BoardSize

	def loc_2_move(self, loc):
		return int(loc[0] + loc[1] * self.BoardSize)

	def get_input(self):
		while True:
			for event in pygame.event.get():
				if event.type == QUIT:
					return Output('quit',None)

				if event.type == MOUSEBUTTONDOWN: 
					if event.button == 1:
						mouse_pos = event.pos

						for name, button in self.buttons.items():
							if button.pressed(mouse_pos):
								return  Output(name, None)

						if self.board_area.rect.collidepoint(mouse_pos):
							x = (mouse_pos[0] - self.UnitSize)//self.UnitSize
							y = self.BoardSize - (mouse_pos[1] - self.UnitSize)//self.UnitSize - 1
							move = self.loc_2_move((x, y))
							if move in self.board.availables:
								return  Output('move',move)


	def draw_pieces(self, move, player, last_step=False):
		x, y = self.move_2_loc(move)
		pos = int(self.UnitSize * 1.5 + x * self.UnitSize), int(self.UnitSize * 1.5 + (self.BoardSize - y - 1) * self.UnitSize)
		color = [self.BLACK, self.WHITE][player-1]
		pygame.draw.circle(self.surface, color, pos, int(self.UnitSize * 0.45))
		if last_step:
			color = [self.WHITE, self.BLACK][player-1]
			start_p1 = pos[0] - self.UnitSize * 0.3, pos[1]
			end_p1 = pos[0] + self.UnitSize * 0.3, pos[1]
			pygame.draw.line(self.surface, color, start_p1, end_p1)
			start_p2 = pos[0], pos[1] - self.UnitSize * 0.3
			end_p2 = pos[0], pos[1] + self.UnitSize * 0.3
			pygame.draw.line(self.surface, color, start_p2, end_p2)

	def draw_static(self):
		self.surface.fill(self.BackGround)
		self.board_area.draw(self.surface, self.TextSize)
		for _ , button in self.buttons.items():
			button.draw(self.surface,self.TextSize)
		pygame.display.update()

	@staticmethod
	def draw_text(surface, text, position, text_height=25, font_color=(0, 0, 0), backgroud_color=None,
				   angle=0):
		font = pygame.font.Font('WenQuan.ttf',int(text_height))
		text = font.render(str(text), True, font_color, backgroud_color)
		text = pygame.transform.rotate(text, angle)
		text_rect = text.get_rect()
		text_rect.center = position
		surface.blit(text, text_rect)

	def play_human(self, start_player=1):
		self.board.reset_board(start_player)

		while True:
			if not self.game_end:
				print('current_player', self.board.current_player)
				text = "请玩家{x}落子".format(x=self.board.current_player)
				self.message_area.draw(self.surface,text,self.TextSize)

			user_input = self.get_input()

			if user_input.action == 'quit':
				break

			if user_input.action == 'RestartGame':
				self.game_end = False
				self.board.reset_board(start_player)
				self.restart_game()
				continue

			if user_input.action == 'SwitchPlayer':
				self.game_end = False
				start_player = start_player % 2 + 1
				self.board.reset_board(start_player)
				self.restart_game()
				continue

			if user_input.action == 'move' and not self.game_end:
				move = user_input.value
				self.render_step(move)
				self.board.do_move(move)
				self.game_end, winner = self.board.game_end()
				if self.game_end:
					if winner != -1:
						print("Game end. Winner is player", winner)
						text = "玩家{x}胜利".format(x=winner)
						self.message_area.draw(self.surface,text,self.TextSize)
					else:
						text =  "二位旗鼓相当！"
						self.message_area.draw(self.surface,text,self.TextSize)
			
		pygame.quit()

if __name__ == '__main__':
	board_size = 9
	n = 5
	start_player = 1
	game = Game(width=board_size, height=board_size, n_in_row=n)
	game.play_human(start_player)