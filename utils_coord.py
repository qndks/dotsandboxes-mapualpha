def coord_to_idx(x, y, z):
    return (x * 6 + y) if z == 0 else (30 + x * 5 + y)

def idx_to_coord(idx):
    z = idx >= 30
    base = 6 - z
    i = idx - 30*z
    return [i // base, i % base, int(z)]

def get_box_edges(x, y):
    top    = coord_to_idx(x,   y,   0)
    bottom = coord_to_idx(x,   y+1, 0)
    left   = coord_to_idx(x,   y,   1)
    right  = coord_to_idx(x+1, y,   1)
    return [top, bottom, left, right]

def get_edge_squares(idx):
    x, y, z = idx_to_coord(idx)
    squares = []

    if z == 0:
        if y <= 4:
            squares.append((x, y))
        if y >= 1 and y <= 5:
            squares.append((x, y-1))
    else:
        if x <= 4:
            squares.append((x, y))
        if x >= 1 and x <= 5:
            squares.append((x-1, y))

    return squares
    
def apply_move(state_vec, square_owner, move_idx, player_id):
    state_vec[move_idx] = 1.0
    completed = 0

    for (bx, by) in get_edge_squares(move_idx):
        if square_owner[bx][by] != 0:
            continue
        edges = get_box_edges(bx, by)
        if all(state_vec[e] != 0 for e in edges):
            square_owner[bx][by] = player_id
            completed += 1

    return completed

def build_board_lines_from_state_vec(state_vec, xsize=5, ysize=5):
    board_lines = [[[0, 0] for _ in range(6)] for _ in range(6)]

    for idx, v in enumerate(state_vec):
        x, y, z = idx_to_coord(idx)
        if (z == 0 and x < xsize) or (z == 1 and y < ysize):
            board_lines[x][y][z] = 1 if v != 0 else 0

    return board_lines