from random import randrange
import sys

board = [['1', '2', '3'],
        ['4', '5', '6'],
        ['7', '8', '9']]

takenvalues = [5, 0]

def display_board(board):
    for i in range(4):
        print(('+-------' * 3) + '+')
        if i > 2: break
        print('|       |       |       |')
        print('|   ' + board[i][0] + '   |   ' + board[i][1] + '   |   ' + board[i][2] + '   |')
        print('|       |       |       |')

def enter_move(board):
    #The function accepts the board's current status, asks the user about their move, 
    # checks the input, and updates the board according to the user's decision.
    counter = 0
    while True:
        user = input('Enter Your Move')
        if int(user) not in range(10) or int(user) in takenvalues:
            print("Value entered is either not a number 1-9 or has already been taken by one of the players")
            continue
        if int(user) in [1, 2, 3]:
            rowind = 0
        elif int(user) in [4, 5, 6]:
            rowind = 1
        else:
            rowind = 2
        if int(user) in [1, 4, 7]:
            colind = 0
        elif int(user) in [2, 5, 8]:
            colind = 1
        else:
            colind = 2
        board[rowind][colind] = 'O'
        takenvalues.append(int(user))
        counter = counter + 1
        if counter > 0: break


def victory_for(board, sign):
    if board[0][0] == board[0][1] == board[0][2] or\
       board[1][0] == board[1][1] == board[1][2] or\
       board[2][0] == board[2][1] == board[2][2] or\
       board[0][0] == board[1][0] == board[2][0] or\
       board[0][1] == board[1][1] == board[2][1] or\
       board[0][2] == board[1][2] == board[2][2] or\
       board[0][0] == board[1][1] == board[2][2] or\
       board[0][2] == board[1][1] == board[2][0]:
        if sign == 'X':
            print('Computer Has Won!')
            sys.exit()
        else:
            print('Congrats! You Won!')
            sys.exit()

def draw_move(board):
    # The function draws the computer's move and updates the board.
    counteropp = 0
    while True:
        opponent = randrange(1, 10)
        if int(opponent) in takenvalues:
            continue
        if int(opponent) in [1, 2, 3]:
            rowindopp = 0
        elif int(opponent) in [4, 5, 6]:
            rowindopp = 1
        else:
            rowindopp = 2
        if int(opponent) in [1, 4, 7]:
            colindopp = 0
        elif int(opponent) in [2, 5, 8]:
            colindopp = 1
        else:
            colindopp = 2
        board[rowindopp][colindopp] = 'X'
        takenvalues.append(int(opponent))
        counteropp = counteropp + 1
        print('Computer has selected -')
        if counteropp > 0: break
    

board[1][1] = 'X'
display_board(board)

for i in range(4):
    enter_move(board)
    display_board(board)
    victory_for(board, 'O')
    draw_move(board)
    display_board(board)
    victory_for(board, 'X')




