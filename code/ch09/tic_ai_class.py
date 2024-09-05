from  copy import deepcopy  
import random

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
		if isinstance(loc, int):
			move = loc 
		else:
			move = self.locToMove(loc)
		if self.pieces[move] == '.':
			return True
		return False
	
	def setMove(self,loc,player):
		if isinstance(loc, int):
			self.pieces[loc] = player
		else:
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
	
# 基于蒙特卡洛构建的井字棋AI
class AI_tic:
	
	def __init__(self,n_sim, size):
		self.n_sim = n_sim
		self.size = size

	def getNextMoves(self,currentBoard, player):
		nextMoves = []
		for i , _ in enumerate(currentBoard.pieces):
			if currentBoard.isMoveValid(i):
				boardCopy = deepcopy(currentBoard)
				boardCopy.setMove(i, player)
				nextMoves.append(boardCopy)
		return nextMoves

	def oneSimulation(self,currentBoard,currentPlayer):
		simulationMoves = []
		player = currentPlayer
		nextMoves = self.getNextMoves(currentBoard, player)
		
		score = self.size * self.size
		
		while nextMoves != []:
			roll = random.randint(1, len(nextMoves)) - 1
			nextBoard = nextMoves[roll]
			simulationMoves.append(nextBoard)
			if nextBoard.hasWon(player):
				break
			score -= 1
			player = Game.getNextPlayer(player)
			nextMoves = self.getNextMoves(nextBoard, player)
		firstMove = simulationMoves[0]
		if player != currentPlayer and nextBoard.hasWon(player):
			score *= -1
		return firstMove, score
	 
	def getBestNextMove(self,currentBoard, currentPlayer):
		evaluations = {}
		for _ in range(self.n_sim):
			boardCopy = deepcopy(currentBoard)
			firstMove, score = self.oneSimulation(boardCopy,currentPlayer)
			firstMovePos = tuple(firstMove.pieces)
			if firstMovePos in evaluations:
				evaluations[firstMovePos] += score
			else:
				evaluations[firstMovePos] = score
		bestMove = max(evaluations, key=evaluations.get)
		return list(bestMove)
		

class Game:
	userPlayer = 'O'

	def __init__(self,boardSize,startPlayer): 
		self.currentPlayer = startPlayer
		self.board = Board(boardSize)
		self.AI = AI_tic(600,boardSize)
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

	# 用于人类和AI对战
	def play(self):
		self.board.show()
		while self.board.hasMovesLeft():
			if self.currentPlayer == self.userPlayer:
				self.getPlayerMove()
			else:
				self.board.pieces = self.AI.getBestNextMove(self.board,self.currentPlayer)
			self.board.show()
			if self.board.hasWon(self.currentPlayer):
				print('\n 玩家 ' + self.currentPlayer + ' 胜利!')
				break
			self.currentPlayer = self.getNextPlayer(self.currentPlayer)

	# 用于AI之间对战
	def AIvsAI(self):
		self.board.show()
		while self.board.hasMovesLeft():
			self.board.pieces  = self.AI.getBestNextMove(self.board,self.currentPlayer)
			self.board.show()
			if self.board.hasWon(self.currentPlayer):
				print('\n 玩家 ' + self.currentPlayer + ' 胜利!')
				break
			self.currentPlayer = self.getNextPlayer(self.currentPlayer)

	@staticmethod
	def replacePieces(inputList, player):
		outputList = []
		for x in inputList:
			if x == '.':
				y = '0'
			elif x == player:
				y = '1'
			else:
				y = '-1'
			outputList.append(y)
		return outputList 

	# 用于AI之间对战，并记录下落子的位置
	def AIvsAI_file(self,file):
		while self.board.hasMovesLeft():
			PiecesBefore = self.replacePieces(self.board.pieces,self.currentPlayer)
			boardSet = set([str(i)+x for i, x in enumerate(self.board.pieces)])
			self.board.pieces  = self.AI.getBestNextMove(self.board,self.currentPlayer)
			boardSetPlay = set([str(i)+x for i, x in enumerate(self.board.pieces)])
			move =  list(boardSetPlay - boardSet)[0][0]
			file.write(','.join(PiecesBefore))
			file.write(','+move+'\n')
			self.currentPlayer = self.getNextPlayer(self.currentPlayer)

if __name__ == '__main__':

	game = Game(boardSize=3,startPlayer='X')
	# 实现两个AI之间的对战
	#game.AIvsAI()
	# 如果需要人工和AI之间的对战，使用如下代码
	game.play()
	


# 如果需要保存AI之间对战信息，使用如下代码
# if __name__ == '__main__':

# 	with open(r'tic_record.txt', 'w') as file:
# 		for i in range(500):
# 			game = Game(boardSize=3,startPlayer='X')
# 			game.AIvsAI_file(file)
# 			print("-----"+"epoch"+str(i)+"-----")
# 		print("Done")
