import random

def parse_board(board_str):
    lines = board_str.strip().split('\n')
    grid = []
    for line in lines:
        if line.startswith('|') and line.endswith('|'):
            row = list(line[1:-1])
            grid.append(row)
    return grid

def find_positions(grid):
    head_a = None
    head_b = None
    length_a = 1
    length_b = 1
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
            elif cell == 'a':
                length_a += 1
            elif cell == 'b':
                length_b += 1
            elif cell == '*':
                foods.append((r, c))
                
    return head_a, head_b, foods, length_a, length_b

def is_safe(grid, r, c):
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    if r < 0 or r >= rows or c < 0 or c >= cols:
        return False
        
    cell = grid[r][c]
    if cell not in (' ', '*'):
        return False
        
    return True

from collections import deque

def bfs_distances(grid, start_r, start_c):
    if not is_safe(grid, start_r, start_c):
        return {}
        
    distances = {(start_r, start_c): 0}
    queue = deque([(start_r, start_c)])
    
    while queue:
        curr_r, curr_c = queue.popleft()
        curr_dist = distances[(curr_r, curr_c)]
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = curr_r + dr, curr_c + dc
            if is_safe(grid, nr, nc) and (nr, nc) not in distances:
                distances[(nr, nc)] = curr_dist + 1
                queue.append((nr, nc))
                
    return distances

def bfs_safe_area(grid, start_r, start_c, opponent_distances):
    if not is_safe(grid, start_r, start_c):
        return 0
        
    visited = {(start_r, start_c)}
    queue = deque([(start_r, start_c, 1)]) 
    area = 0
    
    while queue:
        curr_r, curr_c, my_dist = queue.popleft()
        
        opp_dist = opponent_distances.get((curr_r, curr_c), float('inf'))
        if opp_dist <= my_dist:
            continue
            
        area += 1
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = curr_r + dr, curr_c + dc
            if is_safe(grid, nr, nc) and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append((nr, nc, my_dist + 1))
                
    return area

def get_next_snake_move(board_str, side):

    grid = parse_board(board_str)
    if not grid:
        return 'up'
        
    head_a, head_b, foods, length_a, length_b = find_positions(grid)
    
    my_head = head_a if side == 'A' else head_b
    my_length = length_a if side == 'A' else length_b
    
    opp_head = head_b if side == 'A' else head_a
    
    if not my_head:
        return random.choice(['up', 'down', 'left', 'right'])
        
    r, c = my_head
    
    opp_distances = {}
    if opp_head:
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = opp_head[0] + dr, opp_head[1] + dc
            if is_safe(grid, nr, nc):
                sub_dists = bfs_distances(grid, nr, nc)
                for pos, dist in sub_dists.items():
                    actual_dist = dist + 1
                    if pos not in opp_distances or actual_dist < opp_distances[pos]:
                        opp_distances[pos] = actual_dist

    moves = {
        'up': (r - 1, c),
        'down': (r + 1, c),
        'left': (r, c - 1),
        'right': (r, c + 1)
    }
    
    safe_moves_data = {}
    
    for direction, (nr, nc) in moves.items():
        if is_safe(grid, nr, nc):

            if opp_head and abs(nr - opp_head[0]) + abs(nc - opp_head[1]) == 1:
                pass 

            area = bfs_safe_area(grid, nr, nc, opp_distances)
            
            my_dists = bfs_distances(grid, nr, nc)

            closest_food_dist = float('inf')
            for fr, fc in foods:
                if (fr, fc) in my_dists: 
                    if my_dists[(fr, fc)] < closest_food_dist:
                        closest_food_dist = my_dists[(fr, fc)]
            
            safe_moves_data[direction] = {
                'area': area,
                'food_dist': closest_food_dist
            }
            
    if not safe_moves_data:
        return random.choice(['up', 'down', 'left', 'right'])
        
    safe_threshold = my_length
    
    excellent_moves = [d for d, data in safe_moves_data.items() if data['area'] >= safe_threshold]
    
    if not excellent_moves:
        max_area = max(data['area'] for data in safe_moves_data.values())
        survival_moves = [d for d, data in safe_moves_data.items() if data['area'] == max_area]
        return random.choice(survival_moves)
        
    best_direction = None
    min_dist = float('inf')
    
    for direction in excellent_moves:
        data = safe_moves_data[direction]
        if data['food_dist'] < min_dist:
            min_dist = data['food_dist']
            best_direction = direction
            
    if best_direction: 
        return best_direction
        
    max_excellent_area = max(safe_moves_data[d]['area'] for d in excellent_moves) 
    fallback_moves = [d for d in excellent_moves if safe_moves_data[d]['area'] == max_excellent_area] 
    return random.choice(fallback_moves)
    
    return random.choice(fallback_moves)
