import random

def parse_board(board_str):
    """
    Parses the board string into a 2D list.
    Removes the starting and ending '|' and splitting by newline.
    """
    # The board is separated by \n. Each line is surrounded by |...|
    lines = board_str.strip().split('\n')
    grid = []
    for line in lines:
        if line.startswith('|') and line.endswith('|'):
            # Remove the boundary pipes
            row = list(line[1:-1])
            grid.append(row)
    return grid

def find_positions(grid):
    """
    Finds the head of our snake, the opponent's snake, bodies, and foods.
    """
    head_a = None
    head_b = None
    foods = []

    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    for r in range(rows):
        for c in range(cols):
            cell = grid[r][c]
            if cell == 'A':
                head_a = (r, c)
            elif cell == 'B':
                head_b = (r, c)
            elif cell == '*':
                foods.append((r, c))

    return head_a, head_b, foods

def is_safe(grid, r, c):
    """
    Checks if a given coordinate is safe to move to (not out of bounds, not a body/head).
    """
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    if r < 0 or r >= rows or c < 0 or c >= cols:
        return False

    cell = grid[r][c]
    # ' ' is empty space, '*' is food. Everything else (A, B, a, b) is a hazard.
    if cell not in (' ', '*'):
        return False

    return True

def get_next_snake_move(board_str, side):
    """
    Returns the best direction ('up', 'down', 'left', 'right') for the snake.
    """
    grid = parse_board(board_str)
    if not grid:
        return 'up' # Fallback

    head_a, head_b, foods = find_positions(grid)

    my_head = head_a if side == 'A' else head_b
    if not my_head:
        # If head not found for some reason, return a default safe-ish fallback
        return random.choice(['up', 'down', 'left', 'right'])

    r, c = my_head

    # Possible moves and their resulting coordinates
    moves = {
        'up': (r - 1, c),
        'down': (r + 1, c),
        'left': (r, c - 1),
        'right': (r, c + 1)
    }

    # Filter safe moves
    safe_moves = []
    for direction, (nr, nc) in moves.items():
        if is_safe(grid, nr, nc):
            safe_moves.append(direction)

    if not safe_moves:
        # We are trapped, just return something
        return random.choice(['up', 'down', 'left', 'right'])

    # If there are foods, try to move towards the closest one
    if foods:
        best_direction = None
        min_distance = float('inf')

        for direction in safe_moves:
            nr, nc = moves[direction]
            for fr, fc in foods:
                # Manhattan distance
                dist = abs(nr - fr) + abs(nc - fc)
                if dist < min_distance:
                    min_distance = dist
                    best_direction = direction

        if best_direction:
            return best_direction

    # If no food or tie, just pick a safe move at random
    return random.choice(safe_moves)
