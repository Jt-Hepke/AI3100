#JT Hepke jh639423@ohio.edu
#N Queens AI3100 Python


def queenPlacement(board, row): #places queens on given row
   n = len(board) #size of board

   #if every row has a queen solution had to been found for our setup of code
   if row == n:
      return True

   for col in range(n):  # try each column of the current row
      safe = True #assume spot safe

      # check same column and diagonals against earlier rows
      for r in range(row): 
         for c in range(n):
            if board[r][c] == "Q":
               if c == col or abs(r - row) == abs(c - col):
                  safe = False #spot not good
                  break
         if not safe: #stop checking rows
            break

      if safe:
         board[row][col] = "Q" #place queen in this space
         if queenPlacement(board, row + 1): #then push to next row
            return True #only if all queens can be placed
         board[row][col] = "*" #remove the queen if choice doesn't work

   return False  # no valid column for this row

n = int(input())
if n >= 4:
    #print(n)
    #board space
    board = []
    for i in range(n): #fill each row 
        board.append(["*"] * n)

    #print board
    if queenPlacement(board, 0): #start at row 0
       for row in board:
          print(" ".join(row))
else:
    print("no solution") #smaller then 4

