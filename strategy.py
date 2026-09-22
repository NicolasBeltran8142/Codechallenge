import random

def parse_board(board_str):
    """
    [TEORIA] Representación del Tablero
    El servidor nos envía el tablero como un bloque de texto gigante. 
    Para una computadora es difícil analizar un solo texto largo, por lo que convertimos
    este texto en una "Grilla Bidimensional" o Matriz (una lista de listas).
    Imagina que es como una hoja cuadriculada. Cada fila es una lista, y cada celda
    tiene una coordenada (r, c) donde 'r' es la fila (row) y 'c' es la columna (col).
    """
    lines = board_str.strip().split('\n')
    grid = []
    for line in lines:
        # Solo procesamos las líneas que empiezan y terminan con '|' (los bordes)
        if line.startswith('|') and line.endswith('|'):
            # Quitamos los '|' de los extremos para quedarnos solo con el contenido
            row = list(line[1:-1])
            grid.append(row)
    return grid

def find_positions(grid):
    """
    [TEORIA] Escaneo de la Grilla (Actualizado v4)
    Anotamos las coordenadas de:
    - 'A', 'a', 'B', 'b': Serpientes
    - '1'-'9': Comidas numéricas
    - 'x': Power-ups (multiplicadores)
    Devuelve las cabezas, los power-ups, todos los dígitos encontrados con su valor, y las longitudes.
    """
    head_a = None
    head_b = None
    length_a = 1
    length_b = 1
    powerups = []
    digits = {} # {(r, c): int_value}
    
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
            elif cell in ('x', 'X'):
                powerups.append((r, c))
            elif cell.isdigit():
                digits[(r, c)] = int(cell)
                
    return head_a, head_b, powerups, digits, length_a, length_b

def get_target_digit(digits_dict):
    """
    [TEORIA] Matemática Modular para la Comida Cíclica
    Si tenemos 5 números consecutivos cíclicos (ej. 8, 9, 1, 2, 3), el "primero"
    (el que hay que comer) siempre es el que está a la derecha del hueco o "salto" más grande
    cuando los ordenamos de menor a mayor.
    En el ejemplo ordenado: 1, 2, 3, 8, 9
    Saltos: 2-1=1, 3-2=1, 8-3=5 (¡Salto grande!), 9-8=1, y 1-9 (cíclico) = (1-9)%9 = 1
    El salto más grande es del 3 al 8. Por ende, la secuencia termina en 3 y empieza en 8.
    """
    if not digits_dict:
        return None

    vals = sorted(list(digits_dict.values()))
    if len(vals) == 1:
        return vals[0]

    max_gap = 0
    target_val = vals[0]

    for i in range(len(vals)):
        # Calculamos la distancia al siguiente número (cíclica)
        # Asumimos que los dígitos válidos son del 1 al 9, módulo 9 (donde 0 equivale a 9)
        v1 = vals[i]
        v2 = vals[(i + 1) % len(vals)]

        # Distancia en el ciclo de 1 a 9 avanzando hacia adelante
        gap = (v2 - v1) % 9
        if gap == 0:
            pass

        if gap > max_gap:
            max_gap = gap
            target_val = v2

    return target_val


def is_safe(grid, r, c, target_digit=None):
    """
    [TEORIA] Validación de Movimiento
    Debemos verificar:
    1. Límites del mapa.
    2. Obstáculos. ' ' y 'x' son seguros siempre.
    3. Si hay un dígito, SOLO es seguro si es exactamente igual a target_digit.
       Cualquier otro número es un veneno (-500 pts) y actuará como un muro.
    """
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    if r < 0 or r >= rows or c < 0 or c >= cols:
        return False
        
    cell = grid[r][c]
    if cell in (' ', 'x', 'X'):
        return True

    if cell.isdigit():
        if target_digit is not None and int(cell) == target_digit:
            return True
        return False # Número equivocado = MUERTE

    # 'A', 'B', 'a', 'b', etc
    return False

from collections import deque

def bfs_distances(grid, start_r, start_c, target_digit=None):
    """
    [TEORIA] Búsqueda en Anchura (BFS - Breadth-First Search)
    Calcula la distancia real (en cantidad de pasos) desde (start_r, start_c)
    hasta todas las casillas alcanzables en el mapa, esquivando obstáculos.
    Devuelve un diccionario {(r, c): distancia}.
    """
    if not is_safe(grid, start_r, start_c, target_digit):
        return {}
        
    distances = {(start_r, start_c): 0}
    queue = deque([(start_r, start_c)])
    
    while queue:
        curr_r, curr_c = queue.popleft()
        curr_dist = distances[(curr_r, curr_c)]
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = curr_r + dr, curr_c + dc
            if is_safe(grid, nr, nc, target_digit) and (nr, nc) not in distances:
                distances[(nr, nc)] = curr_dist + 1
                queue.append((nr, nc))
                
    return distances

