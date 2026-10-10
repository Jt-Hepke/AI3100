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

