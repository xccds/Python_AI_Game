class Board:

	def __init__(self, size):
		self.size = size
		self.pieces = ['.'] * size * size
	
	def show(self):
		print("\n")
		print("%s|%s|%s" % (self.pieces[0], self.pieces[1], self.pieces[2]))
		print("-+-+-")
		print("%s|%s|%s" % (self.pieces[3], self.pieces[4], self.pieces[5]))
		print("-+-+-")
		print("%s|%s|%s" % (self.pieces[6], self.pieces[7], self.pieces[8]))

	def hasMovesLeft(self):
		return '.' in self.pieces
	
	# def moveToLoc(self, move):
	# 	return move // self.size, move % self.size 

	def locToMove(self, loc):
		return int(loc[0] * self.size + loc[1])

	def isMoveValid(self,loc):
		move = self.locToMove(loc)
		if self.pieces[move] == '.':
			return True
		return False
	
	def setMove(self,loc,player):
		move = self.locToMove(loc)
		self.pieces[move] = player

	def hasWon(self,player):
		winningSet = [player for _ in range(self.size)]

		row1 = self.pieces[:3]
		row2 = self.pieces[3:6]
		row3 = self.pieces[6:]
		if winningSet in [row1,row2,row3]:
			return True 

		col1 = [self.pieces[0],self.pieces[3],self.pieces[6]]
		col2 = [self.pieces[1],self.pieces[4],self.pieces[7]]
		col3 = [self.pieces[2],self.pieces[5],self.pieces[8]]
		if winningSet in [col1,col2,col3]:
			return True 

		diag1 =[self.pieces[0],self.pieces[4],self.pieces[8] ]
		diag2 =[self.pieces[6],self.pieces[4],self.pieces[2] ]

		if winningSet in [diag1,diag2]:
			return True 
		
		return False

class Game:

	def __init__(self,boardSize,startPlayer): 
		self.currentPlayer = startPlayer
		self.board = Board(boardSize)
		print ("井字棋游戏开始 ")
		print ("规则：三子连成线即胜利")
		print ("X 先手, O 后手")

	@staticmethod
	def getNextPlayer(currentPlayer):
		if currentPlayer == 'X':
			return 'O'
		else :
			return 'X'  

	def getPlayerMove(self):
		while(True):
			userMove = input(f'\n 玩家 {self.currentPlayer} 输入棋盘坐标(坐标取值0,1,2):  X,Y?  ')
			userMoveLoc = [int(char) for char in  userMove.split(',')]
			if self.board.isMoveValid(userMoveLoc):
				self.board.setMove(userMoveLoc,self.currentPlayer)
				break

	def play(self):
		self.board.show()
		while self.board.hasMovesLeft():
			self.getPlayerMove()
			self.board.show()
			if self.board.hasWon(self.currentPlayer):
				print('\n 玩家 ' + self.currentPlayer + ' 胜利!')
				break
			self.currentPlayer = self.getNextPlayer(self.currentPlayer)


if __name__ == '__main__':
	
	game = Game(boardSize=3,startPlayer='X')
	game.play()