def bfs_safe_area(grid, start_r, start_c, opponent_distances, target_digit=None):
    """
    [TEORIA] Control de Territorio y Área Segura
    Calcula cuántas casillas de espacio libre real tenemos si empezamos a caminar 
    desde (start_r, start_c), pero ¡OJO! descontando las casillas a las que el 
    oponente puede llegar antes o al mismo tiempo que nosotros.
    Esto evita que nos encierren.
    """
    if not is_safe(grid, start_r, start_c, target_digit):
        return 0
        
    visited = {(start_r, start_c)}
    queue = deque([(start_r, start_c, 1)]) # (fila, columna, nuestra_distancia_pasos)
    area = 0
    
    while queue:
        curr_r, curr_c, my_dist = queue.popleft()
        
        # Verificamos si esta casilla está en peligro por el oponente
        opp_dist = opponent_distances.get((curr_r, curr_c), float('inf'))
        # Si el oponente llega antes o en el mismo turno, descartamos seguir por acá (territorio enemigo)
        if opp_dist <= my_dist:
            continue
            
        area += 1
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = curr_r + dr, curr_c + dc
            if is_safe(grid, nr, nc, target_digit) and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append((nr, nc, my_dist + 1))
                
    return area

def get_next_snake_move(board_str, side):
    grid = parse_board(board_str)
    if not grid:
        return 'up'
        
    head_a, head_b, powerups, digits_dict, length_a, length_b = find_positions(grid)
    target_digit = get_target_digit(digits_dict)
    
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
            if is_safe(grid, nr, nc, target_digit):
                sub_dists = bfs_distances(grid, nr, nc, target_digit)
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
    
    target_digit_coords = [coord for coord, val in digits_dict.items() if val == target_digit]

    for direction, (nr, nc) in moves.items():
        if is_safe(grid, nr, nc, target_digit):
            if opp_head and abs(nr - opp_head[0]) + abs(nc - opp_head[1]) == 1:
                pass

            area = bfs_safe_area(grid, nr, nc, opp_distances, target_digit)
            my_dists = bfs_distances(grid, nr, nc, target_digit)
            
            closest_powerup_dist = float('inf')
            for pu in powerups:
                if pu in my_dists:
                    if my_dists[pu] < closest_powerup_dist:
                        closest_powerup_dist = my_dists[pu]

            closest_target_dist = float('inf')
            for t_coord in target_digit_coords:
                if t_coord in my_dists:
                    if my_dists[t_coord] < closest_target_dist:
                        closest_target_dist = my_dists[t_coord]
            
            safe_moves_data[direction] = {
                'area': area,
                'target_dist': closest_target_dist,
                'powerup_dist': closest_powerup_dist
            }
            
    if not safe_moves_data:
        return random.choice(['up', 'down', 'left', 'right'])
        
    safe_threshold = my_length
    excellent_moves = [d for d, data in safe_moves_data.items() if data['area'] >= safe_threshold]
    
    if not excellent_moves:
        max_area = max(data['area'] for data in safe_moves_data.values())
        survival_moves = [d for d, data in safe_moves_data.items() if data['area'] == max_area]
        return random.choice(survival_moves)
        
    # De los movimientos excelentes, buscamos si alguna dirección nos lleva a una 'x'
    best_direction = None
    min_powerup_dist = float('inf')
    
    for direction in excellent_moves:
        data = safe_moves_data[direction]
        if data['powerup_dist'] < min_powerup_dist:
            min_powerup_dist = data['powerup_dist']
            best_direction = direction

    if best_direction and min_powerup_dist != float('inf'):
        return best_direction

    # Si no hay 'x' alcanzable, buscamos el dígito correcto
    min_target_dist = float('inf')
    best_direction = None
    for direction in excellent_moves:
        data = safe_moves_data[direction]
        if data['target_dist'] < min_target_dist:
            min_target_dist = data['target_dist']
            best_direction = direction
            
    if best_direction and min_target_dist != float('inf'):
        return best_direction
        
    max_excellent_area = max(safe_moves_data[d]['area'] for d in excellent_moves)
    fallback_moves = [d for d in excellent_moves if safe_moves_data[d]['area'] == max_excellent_area]
    
    return random.choice(fallback_moves)