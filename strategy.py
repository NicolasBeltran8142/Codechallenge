import random

def parse_board(board_str):
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
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    # 1. Límites del mapa
    if r < 0 or r >= rows or c < 0 or c >= cols:
        return False
        
    cell = grid[r][c]
    # 2. Obstáculos
    if cell not in (' ', '*'):
        return False
        
    return True

def flood_fill(grid, r, c):
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    # Si la celda inicial no es segura, el área es 0
    if not is_safe(grid, r, c):
        return 0

    visited = set()
    queue = [(r, c)]
    visited.add((r, c))
    area = 0
    
    # Mientras haya casillas por revisar en nuestra cola
    while queue:
        curr_r, curr_c = queue.pop(0)
        area += 1
        
        # Revisamos los 4 vecinos de la casilla actual
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = curr_r + dr, curr_c + dc
            
            # Si el vecino no fue visitado aún y es un lugar seguro (vacío o comida)
            if (nr, nc) not in visited and is_safe(grid, nr, nc):
                visited.add((nr, nc))
                queue.append((nr, nc))
                
    return area

def get_next_snake_move(board_str, side):
    grid = parse_board(board_str)
    if not grid:
        return 'up'
        
    head_a, head_b, foods = find_positions(grid)
    
    # Identificamos cuál es nuestra cabeza dependiendo de qué lado nos asignó el servidor
    my_head = head_a if side == 'A' else head_b
    if not my_head:
        return random.choice(['up', 'down', 'left', 'right'])
        
    r, c = my_head
    
    # Direcciones posibles y cómo cambian nuestras coordenadas (fila, columna)
    moves = {
        'up': (r - 1, c),
        'down': (r + 1, c),
        'left': (r, c - 1),
        'right': (r, c + 1)
    }
    
    # Paso 1: Obtener movimientos que no sean chocar inmediatamente (Safe Moves)
    safe_moves = {}
    for direction, (nr, nc) in moves.items():
        if is_safe(grid, nr, nc):
            # Paso 2: Usar Flood Fill para ver qué tan grande es el espacio si vamos por allí
            area = flood_fill(grid, nr, nc)
            safe_moves[direction] = area
            
    if not safe_moves:
        # Estamos completamente atrapados, solo podemos elegir al azar y morir con honor
        return random.choice(['up', 'down', 'left', 'right'])
        
    # Paso 3: Filtrar movimientos que nos lleven a espacios muy cerrados.
    # Si un espacio tiene menos de, digamos, 15 casillas conectadas, es probablemente un callejón mortal.
    # Encontramos cuál es el área máxima a la que podemos acceder.
    max_area = max(safe_moves.values())
    
    # Solo consideramos movimientos que nos lleven a un área decente (evita callejones tontos)
    # Para no ser tan estrictos, pedimos que el área sea al menos el 80% del área más grande que encontramos.
    viable_moves = [dir for dir, area in safe_moves.items() if area >= max_area * 0.8]
    
    # Si de alguna forma todos son malos, volvemos a la lista completa
    if not viable_moves:
        viable_moves = list(safe_moves.keys())
        
    # Paso 4: De los movimientos viables (no suicidas y no callejones), buscar la comida
    if foods:
        best_direction = None
        min_distance = float('inf')
        
        for direction in viable_moves:
            nr, nc = moves[direction]
            for fr, fc in foods:
                # [TEORIA] Distancia de Manhattan
                # Como en el juego no podemos movernos en diagonal, la distancia real
                # entre dos puntos no es una línea recta. Es la suma de la distancia horizontal
                # y la distancia vertical. ¡Como contar cuadras en una ciudad (Manhattan)!
                dist = abs(nr - fr) + abs(nc - fc)
                if dist < min_distance:
                    min_distance = dist
                    best_direction = direction
                    
        if best_direction:
            return best_direction

    # Si no hay comida (o algo falló), elegimos uno de los movimientos viables al azar
    return random.choice(viable_moves)
