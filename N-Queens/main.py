n = int(input())
if n >= 4:
    print(n)
    #board space
    board = []
    for i in range(n):
        row = []
        for j in range(n):
         row.append("*")
        board.append(row)

    #print board
    for row in board:
        print("".join(row))
else:
    print("invalid")

def queenPlacement(board, row):
   for col in range(n): #try colums in row
    safe = True #assume spot good
    for r in range(row): #check rows with queens there
        if board[r][col] == "Q": #check the same col as row
            safe = False #spot not good
        if abs(r - row) == abs(col - board[r].index("Q")):
            safe = False
    if safe:
       board[row][col] = "Q" #place queen
       if solve(row + 1):#place next queen
          return True
       board[row][col] = "*" #backtrack
    return false #no good place in row
queenPlacement(0)