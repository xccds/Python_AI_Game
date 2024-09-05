boardSize = 3
board = ['.'] * boardSize * boardSize
currentPlayer = 'X'

print ("井字棋游戏开始 ")
print ("规则：三子连成线即胜利")
print ("X 先手, O 后手")

def print_board(board):
    print("\n")
    print("%s|%s|%s" % (board[0], board[1], board[2]))
    print("-+-+-")
    print("%s|%s|%s" % (board[3], board[4], board[5]))
    print("-+-+-")
    print("%s|%s|%s" % (board[6], board[7], board[8]))

# alternative solution
# def print_board(board):
#     print("\n")
#     print(f"{board[0]}|{board[1]}|{board[2]}")
#     print("-+-+-")
#     print(f"{board[3]}|{board[4]}|{board[5]}")
#     print("-+-+-")
#     print(f"{board[6]}|{board[7]}|{board[8]}")

def hasWon(currentBoard, player):
    winningSet = [player for _ in range(boardSize)]
	
    row1 = currentBoard[:3]
    row2 = currentBoard[3:6]
    row3 = currentBoard[6:]
    if winningSet in [row1,row2,row3]:
        return True 

    col1 = [currentBoard[0],currentBoard[3],currentBoard[6]]
    col2 = [currentBoard[1],currentBoard[4],currentBoard[7]]
    col3 = [currentBoard[2],currentBoard[5],currentBoard[8]]
    if winningSet in [col1,col2,col3]:
        return True 

    diag1 =[currentBoard[0],currentBoard[4],currentBoard[8] ]
    diag2 =[currentBoard[6],currentBoard[4],currentBoard[2] ]

    if winningSet in [diag1,diag2]:
        return True 
	
    return False

def getNextPlayer(currentPlayer):
	if currentPlayer == 'X':
		return 'O'
	return 'X'

def getPlayerMove(board, currentPlayer):
    isMoveValid = False
    while isMoveValid == False:
        print('')
        userMove = input(f'玩家 {currentPlayer} 输入棋盘坐标(坐标取值0,1,2):  X,Y?  ')
        userX, userY = [int(char) for char in  userMove.split(',')]
        userIndex = userX * boardSize + userY
        if board[userIndex] == '.':
            isMoveValid = True
	
    board[userIndex] = currentPlayer
    return board

def hasMovesLeft(board):
	return '.' in board

if __name__ == '__main__':
    print_board(board)
    while hasMovesLeft(board):
        board = getPlayerMove(board, currentPlayer)
        print_board(board)
        if hasWon(board, currentPlayer):
            print('玩家 ' + currentPlayer + ' 胜利!')
            break
        currentPlayer = getNextPlayer(currentPlayer)
