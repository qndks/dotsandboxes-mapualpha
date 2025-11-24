import random

def init():
    pass

def run(board_lines, xsize, ysize):
    legal_moves = []

    for x in range(xsize + 1):
        for y in range(ysize + 1):
            if x < xsize and board_lines[x][y][0] == 0:
                legal_moves.append((x, y, 0))
            if y < ysize and board_lines[x][y][1] == 0:
                legal_moves.append((x, y, 1))

    return random.choice(legal_moves)